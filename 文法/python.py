import os
import xml.etree.ElementTree as ET
import json
import csv
import re
import sqlparse

def parse_sql(sql, sql_definitions=None):
    """
    SQL文を解析してテーブル名、カラム名、副問合せ、WHERE句のパラメータを抽出する。
    sql_definitions: <sql>タグで定義された共通SQL文（辞書形式）
    """
    tables = {}
    if sql_definitions:
        # <sql> タグの内容を展開
        for key, value in sql_definitions.items():
            sql = sql.replace(f"<include refid=\"{key}\" />", value)

    parsed = sqlparse.parse(sql)
    for stmt in parsed:
        tokens = sqlparse.sql.TokenList(stmt.tokens)

        # 初期化
        from_found = False
        table_name = None

        for token in tokens:
            # FROM句解析
            if from_found and token.ttype is None:
                table_name = token.get_real_name()
                alias = token.get_alias()
                if table_name:
                    if alias:
                        tables[alias] = {"columns": [], "parameters": []}
                    else:
                        tables[table_name] = {"columns": [], "parameters": []}
                from_found = False
            
            if token.value.upper() == "FROM":
                from_found = True

            # WHERE句の解析
            if token.value.upper() == "WHERE":
                condition = "".join(str(t) for t in tokens)
                parameters = re.findall(r"[#|$]{\w+}", condition)  # #{param} または ${param}
                columns_in_where = re.findall(r"([a-zA-Z0-9_]+)\s*=", condition)
                if table_name:
                    tables[table_name]["columns"].extend(columns_in_where)
                    tables[table_name]["parameters"].extend(parameters)

    return tables

def parse_mybatis_xml(file_path):
    """
    MyBatisのXMLファイルを解析し、SQL文を抽出して解析する。
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # <sql>タグを収集
    sql_definitions = {}
    for sql in root.findall(".//sql"):
        sql_id = sql.attrib.get("id")
        if sql_id:
            sql_definitions[sql_id] = "".join(sql.itertext()).strip()

    tables_by_tag = {
        "select": {},
        "resultMap": {},
        "sql": sql_definitions  # sql定義をそのまま保持
    }

    # <select>タグの解析
    for select in root.findall(".//select"):
        sql = "".join(select.itertext()).strip()
        sql_tables = parse_sql(sql, sql_definitions)
        tables_by_tag["select"].update(sql_tables)
    
    # <resultMap>タグの解析
    for resultMap in root.findall(".//resultMap"):
        for result in resultMap.findall(".//result"):
            column = result.attrib.get('column')
            table_name = "unknown_table"  # 必要ならテーブル名を推測
            if table_name not in tables_by_tag["resultMap"]:
                tables_by_tag["resultMap"][table_name] = {"columns": [], "parameters": []}
            tables_by_tag["resultMap"][table_name]["columns"].append(column)
    
    return tables_by_tag

def save_to_json(data, output_path):
    """
    辞書をJSON形式で保存する。
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_to_csv(data, output_path):
    """
    辞書をCSV形式で保存する。
    """
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # ヘッダー行の書き込み
        writer.writerow(["ファイル名", "タグ", "テーブル名", "カラム名", "パラメータ名"])
        
        # データの展開と書き込み
        for file_name, tags in data.items():
            for tag, tables in tags.items():
                if tag == "sql":  # <sql>タグは特別な処理を行う
                    for sql_id, sql_content in tables.items():
                        writer.writerow([file_name, "sql", sql_id, sql_content, ""])
                else:
                    for table_name, details in tables.items():
                        for column in details["columns"]:
                            writer.writerow([file_name, tag, table_name, column, ""])
                        for param in details["parameters"]:
                            writer.writerow([file_name, tag, table_name, "", param])

def main():
    input_dir = "./mybatis_xml"  # XMLファイルのディレクトリ
    json_output_file = "./tables_columns.json"
    csv_output_file = "./tables_columns.csv"
    all_files_data = {}

    # ディレクトリ内の全XMLファイルを解析
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".xml"):
            file_path = os.path.join(input_dir, file_name)
            file_data = parse_mybatis_xml(file_path)
            all_files_data[file_name] = file_data
    
    # JSONファイルに保存
    save_to_json(all_files_data, json_output_file)
    print(f"JSONファイルに保存しました: {json_output_file}")

    # CSVファイルに保存
    save_to_csv(all_files_data, csv_output_file)
    print(f"CSVファイルに保存しました: {csv_output_file}")

if __name__ == "__main__":
    main()