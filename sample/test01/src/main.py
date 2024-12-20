import os
from io_handler import save_to_csv, read_xml_files
from parser import parse_mybatis_xml

def main():
    input_dir = "./sample/test01/input/mybatis_xml"  # XMLファイルのディレクトリ
    csv_output_file = "./sample/test01/output/tables_columns.csv"

    # XMLファイルを読み取る
    xml_files = read_xml_files(input_dir)
    
    # 全ファイルの解析結果を格納
    all_files_data = {}
    for file_name, file_path in xml_files.items():
        print(f"Parsing file: {file_name}")
        file_data = parse_mybatis_xml(file_path)
        all_files_data[file_name] = file_data

    # 結果を保存
    save_to_csv(all_files_data, csv_output_file)

    print(f"CSVファイルに保存しました: {csv_output_file}")

if __name__ == "__main__":
    main()
