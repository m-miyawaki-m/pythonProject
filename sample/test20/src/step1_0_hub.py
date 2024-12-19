import csv
import os
from step1_1_xml_parser import analyze_xml  # XML解析モジュールをインポート
from step1_2_logic_parser import analyze_logic_with_javalang
from step1_3_dao_parser import analyze_dao_with_javalang

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_files_with_output(input_csv, output_base_dir):
    # プロパティごとのディレクトリを準備
    property_dirs = {
        "LOGIC": os.path.join(output_base_dir, "LOGIC"),
        "DAO": os.path.join(output_base_dir, "DAO"),
        "MyBatis": os.path.join(output_base_dir, "MyBatis"),
    }
    for prop, path in property_dirs.items():
        create_directory(path)

    with open(input_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            file_path = row['file_path']
            file_name = os.path.basename(file_path)  # ファイル名を取得
            class_name, _ = os.path.splitext(file_name)
            property_type = row['property']

            if property_type not in property_dirs:
                print(f"未対応のプロパティ: {property_type} ({file_path})")
                continue

            output_dir = property_dirs[property_type]
            output_csv = os.path.join(output_dir, f"{class_name}.csv")

            if property_type == "LOGIC":
                print(f"LOGIC解析: {file_path}")
                results = analyze_logic_with_javalang(file_path)
            elif property_type == "DAO":
                print(f"DAO解析: {file_path}")
                results = analyze_dao_with_javalang(file_path)
            elif property_type == "MyBatis":
                print(f"MyBatis解析: {file_path}")
                results = analyze_xml(file_path)
            else:
                print(f"未対応の解析: {property_type}")
                results = []
                continue

            # クラスごとに CSV を出力
            if results:
                with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
                    writer = csv.DictWriter(output_file, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
                print(f"結果を出力: {output_csv}")

# 実行例
process_files_with_output("./sample/test20/output/file_properties.csv", "./sample/test20/output")