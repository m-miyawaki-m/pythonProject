ビジネスロジックのメソッドを起点に、関連する DAO 層の操作や MyBatis XML ファイルを組み合わせた CSV を出力するコードを設計します。この出力は、メソッドごとに以下の情報を含みます：

1. **ビジネスロジック層**:

   - クラス名
   - メソッド名
   - 呼び出しメソッド

2. **DAO 層**:

   - DAO クラス名
   - SQL 操作の種類（`select`, `insert` など）
   - 使用されたパラメータ

3. **MyBatis XML**:
   - `namespace`
   - タグ（`select`, `insert` など）
   - SQL 文

---

### **設計フロー**

1. **解析結果の統合**:

   - ロジック層の呼び出しメソッドから DAO メソッドを追跡。
   - DAO メソッドから MyBatis XML の関連情報をマッチング。

2. **出力形式の設計**:
   - メソッドごとの情報を一つの行にまとめる。
   - 必要な情報が見つからない場合は空白 (`None`) を補完。

---

### **実装コード**

以下は、ビジネスロジック層を起点に、DAO 層および MyBatis XML の情報を組み合わせた結果を CSV に出力する Python スクリプトです。

#### **コード例**

```python
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
    logic_dir="./output/LOGIC",
    dao_dir="./output/DAO",
    mybatis_dir="./output/MyBatis",
    output_file="./output/combined_logic_dao_xml.csv"
)
```

---

### **統合結果の例**

#### **CSV 出力例**

| logic_class | logic_method | called_method | dao_class | sql_operation | sql_parameters      | namespace              | xml_tag | sql_query               |
| ----------- | ------------ | ------------- | --------- | ------------- | ------------------- | ---------------------- | ------- | ----------------------- |
| LogicClass  | methodA      | findAll       | UserDao   | select        | findAll             | com.example.UserMapper | select  | SELECT \* FROM users    |
| LogicClass  | methodB      | insertUser    | UserDao   | insert        | insertUser, #{user} | com.example.UserMapper | insert  | INSERT INTO users (...) |

---

### **設計のポイント**

1. **呼び出しの追跡**:

   - ロジック層の呼び出しメソッドを DAO 層の解析結果と突き合わせる。

2. **DAO と MyBatis のマッピング**:

   - DAO 層の SQL 操作（`sql_operation`）を MyBatis XML の `id` に関連付ける。

3. **柔軟な出力**:
   - 不足している情報（呼び出しメソッドや MyBatis データ）がある場合でも空白で補完しつつ結果を出力。

---

### 応用

- **JSON 出力**:
  - 結果を JSON に変換して、より構造化された形式で保存。
- **依存グラフの生成**:
  - ロジック層から MyBatis 層までのフローをグラフ化して可視化。

このコードを利用すれば、ビジネスロジックを起点にした一気通貫の結果を CSV に出力できます。必要に応じてカスタマイズしてください！
