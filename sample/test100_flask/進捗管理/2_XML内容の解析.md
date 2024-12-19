以下の手順で、指定された XML ファイルから MyBatis の ID と SQL 文を抽出し、エラーのない SQL 解析を行うスクリプトを作成できます。最終的には、結果を CSV に保存します。

### **手順の概要**

1. **XML ファイルの検索**: 指定ディレクトリから XML ファイルを検索。
2. **MyBatis タグと SQL 文の抽出**: `<select>`, `<insert>`, `<update>`, `<delete>`タグをパースし、SQL 文を抽出。
3. **SQL 文の前処理**: `include`, `if`, `trim`, `foreach`タグやバインド変数（`#{}`や`${}`）を無害化して解析可能な形式に変換。
4. **SQL 文の解析**: SQL 構造を解析し、DML 句やテーブル名を抽出。
5. **結果を CSV に保存**。

以下に、具体的なコードを示します。

---

### **コード実装**

#### **1. XML ファイルの検索**

```python
import os
import re
import csv

def find_xml_files(directory):
    pattern = re.compile(r"[a-zA-Z]{5}[0-9]{6}\.xml")
    xml_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if pattern.match(file):
                xml_files.append(os.path.join(root, file))
    return xml_files
```

#### **2. MyBatis タグと SQL 文の抽出**

```python
import xml.etree.ElementTree as ET

def extract_mybatis_data(file_path):
    mybatis_data = []
    tree = ET.parse(file_path)
    root = tree.getroot()

    for tag in root.findall(".//"):
        if tag.tag in {"select", "insert", "update", "delete"}:
            sql_text = ET.tostring(tag, encoding='unicode', method='text').strip()
            sql_id = tag.attrib.get('id', 'unknown_id')
            mybatis_data.append({
                "file_name": os.path.basename(file_path),
                "tag": tag.tag,
                "id": sql_id,
                "sql": sql_text
            })
    return mybatis_data
```

#### **3. SQL 文の前処理**

```python
def preprocess_sql(sql):
    # タグやバインド変数を無害化
    sql = re.sub(r"<include.*?>.*?</include>", "", sql, flags=re.DOTALL)
    sql = re.sub(r"<if.*?>.*?</if>", "", sql, flags=re.DOTALL)
    sql = re.sub(r"<trim.*?>.*?</trim>", "", sql, flags=re.DOTALL)
    sql = re.sub(r"<foreach.*?>.*?</foreach>", "", sql, flags=re.DOTALL)
    sql = re.sub(r"#{.*?}", "?", sql)
    sql = re.sub(r"\${.*?}", "?", sql)
    return sql.strip()
```

#### **4. SQL 文の解析**

```python
import sqlparse

def analyze_sql(sql):
    parsed = sqlparse.parse(sql)
    if parsed:
        statement = parsed[0]
        return {
            "dml": statement.get_type(),
            "tables": [str(token) for token in statement.tokens if token.ttype is None]
        }
    return {"dml": "UNKNOWN", "tables": []}
```

#### **5. 結果を CSV に保存**

```python
def save_to_csv(file_path, data, fieldnames):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
```

---

### **統合フロー**

```python
def main(project_directory, output_csv):
    xml_files = find_xml_files(project_directory)
    all_data = []

    for xml_file in xml_files:
        mybatis_data = extract_mybatis_data(xml_file)
        for entry in mybatis_data:
            entry['sql'] = preprocess_sql(entry['sql'])
            sql_analysis = analyze_sql(entry['sql'])
            entry.update(sql_analysis)
        all_data.extend(mybatis_data)

    fieldnames = ["file_name", "tag", "id", "sql", "dml", "tables"]
    save_to_csv(output_csv, all_data, fieldnames)
    print(f"解析結果を {output_csv} に保存しました。")

# 実行例
main("/path/to/project", "xml_analysis.csv")
```

---

### **期待される CSV 形式**

| file_name          | tag    | id      | sql                               | dml    | tables    |
| ------------------ | ------ | ------- | --------------------------------- | ------ | --------- |
| UserDataMapper.xml | select | findAll | SELECT \* FROM users WHERE id = ? | SELECT | ["users"] |

このコードを調整して実行することで、MyBatis XML ファイルの解析と SQL の構造化情報の抽出を効率的に行うことができます。必要に応じて、さらなる機能追加やエラー処理を実装可能です。
