import re
import os

def parse_java_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # LogicメソッドとDAO呼び出しを解析
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

# 実行
java_file_path = "./sample/file/UserLogic.java"
logic_to_dao_mapping = parse_java_file(java_file_path)

# 結果表示
for mapping in logic_to_dao_mapping:
    print(f"Logic Method: {mapping['logic_method']}")
    print(f"DAO Name: {mapping['dao_name']}")
    print(f"DAO Method: {mapping['dao_method']}")
    print("-" * 40)
