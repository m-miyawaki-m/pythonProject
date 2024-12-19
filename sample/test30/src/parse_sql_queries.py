# parse_sql_queries.py

import sqlglot
from sqlglot import parse_one, exp
import sys
import os
import json
import csv
import pandas as pd
import argparse

def read_sql_file(file_path):
    """
    SQLファイルを読み込み、sqlglot.parseを使用してSQL文のリストを返します。
    コメント行（-- で始まる行）は無視します。
    """
    if not os.path.isfile(file_path):
        print(f"Error: ファイル '{file_path}' が存在しません。")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # コメントを削除
    lines = content.splitlines()
    lines = [line for line in lines if not line.strip().startswith('--')]
    content = '\n'.join(lines)
    
    # sqlglot.parseを使用してステートメントを解析
    try:
        statements = sqlglot.parse(content, read='postgres')
    except Exception as e:
        print(f"Error parsing SQL file '{file_path}': {e}")
        statements = []
    
    return statements

def load_schema(schema_file='schema.json'):
    """
    スキーマ情報をJSONファイルから読み込みます。
    スキーマ情報は {テーブル名またはビュー名: [カラム名1, カラム名2, ...], ...} の形式で辞書として保持されます。
    """
    if not os.path.isfile(schema_file):
        print(f"Error: スキーマファイル '{schema_file}' が存在しません。")
        sys.exit(1)
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    # カラムリストをセットに変換
    schema = {table: set(columns) for table, columns in schema.items()}
    return schema

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

def extract_columns_with_table(tree, tables, schema_info):
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
            # エイリアスが指定されていない場合、スキーマ情報を利用して特定
            possible_tables = []
            for table, cols in schema_info.items():
                if column_name in cols:
                    possible_tables.append(table)
            if len(possible_tables) == 1:
                columns.setdefault(possible_tables[0], set()).add(column_name)
            elif len(possible_tables) > 1:
                # 同名カラムが複数のテーブルに存在する場合、'AMBIGUOUS' に分類
                columns.setdefault('AMBIGUOUS', set()).add(column_name)
            else:
                # スキーマに存在しないカラム
                columns.setdefault('UNKNOWN', set()).add(column_name)
    
    # INSERT文の場合
    if isinstance(tree, exp.Insert):
        table_name = tree.this.name
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
    for condition in tree.find_all(exp.Column):
        table_alias = condition.table
        column_name = condition.name
        if table_alias:
            table_name = tables.get(table_alias, 'UNKNOWN')
            columns.setdefault(table_name, set()).add(column_name)
        else:
            # エイリアスが指定されていない場合、スキーマ情報を利用して特定
            possible_tables = []
            for table, cols in schema_info.items():
                if column_name in cols:
                    possible_tables.append(table)
            if len(possible_tables) == 1:
                columns.setdefault(possible_tables[0], set()).add(column_name)
            elif len(possible_tables) > 1:
                # 同名カラムが複数のテーブルに存在する場合、'AMBIGUOUS' に分類
                columns.setdefault('AMBIGUOUS', set()).add(column_name)
            else:
                # スキーマに存在しないカラム
                columns.setdefault('UNKNOWN', set()).add(column_name)
    
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

def parse_sql(sql, dialect='postgres', schema_info=None):
    """
    単一のSQL文を解析し、DML、テーブル、カラムを抽出します。
    """
    try:
        tree = parse_one(sql, read=dialect)
    except sqlglot.errors.ParseError as e:
        print(f"ParseError in SQL: {e}")
        return None
    
    dml = extract_dml(tree)
    tables = extract_tables_aliases(tree)
    columns = extract_columns_with_table(tree, tables, schema_info)
    
    # CTEの解析
    for cte in tree.find_all(exp.CTE):
        cte_alias = cte.alias
        if isinstance(cte, exp.CTE):
            cte_expression = cte.this
            cte_tables = extract_tables_aliases(cte_expression)
            cte_columns = extract_columns_with_table(cte_expression, cte_tables, schema_info)
            # CTE内のテーブルとカラムを統合
            tables[cte_alias] = cte_alias  # CTE自体を仮想テーブルとして登録
            schema_info[cte_alias] = cte_columns.get(cte_alias, set())
            for table, cols in cte_columns.items():
                columns.setdefault(table, set()).update(cols)
    
    # サブクエリの解析
    for subquery in tree.find_all(exp.Subquery):
        sub_tables = extract_tables_aliases(subquery)
        sub_columns = extract_columns_with_table(subquery, sub_tables, schema_info)
        # テーブルとカラムを統合
        tables.update(sub_tables)
        for table, cols in sub_columns.items():
            columns.setdefault(table, set()).update(cols)
    
    # 結果を整理
    tables_list = sorted(set(tables.values()))  # 重複を排除
    columns_dict = {table: sorted(cols) for table, cols in columns.items()}
    
    return {
        'DML': dml,
        'Tables': tables_list,
        'Columns': columns_dict
    }

def parse_queries(sql_queries, schema_info):
    """
    SQLクエリのリストを解析し、各クエリのDML、テーブル、カラムを抽出します。
    結果をリストとして返します。
    """
    results = []
    for idx, tree in enumerate(sql_queries, 1):
        # SQL文を文字列に戻す
        sql = tree.sql()
        sql = sql.strip()
        if not sql:
            continue
        print(f"\n--- SQL Statement {idx} ---")
        print(sql)
        parsed = parse_sql(sql, schema_info=schema_info)
        if parsed:
            print("\nParsed Information:")
            print(f"DML: {parsed['DML']}")
            print(f"Tables: {parsed['Tables']}")
            print("Columns:")
            for table, cols in parsed['Columns'].items():
                print(f"  {table}: {cols}")
            # フォーマットを整えてCSV用に文字列に変換
            tables_str = ";".join(parsed['Tables'])
            columns_str = ";".join([f"{table}:{','.join(cols)}" for table, cols in parsed['Columns'].items()])
            results.append({
                'SQL': sql.replace('\n', ' ').strip(),
                'DML': parsed['DML'],
                'Tables': tables_str,
                'Columns': columns_str
            })
        else:
            print("Failed to parse the SQL statement.")
    return results

def save_results_to_csv(results, output_file):
    """
    解析結果をCSVファイルに保存します。
    CSVのカラムは 'SQL', 'DML', 'Tables', 'Columns' です。
    """
    if not results:
        print(f"No results to save for '{output_file}'.")
        return
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nParsed results saved to '{output_file}'.")

def main(schema_file, sql_dir, output_dir='parsed_csvs'):
    # スキーマ情報の読み込み
    schema_info = load_schema(schema_file)
    
    # 出力ディレクトリの作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 指定ディレクトリ内の全てのSQLファイルを取得
    sql_files = [os.path.join(sql_dir, f) for f in os.listdir(sql_dir) if f.endswith('.sql')]
    
    if not sql_files:
        print(f"No SQL files found in directory '{sql_dir}'.")
        sys.exit(1)
    
    # 各SQLファイルの解析
    for sql_file in sql_files:
        print(f"\nProcessing SQL file: {sql_file}")
        sql_queries = read_sql_file(sql_file)
        results = parse_queries(sql_queries, schema_info)
        
        # 出力CSVファイル名の決定
        base_name = os.path.splitext(os.path.basename(sql_file))[0]
        output_csv = os.path.join(output_dir, f"{base_name}_parsed.csv")
        
        # 結果をCSVに保存
        save_results_to_csv(results, output_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse SQL files and extract DML, Tables, and Columns.")
    parser.add_argument('schema_json', help="Path to the schema JSON file.")
    parser.add_argument('sql_directory', help="Path to the directory containing SQL (.sql) files.")
    parser.add_argument('--output', default='parsed_csvs', help="Output directory for parsed CSV files.")
    
    args = parser.parse_args()
    main(args.schema_json, args.sql_directory, args.output)
