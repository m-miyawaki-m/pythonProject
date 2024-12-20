import json
import re
import xml.etree.ElementTree as ET


def parse_mybatis_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    extracted_data = []

    target_tags = {"select", "insert", "update", "delete"}

    for element in root:
        if element.tag in target_tags:
            sql_content = element.text.strip()

            # テーブル名の抽出
            table_pattern = r"FROM\s+(\w+)|INTO\s+(\w+)|UPDATE\s+(\w+)"
            tables = re.findall(table_pattern, sql_content)
            table_names = [
                table for match in tables for table in match if table
            ]

            # カラム名の抽出
            column_pattern = (
                r"SELECT\s+(.*?)\s+FROM|INSERT\s+INTO\s"
                r"+\w+\s+\((.*?)\)|UPDATE\s+\w+\s+SET\s+(.*?)\="
            )
            columns = re.findall(column_pattern, sql_content)
            column_names = [col for match in columns for col in match if col]

            extracted_data.append(
                {
                    "tag": element.tag,
                    "id": element.attrib.get("id"),
                    "tables": table_names,
                    "columns": column_names,
                }
            )

    return extracted_data


# 結果を保存
def save_parsed_data(data, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# 実行
xml_file_path = "./sample/file/mybatis_mapper.xml"
output_file = "./sample/file/parsed_mybatis.json"
parsed_data = parse_mybatis_xml(xml_file_path)
save_parsed_data(parsed_data, output_file)
print(f"解析結果を {output_file} に保存しました。")
