プロパティごとに解析結果を別のディレクトリに振り分け、さらにクラスごとに CSV を出力するスクリプトを以下に示します。この設計では、ディレクトリの整理と CSV 出力を自動化します。

---

### スクリプト概要

1. **プロパティごとに出力ディレクトリを作成**

   - `LOGIC`, `DAO`, `MyBatis` の各プロパティごとにディレクトリを作成。

2. **クラスごとに CSV を出力**

   - ファイル名（クラス名）をキーとして CSV を作成。

3. **ファイルの処理**
   - 各プロパティに対応する解析を実行し、結果をプロパティのディレクトリに保存。

---

### 実装例

#### メインスクリプト

```python
import csv
import os
from logic_parser import analyze_logic
from dao_parser import analyze_dao
from xml_parser import analyze_xml

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
            file_name = os.path.basename(file_path)
            class_name, _ = os.path.splitext(file_name)
            property_type = row['property']

            if property_type not in property_dirs:
                print(f"未対応のプロパティ: {property_type} ({file_path})")
                continue

            output_dir = property_dirs[property_type]
            output_csv = os.path.join(output_dir, f"{class_name}.csv")

            if property_type == "LOGIC":
                print(f"LOGIC解析: {file_path}")
                results = analyze_logic(file_path)
            elif property_type == "DAO":
                print(f"DAO解析: {file_path}")
                results = analyze_dao(file_path)
            elif property_type == "MyBatis":
                print(f"MyBatis解析: {file_path}")
                results = analyze_xml(file_path)
            else:
                print(f"未対応の解析: {file_path}")
                results = []

            # クラスごとに CSV を出力
            with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)

            print(f"結果を出力: {output_csv}")

# 実行例
process_files_with_output("./file_properties.csv", "./output")
```

---

#### 各解析モジュールの戻り値仕様

各モジュール (`logic_parser`, `dao_parser`, `xml_parser`) は、以下のようなリスト形式のデータを返すことを想定しています。

```python
[
    {"key1": "value1", "key2": "value2"},
    {"key1": "value3", "key2": "value4"}
]
```

---

#### ロジック解析モジュール（例: `logic_parser.py`）

```python
def analyze_logic(file_path):
    # ロジック解析の処理を実行
    # ここでは仮の結果を返す
    return [
        {"method": "methodA", "called_by": "methodB"},
        {"method": "methodB", "called_by": "methodC"}
    ]
```

---

#### DAO 解析モジュール（例: `dao_parser.py`）

```python
def analyze_dao(file_path):
    # DAO解析の処理を実行
    # 仮の結果を返す
    return [
        {"sql_operation": "SELECT", "mybatis_id": "findAll", "parameters": "id, name"}
    ]
```

---

#### XML 解析モジュール（例: `xml_parser.py`）

```python
import xml.etree.ElementTree as ET

def analyze_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    results = []
    for element in root.findall(".//"):
        if element.tag in {"select", "insert", "update", "delete"}:
            results.append({
                "tag": element.tag,
                "id": element.attrib.get('id', 'N/A'),
                "sql": ''.join(element.itertext())
            })
    return results
```

---

### 実行後の出力

以下のようにプロパティごとにディレクトリが作成され、その中にクラスごとの CSV が出力されます。

```
output/
├── LOGIC/
│   ├── UserLogic.csv
│   ├── AccountLogic.csv
├── DAO/
│   ├── UserDao.csv
│   ├── AccountDao.csv
├── MyBatis/
│   ├── UserMapper.csv
│   ├── AccountMapper.csv
```

---

### この方法のメリット

1. **整理されたディレクトリ構成**

   - プロパティごとにディレクトリを分けることで結果の把握が容易。

2. **クラス単位での詳細出力**

   - クラスごとに個別の CSV を出力することで、柔軟な分析が可能。

3. **スケーラブルな設計**
   - プロパティや解析モジュールを追加する場合でも容易に拡張可能。

必要に応じて調整し、プロジェクトに適用してください！
