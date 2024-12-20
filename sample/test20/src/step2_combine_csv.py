import csv
import os
from collections import defaultdict

def combine_logic_dao_xml(logic_dir, dao_dir, mybatis_dir, output_file):
    """
    ビジネスロジックを起点に、DAOとMyBatis XMLの情報を組み合わせたCSVを出力します。

    Args:
        logic_dir (str): ロジック層解析結果のディレクトリ。
        dao_dir (str): DAO層解析結果のディレクトリ。
        mybatis_dir (str): MyBatis解析結果のディレクトリ。
        output_file (str): 統合結果を保存するCSVファイルパス。
    """
    combined_results = []

    # DAO層とMyBatisのマッピング
    dao_to_xml_map = defaultdict(list)
    for file_name in os.listdir(mybatis_dir):
        if file_name.endswith(".csv"):
            with open(os.path.join(mybatis_dir, file_name), 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    dao_to_xml_map[row['id']].append({
                        "namespace": row['namespace'],
                        "tag": row['tag'],
                        "sql": row['sql']
                    })

    # ロジック層を起点に処理
    for file_name in os.listdir(logic_dir):
        if file_name.endswith(".csv"):
            with open(os.path.join(logic_dir, file_name), 'r', encoding='utf-8') as logic_file:
                logic_reader = csv.DictReader(logic_file)
                for logic_row in logic_reader:
                    logic_class_name = logic_row["class_name"]
                    logic_method_name = logic_row["method_name"]
                    called_methods = [v for k, v in logic_row.items() if k.startswith("called_method_") and v]

                    # DAO解析結果の確認
                    for called_method in called_methods:
                        for dao_file in os.listdir(dao_dir):
                            if dao_file.endswith(".csv"):
                                with open(os.path.join(dao_dir, dao_file), 'r', encoding='utf-8') as dao_file:
                                    dao_reader = csv.DictReader(dao_file)
                                    for dao_row in dao_reader:
                                        if dao_row["method_name"] == called_method:
                                            # MyBatis XML の確認
                                            dao_operation = dao_row["sql_operation"]
                                            dao_params = dao_row["parameters"]
                                            xml_info = dao_to_xml_map.get(dao_row["sql_operation"], [])
                                            
                                            # 統合結果に追加
                                            for xml_entry in xml_info:
                                                combined_results.append({
                                                    "logic_class": logic_class_name,
                                                    "logic_method": logic_method_name,
                                                    "called_method": called_method,
                                                    "dao_class": dao_row["class_name"],
                                                    "sql_operation": dao_operation,
                                                    "sql_parameters": dao_params,
                                                    "namespace": xml_entry["namespace"],
                                                    "xml_tag": xml_entry["tag"],
                                                    "sql_query": xml_entry["sql"]
                                                })

    # 結果をCSVに出力
    with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
        fieldnames = [
            "logic_class", "logic_method", "called_method",
            "dao_class", "sql_operation", "sql_parameters",
            "namespace", "xml_tag", "sql_query"
        ]
        writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_results)

    print(f"統合結果を {output_file} に出力しました。")

# 実行例
combine_logic_dao_xml(
    logic_dir="./sample/test20/output/LOGIC",
    dao_dir="./sample/test20/output/DAO",
    mybatis_dir="./sample/test20/output/MyBatis",
    output_file="./sample/test20/output/combined_logic_dao_xml.csv"
)
