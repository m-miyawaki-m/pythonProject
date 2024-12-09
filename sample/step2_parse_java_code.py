import os
import json
import re

def parse_java_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    method_pattern = r"public\s+\w+\s+(\w+)\(.*?\)\s*\{.*?(\w+DAO)\.(\w+)\(.*?\);"
    matches = re.findall(method_pattern, content, re.DOTALL)

    logic_to_dao = []
    for match in matches:
        logic_to_dao.append({
            "logic_method": match[0],
            "dao_name": match[1],
            "dao_method": match[2]
        })

    return logic_to_dao

def save_to_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# 実行
java_file_path = "sample/input/UserLogic.java"
output_file = "sample/output/logic_to_dao_mapping.json"
parsed_data = parse_java_file(java_file_path)
save_to_json(parsed_data, output_file)
print(f"解析結果を {output_file} に保存しました。")
