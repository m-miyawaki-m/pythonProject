# parse_ddl.py

import sqlglot
from sqlglot import parse_one, exp
import sys
import os
import json
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

def parse_ddl(statements):
    """
    DDL文を解析し、スキーマ情報を構築します。
    スキーマ情報は {テーブル名またはビュー名: [カラム名1, カラム名2, ...], ...} の形式で辞書として保持されます。
    """
    schema = {}
    for tree in statements:
        # CREATE TABLE の処理
        if isinstance(tree, exp.Create) and tree.args.get('kind') == 'table':
            table_name = tree.this.name
            columns = []
            for column in tree.expressions:
                if isinstance(column, exp.ColumnDef):
                    col_name = column.this.name
                    columns.append(col_name)
            schema[table_name] = columns
        
        # CREATE VIEW の処理
        elif isinstance(tree, exp.Create) and tree.args.get('kind') == 'view':
            view_name = tree.this.name
            columns = []
            
            # カラムリストが指定されている場合
            if tree.args.get('columns'):
                for col in tree.args['columns']:
                    columns.append(col.name)
            else:
                # カラムリストが指定されていない場合、ビューのSELECT文を解析してカラム名を取得
                select = tree.args.get('expression')
                if select:
                    for alias in select.find_all(exp.Alias):
                        columns.append(alias.alias_or_name)
                    # Aliasがない場合もカラム名を取得
                    for column in select.find_all(exp.Column):
                        if not any(alias.this == column for alias in select.find_all(exp.Alias)):
                            columns.append(column.name)
            schema[view_name] = columns
    return schema

def save_schema_to_json(schema, output_file='schema.json'):
    """
    スキーマ情報をJSONファイルに保存します。
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=4)
    print(f"Schema information saved to '{output_file}'.")

def main(ddl_dir, output_file='schema.json'):
    if not os.path.isdir(ddl_dir):
        print(f"Error: ディレクトリ '{ddl_dir}' が存在しません。")
        sys.exit(1)
    
    # ディレクトリ内の全てのSQLファイルを取得
    ddl_files = [os.path.join(ddl_dir, f) for f in os.listdir(ddl_dir) if f.endswith('.sql')]
    
    if not ddl_files:
        print(f"No SQL files found in directory '{ddl_dir}'.")
        sys.exit(1)
    
    all_schema = {}
    for ddl_file in ddl_files:
        print(f"\nProcessing DDL file: {ddl_file}")
        ddl_statements = read_sql_file(ddl_file)
        schema_info = parse_ddl(ddl_statements)
        all_schema.update(schema_info)
    
    print("\n--- Consolidated Schema Information ---")
    for name, columns in all_schema.items():
        print(f"{name}: {columns}")
    
    save_schema_to_json(all_schema, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse DDL files and extract schema information.")
    parser.add_argument('ddl_directory', help="Path to the directory containing DDL (.sql) files.")
    parser.add_argument('--output', default='schema.json', help="Output JSON file for schema information.")
    
    args = parser.parse_args()
    main(args.ddl_directory, args.output)
