import os
import csv
import re

def assign_properties_and_find_files(directory, output_csv):
    files_with_properties = []

    # パターンの正規表現
    dao_pattern = re.compile(r".*Dao\.java$")
    logic_pattern = re.compile(r".*Logic\.java$")
    mybatis_pattern = re.compile(r"[a-zA-Z]{6}[0-9]{5}\.xml$")

    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            last_modified = os.path.getmtime(file_path)

            # プロパティの割り当て
            if dao_pattern.match(filename):
                file_property = "DAO"
            elif logic_pattern.match(filename):
                file_property = "LOGIC"
            elif mybatis_pattern.match(filename):
                file_property = "MyBatis"
            else:
                file_property = "OTHER"  # 該当しない場合のデフォルト

            files_with_properties.append({
                "file_name": filename,
                "file_path": file_path,
                "last_modified": last_modified,
                "property": file_property
            })

    # CSV に保存
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["file_name", "file_path", "last_modified", "property"])
        writer.writeheader()
        writer.writerows(files_with_properties)

    print(f"プロパティ付きのファイル一覧を {output_csv} に出力しました。")

# 実行例
assign_properties_and_find_files("./sample/test20/sample_project", "./sample/test20/output/file_properties.csv")