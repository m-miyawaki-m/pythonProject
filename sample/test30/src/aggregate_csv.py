# aggregate_csv.py

import pandas as pd
import os
import sys
import argparse

def read_all_csvs(csv_dir):
    """
    指定されたディレクトリ内の全てのCSVファイルを読み込み、DataFrameのリストを返します。
    """
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    dataframes = []
    for csv_file in csv_files:
        path = os.path.join(csv_dir, csv_file)
        df = pd.read_csv(path)
        dataframes.append(df)
    return dataframes

def aggregate_dml(dataframes):
    """
    全てのDataFrameからDML操作の統計を集計します。
    """
    all_dml = []
    for df in dataframes:
        all_dml.extend(df['DML'].dropna().tolist())
    dml_counts = pd.Series(all_dml).value_counts().reset_index()
    dml_counts.columns = ['DML', 'Count']
    return dml_counts

def aggregate_tables(dataframes):
    """
    全てのDataFrameからテーブル使用状況を集計します。
    """
    table_usage = {}
    for df in dataframes:
        for tables in df['Tables'].dropna().tolist():
            table_list = tables.split(';')
            for table in table_list:
                table_usage[table] = table_usage.get(table, 0) + 1
    table_usage_df = pd.DataFrame(list(table_usage.items()), columns=['Table', 'Usage_Count'])
    table_usage_df = table_usage_df.sort_values(by='Usage_Count', ascending=False)
    return table_usage_df

def aggregate_columns(dataframes):
    """
    全てのDataFrameからカラム使用状況を集計します。
    """
    column_usage = {}
    for df in dataframes:
        for columns in df['Columns'].dropna().tolist():
            table_columns = columns.split(';')
            for table_col in table_columns:
                if ':' in table_col:
                    table, cols = table_col.split(':', 1)
                    col_list = cols.split(',')
                    for col in col_list:
                        key = f"{table}.{col}"
                        column_usage[key] = column_usage.get(key, 0) + 1
    column_usage_df = pd.DataFrame(list(column_usage.items()), columns=['Table.Column', 'Usage_Count'])
    column_usage_df = column_usage_df.sort_values(by='Usage_Count', ascending=False)
    return column_usage_df

def save_aggregated_data(dml_df, tables_df, columns_df, output_dir='aggregated_results'):
    """
    集計結果を指定されたディレクトリ内にCSVファイルとして保存します。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    dml_output = os.path.join(output_dir, 'dml_counts.csv')
    tables_output = os.path.join(output_dir, 'table_usage.csv')
    columns_output = os.path.join(output_dir, 'column_usage.csv')
    
    dml_df.to_csv(dml_output, index=False, encoding='utf-8-sig')
    tables_df.to_csv(tables_output, index=False, encoding='utf-8-sig')
    columns_df.to_csv(columns_output, index=False, encoding='utf-8-sig')
    
    print(f"Aggregated DML counts saved to '{dml_output}'.")
    print(f"Aggregated table usage saved to '{tables_output}'.")
    print(f"Aggregated column usage saved to '{columns_output}'.")

def main(csv_dir, output_dir='aggregated_results'):
    # 全てのCSVファイルを読み込む
    dataframes = read_all_csvs(csv_dir)
    if not dataframes:
        print(f"No CSV files found in directory '{csv_dir}'.")
        sys.exit(1)
    
    # DML操作の集計
    dml_counts = aggregate_dml(dataframes)
    
    # テーブル使用状況の集計
    table_usage = aggregate_tables(dataframes)
    
    # カラム使用状況の集計
    column_usage = aggregate_columns(dataframes)
    
    # 集計結果をCSVに保存
    save_aggregated_data(dml_counts, table_usage, column_usage, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate parsed SQL CSV files and generate summary reports.")
    parser.add_argument('parsed_csv_directory', help="Path to the directory containing parsed CSV files.")
    parser.add_argument('--output', default='aggregated_results', help="Output directory for aggregated CSV files.")
    
    args = parser.parse_args()
    main(args.parsed_csv_directory, args.output)
