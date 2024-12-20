以下に、このスレッドで議論した内容を整理し、ステップバイステップのフローとしてまとめます。このフローは、MyBatis XML ファイル解析と SQL 解析のプロセスを 2 段階に分けたアプローチに基づいています。

---

## **フロー全体概要**

1. **XML 解析（ステップ 1）**

   - MyBatis XML ファイルを解析し、必要な情報を CSV 形式で出力。
   - MyBatis ID と SQL 文を含めることで、後続の解析を簡易化。

2. **SQL 解析（ステップ 2）**
   - ステップ 1 で生成された CSV を入力として使用し、SQL 文を解析。
   - テーブル名、カラム名、条件式、DML 句などを抽出し、新たな CSV に出力。

---

### **ステップ 1: XML 解析**

#### **目的**

- MyBatis XML ファイルからタグ情報、MyBatis ID（`id`属性）、SQL 文を抽出して CSV に保存。
- SQL 文そのものは文字列として扱い、詳細解析は行わない。

#### **詳細手順**

1. **XML ファイルの読み込み**
   - `xml.etree.ElementTree`を使用して XML をパース。
   - `<select>`, `<insert>`, `<update>`, `<delete>`, `<sql>`タグを対象に情報を収集。
2. **タグ情報の収集**
   - タグ名（例: `select`）。
   - `id`属性値（MyBatis ID）。
   - タグ内の SQL 文を文字列として抽出。
3. **CSV 出力**
   - 以下のカラムを持つ CSV を生成：
     - **ファイル名**: XML ファイルの名前。
     - **タグ**: MyBatis タグ名（例: `select`, `insert`）。
     - **ID（MyBatis ID）**: `id`属性値。
     - **SQL 文**: タグ内の SQL 文（展開は行わない）。
   - サンプル出力例：
     | ファイル名 | タグ | ID（MyBatis ID） | SQL 文 |
     | ----------------- | ------ | ---------------- | ------------------------------------- |
     | UserDataMapper.xml | select | findAll | SELECT u.id, u.name FROM USER_DATA ...|

---

### **ステップ 2: SQL 解析**

#### **目的**

- ステップ 1 で出力された CSV の SQL 文を解析し、構造的な情報（テーブル名、カラム名、条件式など）を別 CSV に出力。

#### **詳細手順**

1. **CSV ファイルの読み込み**
   - ステップ 1 で生成された CSV を読み込み。
   - SQL 文と MyBatis ID を取得。
2. **SQL 文の解析**
   - `sqlparse`を使用して SQL 文をトークン化し、以下の情報を抽出：
     - **DML 句**: SELECT, INSERT, UPDATE, DELETE。
     - **テーブル名**: FROM 句や JOIN 句から取得。
     - **カラム名**: SELECT 句や INSERT 文などで利用されるカラム。
     - **条件式**: WHERE 句や JOIN 条件。
3. **CSV 出力**
   - 以下のカラムを持つ CSV を生成：
     - **ファイル名**: 元の XML ファイルの名前。
     - **ID（MyBatis ID）**: `id`属性値。
     - **DML 句**: SQL 文の操作種別（例: SELECT）。
     - **テーブル名**: SQL 文で利用されるテーブル。
     - **カラム名**: SQL 文で利用されるカラム。
     - **条件式**: WHERE 句や JOIN 条件の内容。
   - サンプル出力例：
     | ファイル名 | ID（MyBatis ID） | DML 句 | テーブル名 | カラム名 | 条件式 |
     | ----------------- | ---------------- | ------- | ------------ | ---------- | ---------------- |
     | UserDataMapper.xml | findAll | SELECT | USER_DATA | id, name | u.sex = #{sex} |

---

### **期待される効果**

1. **データの紐付け**

   - MyBatis ID を基準に SQL 文と解析結果を関連付けることで、追跡性が向上。

2. **効率的な解析**

   - XML 解析と SQL 解析を分離することで、それぞれのプロセスが簡素化され、エラーの分離が可能。

3. **柔軟性**
   - SQL 解析後の CSV をさらに加工・結合することで、追加の分析や可視化が可能。

---

### **次のステップ**

1. XML 解析（ステップ 1）のコード実装または修正。
2. SQL 解析（ステップ 2）の実装。
3. 2 段階解析フローの統合とテスト。
4. 必要に応じた出力フォーマットやエラー処理の追加。

このフローをベースに具体的な実装を進める準備が整いました。必要に応じて、各ステップのコード例も提供可能です。

MyBatis XML 解析に `namespace` を含めるようにスクリプトを修正します。MyBatis の `namespace` 属性は、`<mapper>` タグの `namespace` 属性値から取得できます。

---

### 修正版: XML 解析モジュール

`namespace` 属性を抽出し、解析結果に含めます。

#### **コード例**

```python
import xml.etree.ElementTree as ET
import os

def analyze_xml(file_path):
    """
    MyBatis XMLファイルを解析し、指定された情報を抽出します。

    Args:
        file_path (str): 解析対象のXMLファイルのパス。

    Returns:
        list: 抽出結果のリスト。各エントリは辞書形式。
    """
    results = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        file_name = os.path.basename(file_path)  # ファイル名を取得

        # <mapper> タグの namespace 属性を取得
        namespace = root.attrib.get("namespace", "N/A")

        # MyBatis タグを解析
        for element in root.findall(".//"):
            if element.tag in {"select", "insert", "update", "delete"}:
                tag_info = {
                    "file_name": file_name,
                    "namespace": namespace,  # namespace を追加
                    "tag": element.tag,
                    "id": element.attrib.get("id", "N/A"),
                    "sql": "".join(element.itertext()).strip()
                }
                results.append(tag_info)
    except ET.ParseError as e:
        print(f"XML解析エラー: {file_path} - {e}")

    return results
```

---

### 修正版: メインスクリプト

`analyze_xml` の結果に `namespace` を含めたデータを出力するように調整します。

#### **コード例**

```python
import csv
import os
from xml_parser import analyze_xml  # XML解析モジュールをインポート

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_files_with_output(input_csv, output_base_dir):
    # プロパティごとのディレクトリを準備
    property_dirs = {
        "LOGIC": os.path.join(output_base_dir, "LOGIC"),
        "DAO": os.path.join(output_base_dir, "DAO"),
        "MyBatis": os.path.join(output_base_dir, "MyBatis"),
    }
    for prop, path in property_dirs.items():
        create_directory(path)

    with open(input_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            file_path = row['file_path']
            file_name = os.path.basename(file_path)  # ファイル名を取得
            class_name, _ = os.path.splitext(file_name)
            property_type = row['property']

            if property_type not in property_dirs:
                print(f"未対応のプロパティ: {property_type} ({file_path})")
                continue

            output_dir = property_dirs[property_type]
            output_csv = os.path.join(output_dir, f"{class_name}.csv")

            if property_type == "MyBatis":
                print(f"MyBatis解析: {file_path}")
                results = analyze_xml(file_path)
            else:
                print(f"未対応の解析: {property_type}")
                results = []

            # クラスごとに CSV を出力
            if results:
                with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
                    writer = csv.DictWriter(output_file, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
                print(f"結果を出力: {output_csv}")

# 実行例
process_files_with_output("./file_properties.csv", "./output")
```

---

### 出力結果例

対象 XML ファイル: `UserMapper.xml`

#### **XML 例**

```xml
<mapper namespace="com.example.UserMapper">
    <select id="findAll">
        SELECT * FROM users
    </select>
    <select id="findById">
        SELECT * FROM users WHERE id = #{id}
    </select>
</mapper>
```

#### **CSV 例**

| file_name      | namespace              | tag    | id       | sql                                   |
| -------------- | ---------------------- | ------ | -------- | ------------------------------------- |
| UserMapper.xml | com.example.UserMapper | select | findAll  | SELECT \* FROM users                  |
| UserMapper.xml | com.example.UserMapper | select | findById | SELECT \* FROM users WHERE id = #{id} |

保存先:

```
output/MyBatis/UserMapper.csv
```

---

### この変更の効果

1. **`namespace`の追加**

   - MyBatis の名前空間を含むことで、SQL の所属先を明確化。

2. **一貫したフォーマット**

   - ファイル名、タグ、`id`属性、SQL 文を整理して出力。

3. **柔軟な拡張性**
   - `namespace`を利用してさらに分析やグループ化が可能。

---

これで、`namespace` を含む解析結果を出力できるようになります。この設計をベースにプロジェクトに適用してください！
