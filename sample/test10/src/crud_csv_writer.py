import csv

def save_to_csv(output_file, call_relations):
    """CSVファイルに結果を保存"""
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["業務操作", "呼び出し元メソッド", "呼び出し先メソッド",
                      "DAO メソッド", "CRUD 種別", "MyBatis Namespace", "MyBatis Id", "パラメータ"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for relation in call_relations:
            writer.writerow(relation)
