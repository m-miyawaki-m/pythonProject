import xml.etree.ElementTree as ET
import re
import sqlparse

def parse_sql(sql, sql_definitions=None):
    """
    SQL文を解析してテーブル名、カラム名、条件式、条件の出典を抽出する。
    """
    tables = {}
    alias_map = {}

    # SQL 文の展開
    sql = expand_sql_includes(sql, sql_definitions)

    # SQL 文の解析
    parsed = sqlparse.parse(sql)
    for stmt in parsed:
        tokens = sqlparse.sql.TokenList(stmt.tokens)
        process_from_and_join(tokens, tables, alias_map)
        select_columns = process_select_clause(tokens, alias_map, tables)
        process_where_clause(tokens, alias_map, tables)

        # SELECT句やWHERE句で未特定のカラムを処理
        assign_columns_to_tables(select_columns, tables, alias_map)  # alias_map を渡す

    return tables


def expand_sql_includes(sql, sql_definitions):
    """
    <sql> タグを展開する。
    """
    if sql_definitions:
        for key, value in sql_definitions.items():
            sql = sql.replace(f"<include refid=\"{key}\" />", value)
    return sql


def process_from_and_join(tokens, tables, alias_map):
    """
    FROM句とJOIN句を解析し、テーブルとエイリアスを抽出する。
    """
    from_found = False
    join_found = False

    for token in tokens:
        if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
            from_found = True
            continue
        elif token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'JOIN':
            join_found = True
            continue

        if from_found or join_found:
            if isinstance(token, sqlparse.sql.Identifier):  # テーブル名単体
                table_name = token.get_real_name()
                alias = token.get_alias()
                tables[table_name] = {"columns": [], "parameters": [], "condition": "", "source": ""}
                if alias:
                    alias_map[alias] = table_name
                else:
                    alias_map[table_name] = table_name  # エイリアスがない場合、テーブル名をキーにする
            elif isinstance(token, sqlparse.sql.IdentifierList):  # 複数のテーブル
                for identifier in token.get_identifiers():
                    table_name = identifier.get_real_name()
                    alias = identifier.get_alias()
                    tables[table_name] = {"columns": [], "parameters": [], "condition": "", "source": ""}
                    if alias:
                        alias_map[alias] = table_name
                    else:
                        alias_map[table_name] = table_name
            from_found = join_found = False


def process_select_clause(tokens, alias_map, tables):
    """
    SELECT句を解析し、カラム情報を抽出する。
    """
    select_columns = []

    for token in tokens:
        if token.ttype is sqlparse.tokens.DML and token.value.upper() == "SELECT":
            for next_token in tokens.tokens[tokens.token_index(token) + 1:]:
                if next_token.ttype is sqlparse.tokens.Keyword and next_token.value.upper() == "FROM":
                    break
                if next_token.ttype is sqlparse.tokens.Punctuation:
                    continue
                if isinstance(next_token, sqlparse.sql.IdentifierList):  # 複数カラム
                    for identifier in next_token.get_identifiers():
                        real_name = identifier.get_real_name()
                        alias = extract_alias(identifier)  # エイリアスを抽出
                        select_columns.append((alias, real_name))
                elif isinstance(next_token, sqlparse.sql.Identifier):  # 単一カラム
                    real_name = next_token.get_real_name()
                    alias = extract_alias(next_token)  # エイリアスを抽出
                    select_columns.append((alias, real_name))
                elif isinstance(next_token, sqlparse.sql.Function):  # 集約関数（例: NVL, MAX）
                    func_name = next_token.get_name()
                    arguments = []
                    for arg_token in next_token.tokens:
                        if isinstance(arg_token, sqlparse.sql.Identifier):
                            real_name = arg_token.get_real_name()
                            alias = extract_alias(arg_token)  # エイリアスを抽出
                            arguments.append(f"{alias}.{real_name}" if alias else real_name)
                        elif isinstance(arg_token, sqlparse.sql.Token) and arg_token.ttype is sqlparse.tokens.Name:
                            arguments.append(arg_token.value)
                    if func_name:
                        select_columns.append((None, f"{func_name}({', '.join(arguments)})"))

    return select_columns


def extract_alias(identifier):
    """
    sqlparse.sql.Identifier からエイリアスを抽出する。
    """
    # "u.id" のような形式の場合
    if "." in identifier.value:
        return identifier.value.split(".")[0]
    # エイリアスが含まれていない場合
    return None


def process_where_clause(tokens, alias_map, tables):
    """
    WHERE句を解析し、条件式とパラメータを抽出する。
    """
    for token in tokens:
        if token.value.upper() == "WHERE":
            # WHERE句全体を文字列化
            condition = "".join(str(t) for t in tokens)
            # #{param} または ${param} のパラメータを抽出
            parameters = re.findall(r"[#|$]{\w+}", condition)
            # エイリアス.カラム形式を抽出
            columns_in_where = re.findall(r"(\w+)\.(\w+)", condition)

            for alias, column in columns_in_where:
                if alias in alias_map:  # エイリアスを解決
                    actual_table = alias_map[alias]
                    if actual_table not in tables:
                        tables[actual_table] = {"columns": [], "parameters": [], "condition": "", "source": ""}
                    tables[actual_table]["columns"].append(column)
                    # 条件式を記録（既存条件に追記）
                    if tables[actual_table]["condition"]:
                        tables[actual_table]["condition"] += f" AND {condition}"
                    else:
                        tables[actual_table]["condition"] = condition

            # テーブルにパラメータを追加
            for table_name in tables:
                tables[table_name]["parameters"].extend(parameters)


def assign_columns_to_tables(select_columns, tables, alias_map):
    """
    SELECT句やWHERE句で特定されていないカラムをテーブルに割り当てる。
    """
    for alias, column in select_columns:
        if alias and alias in alias_map:  # エイリアスがある場合
            actual_table = alias_map[alias]
            if actual_table not in tables:
                tables[actual_table] = {"columns": [], "parameters": [], "condition": "", "source": ""}
            tables[actual_table]["columns"].append(column)
        elif len(tables) == 1:  # テーブルが1つしかない場合、それに割り当てる
            table_name = list(tables.keys())[0]
            tables[table_name]["columns"].append(column)
        else:  # 不明なテーブルの場合
            if "unknown_table" not in tables:
                tables["unknown_table"] = {"columns": [], "parameters": [], "condition": "", "source": ""}
            tables["unknown_table"]["columns"].append(column)


def process_insert_clause(tokens, tables):
    """
    INSERT文を解析し、テーブル名とカラム名を抽出する。
    """
    for token in tokens:
        if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == "INSERT":
            table_token = tokens.token_next(tokens.token_index(token), skip_ws=True)
            if isinstance(table_token, sqlparse.sql.Identifier):
                table_name = table_token.get_real_name()
                tables[table_name] = {"columns": [], "parameters": [], "condition": "", "source": ""}
            # カラム名の抽出
            column_list_token = tokens.token_next(tokens.token_index(token) + 1, skip_ws=True)
            if isinstance(column_list_token, sqlparse.sql.Parenthesis):
                columns = [col.get_real_name() for col in column_list_token.get_identifiers()]
                tables[table_name]["columns"].extend(columns)


def parse_mybatis_xml(file_path):
    """
    MyBatisのXMLファイルを解析する。
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    sql_definitions = {}
    for sql in root.findall(".//sql"):
        sql_id = sql.attrib.get("id")
        if sql_id:
            sql_definitions[sql_id] = "".join(sql.itertext()).strip()

    tables_by_tag = {"select": {}, "insert": {}, "delete": {}, "update": {}, "sql": sql_definitions}

    for tag_name in ["select", "insert", "delete", "update"]:
        for tag in root.findall(f".//{tag_name}"):
            tag_id = tag.attrib.get("id", "")
            sql = "".join(tag.itertext()).strip()
            parsed_data = parse_sql(sql, sql_definitions)
            for table, data in parsed_data.items():
                data["source"] = sql_definitions.get(tag_id, "")  # 出典を追跡
            tables_by_tag[tag_name][tag_id] = parsed_data

    return tables_by_tag
