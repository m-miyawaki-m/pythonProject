import json


# JSONの読み込み
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# Logicメソッドと対応付け
def generate_crud_mapping(logic_to_dao, parsed_data):
    crud_mapping = []

    for mapping in logic_to_dao:
        dao_method = mapping["dao_method"]
        related_data = next(
            (item for item in parsed_data if item["id"] == dao_method), None
        )

        if related_data:
            crud_mapping.append(
                {
                    "logic_method": mapping["logic_method"],
                    "dao_method": dao_method,
                    "tables": related_data["tables"],
                    "columns": related_data["columns"],
                }
            )

    return crud_mapping


# LogicとDAOの関係マッピングデータ
logic_to_dao_mapping = [
    {"logic_method": "fetchUserById", "dao_method": "getUserById"},
    {"logic_method": "addUser", "dao_method": "insertUser"},
]

# 実行
parsed_data = load_json("./sample/file/parsed_mybatis.json")
crud_mapping = generate_crud_mapping(logic_to_dao_mapping, parsed_data)

# 結果出力
for mapping in crud_mapping:
    print(f"Logic Method: {mapping['logic_method']}")
    print(f"DAO Method: {mapping['dao_method']}")
    print(f"Tables: {', '.join(mapping['tables'])}")
    print(f"Columns: {', '.join(mapping['columns'])}")
    print("-" * 40)
