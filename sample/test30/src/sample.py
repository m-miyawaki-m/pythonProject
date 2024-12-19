import sqlglot
from sqlglot import parse_one, exp
import json
import sys
import os

def extract_tables_aliases(tree):
    """
    FROM句やJOIN句からテーブル名とエイリアスを抽出します。
    戻り値は {エイリアスまたはテーブル名: テーブル名} の辞書です。
    """
    tables = {}
    for table in tree.find_all(exp.Table):
        table_name = table.name
        alias = table.alias_or_name
        tables[alias] = table_name
    return tables

def extract_columns_with_table(tree, tables):
    """
    SELECT句からカラムとそれが属するテーブルを抽出します。
    INSERT, UPDATE, DELETE 文の場合も関連するカラムを抽出します。
    戻り値は {テーブル名: [カラム名, ...], ...} の辞書です。
    """
    columns = {}
    # SELECT文の場合
    for column in tree.find_all(exp.Column):
        table_alias = column.table
        column_name = column.name
        if table_alias:
            table_name = tables.get(table_alias, 'UNKNOWN')
            columns.setdefault(table_name, set()).add(column_name)
        else:
            # エイリアスが指定されていない場合、UNKNOWNに分類
            columns.setdefault('UNKNOWN', set()).add(column_name)
    
    # INSERT文の場合
    if isinstance(tree, exp.Insert):
        table_name = tree.this.this
        for column in tree.columns or []:
            columns.setdefault(table_name, set()).add(column.name)
    
    # UPDATE文の場合
    if isinstance(tree, exp.Update):
        table_name = tree.this.name
        for set_expr in tree.find_all(exp.Set):
            column = set_expr.this.name
            columns.setdefault(table_name, set()).add(column)
    
    # DELETE文の場合
    # DELETE文では通常、直接的なカラム指定は少ないですが、WHERE句にカラムが含まれる場合があります
    # 必要に応じてWHERE句からカラムを抽出するロジックを追加できます
    
    return columns

def extract_dml(tree):
    """
    DMLの種類を抽出します（SELECT、INSERT、UPDATE、DELETE）。
    """
    if isinstance(tree, exp.Select):
        return 'SELECT'
    elif isinstance(tree, exp.Insert):
        return 'INSERT'
    elif isinstance(tree, exp.Update):
        return 'UPDATE'
    elif isinstance(tree, exp.Delete):
        return 'DELETE'
    else:
        return 'UNKNOWN'

def parse_sql(sql, dialect='default'):
    """
    単一のSQL文を解析し、DML、テーブル、カラムを抽出します。
    """
    try:
        tree = parse_one(sql, read=dialect)
    except sqlglot.errors.ParseError as e:
        print(f"ParseError: {e}")
        return None
    
    dml = extract_dml(tree)
    tables = extract_tables_aliases(tree)
    columns = extract_columns_with_table(tree, tables)
    
    # サブクエリの解析
    for subquery in tree.find_all(exp.Subquery):
        sub_tables = extract_tables_aliases(subquery)
        sub_columns = extract_columns_with_table(subquery, sub_tables)
        # テーブルとカラムを統合
        tables.update(sub_tables)
        for table, cols in sub_columns.items():
            columns.setdefault(table, set()).update(cols)
    
    # 結果を整理
    tables_list = list(set(tables.values()))  # 重複を排除
    columns_dict = {table: sorted(cols) for table, cols in columns.items()}
    
    return {
        'DML': dml,
        'Tables': tables_list,
        'Columns': columns_dict
    }

def read_sql_file(file_path):
    """
    SQLファイルを読み込み、セミコロンで分割してSQL文のリストを返します。
    コメント行（-- で始まる行）は無視します。
    """
    if not os.path.isfile(file_path):
        print(f"Error: ファイル '{file_path}' が存在しません。")
        sys.exit(1)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # コメントを削除
    lines = content.splitlines()
    lines = [line for line in lines if not line.strip().startswith('--')]
    content = '\n'.join(lines)
    
    # セミコロンで分割
    statements = sqlglot.parse_split(content, read='default')
    return statements

def main(sql_file_path):
    sql_statements = read_sql_file(sql_file_path)
    results = []
    
    for idx, sql in enumerate(sql_statements, 1):
        sql = sql.strip()
        if not sql:
            continue
        print(f"\n--- SQL Statement {idx} ---")
        print(sql)
        parsed = parse_sql(sql)
        if parsed:
            print("\nParsed Information:")
            print(f"DML: {parsed['DML']}")
            print(f"Tables: {parsed['Tables']}")
            print("Columns:")
            for table, cols in parsed['Columns'].items():
                print(f"  {table}: {cols}")
            results.append({
                'SQL': sql,
                'DML': parsed['DML'],
                'Tables': parsed['Tables'],
                'Columns': parsed['Columns']
            })
        else:
            print("Failed to parse the SQL statement.")
    
    # 必要に応じてJSON形式で保存
    # with open('parsed_results.json', 'w', encoding='utf-8') as f:
    #     json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_sql_file.py <path_to_sql_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    main(sql_file)
