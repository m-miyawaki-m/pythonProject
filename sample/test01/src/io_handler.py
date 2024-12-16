import os
import json
import csv

def read_xml_files(directory):
    """
    指定したディレクトリからXMLファイルを読み取る。
    """
    xml_files = {}
    for file_name in os.listdir(directory):
        if file_name.endswith(".xml"):
            xml_files[file_name] = os.path.join(directory, file_name)
    return xml_files

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
        writer.writerow(["ファイル名", "タグ", "ID", "テーブル名", "カラム名", "条件式", "条件の出典"])

        for file_name, tags in data.items():
            for tag, tables in tags.items():
                for tag_id, details in tables.items():
                    if not details:  # データが空でも出力
                        writer.writerow([file_name, tag, tag_id, "", "", "", ""])
                        continue
                    for table_name, table_data in details.items():
                        columns = table_data.get("columns", [""])
                        parameters = table_data.get("parameters", [""])
                        for column in columns:
                            writer.writerow([
                                file_name, tag, tag_id, table_name, column,
                                table_data.get("condition", ""),
                                table_data.get("source", "")
                            ])
                        for param in parameters:
                            writer.writerow([
                                file_name, tag, tag_id, table_name, "",
                                table_data.get("condition", ""),
                                table_data.get("source", "")
                            ])
