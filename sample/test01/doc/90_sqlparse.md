`sqlparse`は Python のライブラリで、SQL 文を解析し、トークン化やフォーマットを行うのに役立ちます。このプロジェクトでは、MyBatis XML ファイル内の SQL 文を解析して、テーブル名、カラム名、条件式などを抽出するために使用されています。以下に`sqlparse`の基本的な使い方を説明します。

---

### **1. sqlparse の基本構文**

#### **インストール**

```bash
pip install sqlparse
```

#### **主な機能**

- **トークン化（解析）**: SQL 文を構文単位で分解します。
- **フォーマット**: SQL 文を読みやすい形式に整形します。

---

### **2. 主な API と例**

#### **SQL の解析**

`sqlparse.parse()`を使用して SQL 文をトークン化できます。

```python
import sqlparse

sql = "SELECT u.id, u.name FROM USER_DATA u WHERE u.id = 1"
parsed = sqlparse.parse(sql)

for statement in parsed:
    print(statement.tokens)  # トークンリストを取得
```

#### **SQL のフォーマット**

`sqlparse.format()`で SQL 文を整形します。

```python
formatted_sql = sqlparse.format(
    "select * from USER_DATA where id = 1",
    reindent=True,  # インデントを追加
    keyword_case='upper'  # キーワードを大文字に変換
)
print(formatted_sql)
# 出力:
# SELECT *
# FROM USER_DATA
# WHERE id = 1
```

#### **トークンの種類**

トークンのタイプを判定するために`ttype`プロパティを利用します。

```python
from sqlparse import sql, tokens

sql = "SELECT id, name FROM USER_DATA"
parsed = sqlparse.parse(sql)[0]
for token in parsed.tokens:
    if token.ttype is tokens.DML:  # Data Manipulation Language
        print(f"DML: {token}")
    elif isinstance(token, sql.Identifier):
        print(f"Identifier: {token.get_real_name()}")
```

---

### **3. 本プロジェクトでの`sqlparse`の利用例**

#### **FROM 句と JOIN 句の解析**

プロジェクト内の`process_from_and_join()`関数は、`FROM`句や`JOIN`句からテーブル名とエイリアスを抽出します。

```python
def process_from_and_join(tokens, tables, alias_map):
    for token in tokens:
        if token.ttype is sqlparse.tokens.Keyword and token.value.upper() in ['FROM', 'JOIN']:
            # テーブル名やエイリアスの処理
            ...
```

#### **SELECT 句の解析**

`process_select_clause()`関数では、`SELECT`句からカラム情報を取得します。

```python
def process_select_clause(tokens, alias_map, tables):
    for token in tokens:
        if token.ttype is sqlparse.tokens.DML and token.value.upper() == "SELECT":
            # カラム名の処理
            ...
```

#### **WHERE 句の解析**

`process_where_clause()`関数で条件式やパラメータを抽出します。

```python
def process_where_clause(tokens, alias_map, tables):
    for token in tokens:
        if token.value.upper() == "WHERE":
            condition = "".join(str(t) for t in tokens)
            parameters = re.findall(r"[#|$]{\w+}", condition)
            ...
```

---

### **4. 使用例：MyBatis XML ファイルの解析**

以下のように MyBatis の SQL 文を解析し、テーブルやカラム情報を抽出できます。

```python
sql = """
SELECT u.id, u.name
FROM USER_DATA u
WHERE u.id = #{id}
"""
parsed_data = parse_sql(sql)
print(parsed_data)
# 出力:
# {
#     "USER_DATA": {
#         "columns": ["id", "name"],
#         "parameters": ["#{id}"],
#         "condition": "u.id = #{id}",
#         "source": ""
#     }
# }
```

---

### **5. 補足**

- **エイリアスの解決**: SQL 内のテーブル別名（エイリアス）を適切にマッピングすることで、どのテーブルのカラムかを正確に判断します。
- **再帰的なタグ展開**: MyBatis の`<include>`タグや`<sql>`タグの展開後の SQL 解析にも対応しています。

`sqlparse`は SQL の副問い合わせ（サブクエリ）に対応しています。ただし、`sqlparse`自体は SQL 文の解析を行うライブラリであり、サブクエリを特別に抽出するための直接的な API は提供していません。そのため、サブクエリを扱う場合は、SQL 文をトークン化した後、必要な部分を手動で抽出する処理を追加する必要があります。

以下に、`sqlparse`を使用して副問い合わせを扱う方法を説明します。

---

### **1. 基本例：副問い合わせの解析**

副問い合わせを含む SQL 文を`sqlparse`で解析できます。

```python
import sqlparse

sql = """
SELECT id, name
FROM (
    SELECT id, name
    FROM USERS
    WHERE age > 18
) AS subquery
WHERE id < 100
"""

# SQL文を解析
parsed = sqlparse.parse(sql)

for stmt in parsed:
    for token in stmt.tokens:
        if isinstance(token, sqlparse.sql.Parenthesis):
            print("サブクエリの発見:")
            print(token.value)  # サブクエリの内容を取得
```

---

### **2. `Parenthesis`によるサブクエリの抽出**

サブクエリは一般的に括弧（`()`）で囲まれているため、`sqlparse.sql.Parenthesis`として認識されます。このトークンを検索してサブクエリ部分を抽出します。

#### **例: トークンからサブクエリを抽出**

```python
def extract_subqueries(tokens):
    subqueries = []
    for token in tokens:
        if isinstance(token, sqlparse.sql.Parenthesis):
            subqueries.append(token.value)  # サブクエリを追加
        elif hasattr(token, 'tokens'):
            # ネストされたサブクエリを再帰的に検索
            subqueries.extend(extract_subqueries(token.tokens))
    return subqueries

sql = """
SELECT id
FROM (
    SELECT id FROM USERS WHERE age > 18
) AS subquery
WHERE id < 100
"""

parsed = sqlparse.parse(sql)[0]
subqueries = extract_subqueries(parsed.tokens)
print("サブクエリ一覧:")
for subquery in subqueries:
    print(subquery)
```

---

### **3. サブクエリ内の構造をさらに解析**

サブクエリ自体を再度解析することで、テーブル名や条件式を抽出できます。

```python
def parse_sql(sql):
    """
    SQL文を解析し、サブクエリを含む構造を解析する
    """
    parsed = sqlparse.parse(sql)
    subqueries = extract_subqueries(parsed[0].tokens)
    result = {"main_query": sql, "subqueries": []}

    for subquery in subqueries:
        parsed_subquery = sqlparse.parse(subquery)
        result["subqueries"].append({"query": subquery, "tokens": parsed_subquery[0].tokens})
    return result

sql = """
SELECT id
FROM (
    SELECT id FROM USERS WHERE age > 18
) AS subquery
WHERE id < 100
"""

parsed_result = parse_sql(sql)
print("解析結果:", parsed_result)
```

---

### **4. 制限事項**

- **サブクエリの種類**:
  - `FROM`句の中だけでなく、`WHERE`句や`SELECT`句に含まれるサブクエリにも対応可能です。ただし、それらの位置を特定するには追加のロジックが必要です。
- **ネストの深さ**:

  - 複数の入れ子状サブクエリにも対応できますが、深い解析には再帰的処理が必要です。

- **パフォーマンス**:
  - 複雑な SQL 文（非常に多くのネストされたサブクエリを含む）では、解析速度に影響が出る可能性があります。

---

### **結論**

`sqlparse`は副問い合わせをトークンとして認識できますが、サブクエリの具体的な内容を抽出して操作するためには、独自の処理を追加する必要があります。`sqlparse`が提供する`Parenthesis`トークンを活用すれば、サブクエリを検出して解析することが可能です。

プロジェクトの具体的な要件に合わせて、サブクエリ抽出のカスタムロジックを組み込むことをお勧めします。
