import json
import os

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_crud_mapping(logic_to_dao, parsed_mybatis):
    crud_mapping = []
    for mapping in logic_to_dao:
        dao_method = mapping["dao_method"]
        related_data = next((item for item in parsed_mybatis if item["id"] == dao_method), None)
        if related_data:
            crud_mapping.append({
                "logic_method": mapping["logic_method"],
                "dao_method": dao_method,
                "tables": related_data["tables"],
                "columns": related_data["columns"]
            })
    return crud_mapping

# JSONデータの読み込み
logic_to_dao_file = "sample/output/logic_to_dao_mapping.json"
parsed_mybatis_file = "sample/output/parsed_mybatis.json"
crud_mapping_file = "sample/output/crud_mapping.json"

logic_to_dao = load_json(logic_to_dao_file)
parsed_mybatis = load_json(parsed_mybatis_file)

# マッピングの生成
crud_mapping = generate_crud_mapping(logic_to_dao, parsed_mybatis)

# 結果の保存
with open(crud_mapping_file, "w", encoding="utf-8") as file:
    json.dump(crud_mapping, file, indent=4, ensure_ascii=False)

print(f"CRUDマッピングを {crud_mapping_file} に保存しました。")
