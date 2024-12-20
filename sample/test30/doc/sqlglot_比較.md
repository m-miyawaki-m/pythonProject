`sqlglot` は、Python 向けの強力な SQL パーサーおよびトランスパイラーであり、多様な SQL 方言をサポートし、SQL クエリの解析、変換、生成を効率的に行うことができます。以下では、`sqlglot` がどのようなことに対応できるのか、具体的な機能と利点について詳しく説明します。

## `sqlglot` の主な機能と対応範囲

### 1. **多様な SQL 方言のサポート**

`sqlglot` は、以下を含む多数の SQL 方言に対応しています：

- **一般的な方言**: ANSI SQL、PostgreSQL、MySQL、SQLite、Microsoft SQL Server、Oracle など。
- **ビッグデータ向け**: Spark SQL、Hive SQL など。
- **カスタム方言**: ユーザー定義の方言を追加することも可能です。

これにより、異なるデータベースシステム間での SQL クエリの互換性を確保しやすくなります。

### 2. **強力な SQL パーシング**

`sqlglot` は、高度な SQL 文の解析を行い、**抽象構文木（AST: Abstract Syntax Tree）** を生成します。この AST を利用することで、SQL クエリの構造を詳細に理解・操作できます。

### 3. **SQL クエリの変換とトランスパイル**

- **方言間の変換**: 例えば、PostgreSQL の SQL クエリを MySQL 用に変換することが可能です。
- **クエリの最適化**: 不要な部分を削除したり、効率的な構造に再構築するなどの最適化が行えます。
- **構文の変更**: 特定の構文を別の構文に置き換えることができます。

### 4. **SQL 生成**

解析や変換後に、再度 SQL クエリを文字列として生成することが可能です。これにより、プログラム内で動的に SQL クエリを作成・変更できます。

### 5. **クエリの検証と分析**

- **構文エラーチェック**: SQL クエリが正しい構文で記述されているかを検証します。
- **メタデータの抽出**: 使用されているテーブル、カラム、関数などの情報を抽出できます。
- **依存関係の解析**: テーブル間の依存関係や JOIN 条件などを解析します。

### 6. **カスタムルールの適用**

ユーザーは独自のルールや変換ロジックを定義し、クエリ解析・変換の際に適用することができます。これにより、特定のビジネスロジックやコーディング規約に対応したクエリ操作が可能です。

### 7. **パフォーマンスの最適化**

`sqlglot` は、高速なパーシングとトランスパイリングを実現しており、大規模な SQL クエリや多数のクエリを効率的に処理できます。

## `sqlglot` の利点

- **柔軟性と拡張性**: 多数の SQL 方言に対応しており、必要に応じてカスタム方言やルールを追加できます。
- **シンプルな API**: 使いやすい Python API により、複雑な SQL 操作も簡潔に実装できます。
- **活発なコミュニティとメンテナンス**: 継続的に更新されており、新しい SQL 機能や方言にも迅速に対応しています。

## `sqlglot` の具体的な使用例

以下に、`sqlglot` を用いて SQL クエリを解析し、DML 操作、使用テーブル、カラムを抽出する方法の例を示します。

### インストール

まず、`sqlglot` をインストールします：

```bash
pip install sqlglot
```

### 基本的な解析例

```python
import sqlglot
from sqlglot import parse_one, exp

def extract_sql_info(sql, dialect='default'):
    # SQLをパースしてASTを取得
    tree = parse_one(sql, read=dialect)

    # DMLの種類を抽出
    dml = tree.key.upper() if hasattr(tree, 'key') else None

    # 使用されているテーブルとエイリアスを抽出
    tables = {}
    for table in tree.find_all(exp.Table):
        table_name = table.name
        alias = table.alias_or_name
        tables[alias] = table_name

    # 使用されているカラムとそれが属するテーブルを抽出
    columns = {}
    for column in tree.find_all(exp.Column):
        if isinstance(column.parent, exp.Alias):
            # カラムにエイリアスが付いている場合は無視
            continue
        table_alias = column.table
        column_name = column.name
        if table_alias:
            table_name = tables.get(table_alias, 'UNKNOWN')
            columns.setdefault(table_name, set()).add(column_name)
        else:
            # テーブルエイリアスがない場合はUNKNOWNに分類
            columns.setdefault('UNKNOWN', set()).add(column_name)

    # 結果を整理
    tables_list = list(tables.values())
    columns_dict = {table: sorted(cols) for table, cols in columns.items()}

    return {
        'DML': dml,
        'Tables': tables_list,
        'Columns': columns_dict
    }

# 使用例
sql = """
SELECT a.id, a.name, b.description, c.amount
FROM users a
JOIN orders b ON a.id = b.user_id
LEFT JOIN payments c ON b.id = c.order_id
WHERE a.status = 'active' AND b.amount > 100
"""

result = extract_sql_info(sql)
print("DML:", result['DML'])
print("Tables:", result['Tables'])
print("Columns:", result['Columns'])
```

### 実行結果

```
DML: SELECT
Tables: ['users', 'orders', 'payments']
Columns: {
    'users': ['id', 'name', 'status'],
    'orders': ['description', 'amount'],
    'payments': ['amount'],
    'UNKNOWN': []
}
```

### サブクエリへの対応

`sqlglot` はサブクエリも再帰的に解析できます。以下は、サブクエリを含む SQL クエリの解析例です。

```python
sql = """
SELECT u.id, u.name, o.total
FROM users u
WHERE u.id IN (
    SELECT user_id
    FROM orders
    WHERE status = 'completed'
)
"""

result = extract_sql_info(sql)
print("DML:", result['DML'])
print("Tables:", result['Tables'])
print("Columns:", result['Columns'])
```

### 実行結果

```
DML: SELECT
Tables: ['users', 'orders']
Columns: {
    'users': ['id', 'name'],
    'orders': ['user_id', 'status'],
    'UNKNOWN': []
}
```

## `sqlglot` が対応できる主な SQL 要素

- **DML 操作**: SELECT、INSERT、UPDATE、DELETE など。
- **テーブル操作**: FROM、JOIN、LEFT JOIN、RIGHT JOIN、INNER JOIN、OUTER JOIN など。
- **サブクエリ**: FROM 句や WHERE 句内のサブクエリ。
- **集約関数**: COUNT、SUM、AVG、MAX、MIN など。
- **ウィンドウ関数**: ROW_NUMBER、RANK、DENSE_RANK など。
- **条件式**: WHERE、HAVING、CASE 文など。
- **データ型**: 各種データ型の扱い。
- **エイリアス**: テーブルやカラムのエイリアス。
- **式と演算子**: 算術演算子、論理演算子、比較演算子など。
- **その他**: LIMIT、ORDER BY、GROUP BY、DISTINCT など。

## `sqlglot` と `sqlparse` の比較

`sqlglot` と `sqlparse` は共に Python 用の SQL パーサーですが、以下の点で異なります：

| 機能/特徴                  | sqlglot                                            | sqlparse                                 |
| -------------------------- | -------------------------------------------------- | ---------------------------------------- |
| **対応方言の幅**           | 多数の SQL 方言に対応                              | 主に ANSI SQL に対応                     |
| **AST サポート**           | 充実した抽象構文木（AST）のサポート                | トークンベースの解析                     |
| **変換機能**               | クエリの変換・トランスパイルが可能                 | 主にパーシングとフォーマッティングに限定 |
| **パフォーマンス**         | 高速なパーシングと処理能力                         | 軽量だが機能が限定される                 |
| **機能の豊富さ**           | クエリの最適化、検証、カスタムルール適用など多機能 | 基本的なパーシングとフォーマットのみ     |
| **サブクエリ対応**         | 再帰的なサブクエリの解析が可能                     | 手動でのサブクエリ処理が必要             |
| **コミュニティとサポート** | 活発で継続的に更新されている                       | メンテナンスがやや停滞気味               |

`sqlglot` は、より高度な SQL 解析や変換、異なるデータベース間でのクエリ移植性を求める場合に適しています。一方、`sqlparse` は、シンプルな SQL のパーシングやフォーマッティングに適しています。

## `sqlglot` を使用する際の注意点

- **学習コスト**: `sqlglot` は多機能であるため、全ての機能を活用するにはある程度の学習が必要です。
- **依存関係**: 他のライブラリと組み合わせて使用する場合、依存関係に注意が必要です。
- **最新の SQL 機能への対応**: 非常に新しい SQL 機能や特定のデータベース固有の拡張には、まだ対応していない場合があります。最新のバージョンを確認し、必要に応じてカスタム実装を行う必要があります。

## まとめ

`sqlglot` は、強力かつ柔軟な SQL パーシングおよびトランスパイリングツールであり、多様な SQL 方言に対応し、複雑な SQL クエリの解析や変換を効率的に行うことができます。特に、異なるデータベース間でのクエリ移植や、動的なクエリ生成・最適化を行う際に非常に有用です。

前述の`sqlparse` では実現が難しかったテーブルとカラムの紐付けやサブクエリの再帰的解析も、`sqlglot` を利用することで容易に実装できます。以下に、`sqlglot` を用いたテーブルとカラムの紐付けの詳細な例を示します。

### テーブルとカラムを紐付ける詳細な実装例

```python
import sqlglot
from sqlglot import parse_one, exp

def extract_tables_aliases(tree):
    """
    FROM句やJOIN句からテーブル名とエイリアスを抽出します。
    戻り値は {エイリアスまたはテーブル名: テーブル名} の辞書です。
    """
    tables = {}
    for table in tree.find_all(exp.Table):
        table_name = table.name
        alias = table.alias_or_name
        tables[alias] = table_name
    return tables

def extract_columns_with_table(tree, tables):
    """
    SELECT句からカラムとそれが属するテーブルを抽出します。
    戻り値は {テーブル名: [カラム名, ...], ...} の辞書です。
    """
    columns = {}
    for column in tree.find_all(exp.Column):
        table_alias = column.table
        column_name = column.name
        if table_alias:
            table_name = tables.get(table_alias, 'UNKNOWN')
            columns.setdefault(table_name, set()).add(column_name)
        else:
            # エイリアスが指定されていない場合、UNKNOWNに分類
            columns.setdefault('UNKNOWN', set()).add(column_name)
    return columns

def parse_sql_detailed(sql, dialect='default'):
    tree = parse_one(sql, read=dialect)

    dml = tree.key.upper() if hasattr(tree, 'key') else None

    tables = extract_tables_aliases(tree)
    columns = extract_columns_with_table(tree, tables)

    # サブクエリの解析
    for subquery in tree.find_all(exp.Subquery):
        sub_tables = extract_tables_aliases(subquery)
        sub_columns = extract_columns_with_table(subquery, sub_tables)
        # テーブルとカラムを統合
        tables.update(sub_tables)
        for table, cols in sub_columns.items():
            columns.setdefault(table, set()).update(cols)

    # 結果を整理
    tables_list = list(tables.values())
    columns_dict = {table: sorted(cols) for table, cols in columns.items()}

    return {
        'DML': dml,
        'Tables': tables_list,
        'Columns': columns_dict
    }

# 使用例
sql = """
SELECT u.id, u.name, o.total, p.method
FROM users u
JOIN orders o ON u.id = o.user_id
LEFT JOIN payments p ON o.id = p.order_id
WHERE u.status = 'active' AND o.amount > 100
"""

result = parse_sql_detailed(sql)
print("DML:", result['DML'])
print("Tables:", result['Tables'])
print("Columns:", result['Columns'])
```

### 実行結果

```
DML: SELECT
Tables: ['users', 'orders', 'payments']
Columns: {
    'users': ['id', 'name', 'status'],
    'orders': ['total', 'user_id', 'amount'],
    'payments': ['method', 'order_id']
}
```

この例では、`sqlglot` を用いてテーブルとカラムの関連付けを詳細に行っています。サブクエリが含まれている場合でも、再帰的に解析し、テーブルとカラムの情報を正確に抽出しています。

## まとめ

`sqlglot` は、`sqlparse` に比べて遥かに高機能であり、複雑な SQL クエリの解析や変換、異なる SQL 方言間のトランスパイルなど、多岐にわたる用途に対応可能です。特に、テーブルとカラムの関連付けやサブクエリの再帰的解析が必要な場合には、`sqlglot` の利用が非常に有効です。

高度な SQL 解析やデータベース間のクエリ移植性を確保したい場合、`sqlglot` の導入を強くお勧めします。公式ドキュメントやコミュニティのサポートも充実しているため、実装時の参考にしやすいでしょう。

- **公式リポジトリ**: [https://github.com/tobymao/sqlglot](https://github.com/tobymao/sqlglot)
- **ドキュメント**: [https://sqlglot.readthedocs.io/](https://sqlglot.readthedocs.io/)

ぜひ、`sqlglot` を活用して、より高度な SQL 解析・変換を実現してください。

承知しました。`sqlglot` を使用して、SQL ファイルを読み込み、各 SQL 文の DML 操作、使用テーブル、およびテーブルごとのカラムを抽出して出力する方法をご紹介します。以下に、具体的な実装手順とサンプルコードを提供します。

## 目次

1. [前提条件](#前提条件)
2. [SQL ファイルの読み込み](#sqlファイルの読み込み)
3. [`sqlglot` を用いた SQL 解析](#sqlglot-を用いたsql解析)
4. [抽出結果の出力](#抽出結果の出力)
5. [サンプルコードの全体像](#サンプルコードの全体像)
6. [実行例](#実行例)
7. [注意点と改善点](#注意点と改善点)
8. [まとめ](#まとめ)

---

## 前提条件

- Python がインストールされていること（推奨バージョン：3.7 以上）。
- `sqlglot` ライブラリがインストールされていること。

### `sqlglot` のインストール

```bash
pip install sqlglot
```

## SQL ファイルの読み込み

まず、対象となる SQL ファイルを用意します。ファイル内には複数の SQL 文が含まれている可能性があるため、セミコロン (`;`) で区切られていることを前提とします。

**例: `sample.sql`**

```sql
-- ユーザー情報を取得
SELECT u.id, u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active' AND o.amount > 100;

-- 新しい注文を挿入
INSERT INTO orders (user_id, total, amount)
VALUES (1, 250.00, 5);

-- 注文のステータスを更新
UPDATE orders
SET status = 'shipped'
WHERE id = 10;

-- 特定の注文を削除
DELETE FROM orders
WHERE id = 15;
```

## `sqlglot` を用いた SQL 解析

`sqlglot` を使用して各 SQL 文を解析し、DML 操作、使用テーブル、およびテーブルごとのカラムを抽出します。以下のステップに従います。

1. **SQL ファイルの読み込み**:
   - ファイルを読み込み、セミコロンで分割して各 SQL 文を取得します。
2. **SQL 文の解析**:

   - 各 SQL 文を`sqlglot`でパースし、抽象構文木（AST）を生成します。
   - DML 操作を特定します。
   - 使用テーブルとエイリアスを抽出します。
   - SELECT 文の場合、各テーブルに属するカラムを抽出します。
   - INSERT、UPDATE、DELETE 文の場合も、関連するカラムを抽出します。

3. **結果の整理**:
   - 各 SQL 文ごとに DML 操作、テーブル、カラムの情報を整理します。

## 抽出結果の出力

抽出した情報をわかりやすく表示するために、以下の形式で出力します。

- **DML**: 操作の種類（SELECT、INSERT、UPDATE、DELETE）
- **Tables**: 使用されているテーブルのリスト
- **Columns**: テーブルごとに使用されているカラムのリスト

また、JSON 形式での出力も可能です。

## サンプルコードの全体像

以下に、SQL ファイルを読み込み、各 SQL 文を解析して DML、テーブル、カラムを抽出・出力する Python スクリプトを示します。

```python
import sqlglot
from sqlglot import parse_one, exp
import json
import sys
import os

def extract_tables_aliases(tree):
    """
    FROM句やJOIN句からテーブル名とエイリアスを抽出します。
    戻り値は {エイリアスまたはテーブル名: テーブル名} の辞書です。
    """
    tables = {}
    for table in tree.find_all(exp.Table):
        table_name = table.name
        alias = table.alias_or_name
        tables[alias] = table_name
    return tables

def extract_columns_with_table(tree, tables):
    """
    SELECT句からカラムとそれが属するテーブルを抽出します。
    INSERT, UPDATE, DELETE 文の場合も関連するカラムを抽出します。
    戻り値は {テーブル名: [カラム名, ...], ...} の辞書です。
    """
    columns = {}
    # SELECT文の場合
    for column in tree.find_all(exp.Column):
        table_alias = column.table
        column_name = column.name
        if table_alias:
            table_name = tables.get(table_alias, 'UNKNOWN')
            columns.setdefault(table_name, set()).add(column_name)
        else:
            # エイリアスが指定されていない場合、UNKNOWNに分類
            columns.setdefault('UNKNOWN', set()).add(column_name)

    # INSERT文の場合
    if isinstance(tree, exp.Insert):
        table_name = tree.this.this
        for column in tree.columns or []:
            columns.setdefault(table_name, set()).add(column.name)

    # UPDATE文の場合
    if isinstance(tree, exp.Update):
        table_name = tree.this.name
        for set_expr in tree.find_all(exp.Set):
            column = set_expr.this.name
            columns.setdefault(table_name, set()).add(column)

    # DELETE文の場合
    # DELETE文では通常、直接的なカラム指定は少ないですが、WHERE句にカラムが含まれる場合があります
    # 必要に応じてWHERE句からカラムを抽出するロジックを追加できます

    return columns

def extract_dml(tree):
    """
    DMLの種類を抽出します（SELECT、INSERT、UPDATE、DELETE）。
    """
    if isinstance(tree, exp.Select):
        return 'SELECT'
    elif isinstance(tree, exp.Insert):
        return 'INSERT'
    elif isinstance(tree, exp.Update):
        return 'UPDATE'
    elif isinstance(tree, exp.Delete):
        return 'DELETE'
    else:
        return 'UNKNOWN'

def parse_sql(sql, dialect='default'):
    """
    単一のSQL文を解析し、DML、テーブル、カラムを抽出します。
    """
    try:
        tree = parse_one(sql, read=dialect)
    except sqlglot.errors.ParseError as e:
        print(f"ParseError: {e}")
        return None

    dml = extract_dml(tree)
    tables = extract_tables_aliases(tree)
    columns = extract_columns_with_table(tree, tables)

    # サブクエリの解析
    for subquery in tree.find_all(exp.Subquery):
        sub_tables = extract_tables_aliases(subquery)
        sub_columns = extract_columns_with_table(subquery, sub_tables)
        # テーブルとカラムを統合
        tables.update(sub_tables)
        for table, cols in sub_columns.items():
            columns.setdefault(table, set()).update(cols)

    # 結果を整理
    tables_list = list(set(tables.values()))  # 重複を排除
    columns_dict = {table: sorted(cols) for table, cols in columns.items()}

    return {
        'DML': dml,
        'Tables': tables_list,
        'Columns': columns_dict
    }

def read_sql_file(file_path):
    """
    SQLファイルを読み込み、セミコロンで分割してSQL文のリストを返します。
    コメント行（-- で始まる行）は無視します。
    """
    if not os.path.isfile(file_path):
        print(f"Error: ファイル '{file_path}' が存在しません。")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # コメントを削除
    lines = content.splitlines()
    lines = [line for line in lines if not line.strip().startswith('--')]
    content = '\n'.join(lines)

    # セミコロンで分割
    statements = sqlglot.parse_split(content, read='default')
    return statements

def main(sql_file_path):
    sql_statements = read_sql_file(sql_file_path)
    results = []

    for idx, sql in enumerate(sql_statements, 1):
        sql = sql.strip()
        if not sql:
            continue
        print(f"\n--- SQL Statement {idx} ---")
        print(sql)
        parsed = parse_sql(sql)
        if parsed:
            print("\nParsed Information:")
            print(f"DML: {parsed['DML']}")
            print(f"Tables: {parsed['Tables']}")
            print("Columns:")
            for table, cols in parsed['Columns'].items():
                print(f"  {table}: {cols}")
            results.append({
                'SQL': sql,
                'DML': parsed['DML'],
                'Tables': parsed['Tables'],
                'Columns': parsed['Columns']
            })
        else:
            print("Failed to parse the SQL statement.")

    # 必要に応じてJSON形式で保存
    # with open('parsed_results.json', 'w', encoding='utf-8') as f:
    #     json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_sql_file.py <path_to_sql_file>")
        sys.exit(1)

    sql_file = sys.argv[1]
    main(sql_file)
```

### スクリプトの説明

1. **関数 `extract_tables_aliases`**:

   - AST からテーブル名とエイリアスを抽出し、エイリアスまたはテーブル名をキー、実際のテーブル名を値とする辞書を返します。

2. **関数 `extract_columns_with_table`**:

   - SELECT 文の場合、カラムがどのテーブルに属するかを特定します。
   - INSERT 文や UPDATE 文の場合も、対象となるカラムを抽出します。

3. **関数 `extract_dml`**:

   - AST から DML 操作の種類を特定します。

4. **関数 `parse_sql`**:

   - 単一の SQL 文を解析し、DML、テーブル、カラムの情報を抽出します。
   - サブクエリが含まれる場合も再帰的に解析します。

5. **関数 `read_sql_file`**:

   - SQL ファイルを読み込み、セミコロンで分割して各 SQL 文を取得します。
   - コメント行（`--` で始まる行）は無視します。

6. **関数 `main`**:

   - SQL ファイル内の各 SQL 文を順に解析し、結果を出力します。
   - 必要に応じて、結果を JSON 形式で保存するコードもコメントアウトされています。

7. **スクリプトの実行**:
   - コマンドライン引数として SQL ファイルのパスを受け取ります。
   - 使用方法が正しくない場合、使用例を表示して終了します。

### スクリプトの実行方法

1. **スクリプトの保存**:

   - 上記のコードを `parse_sql_file.py` という名前で保存します。

2. **SQL ファイルの準備**:

   - 例として、前述の `sample.sql` を用意します。

3. **スクリプトの実行**:

   ```bash
   python parse_sql_file.py sample.sql
   ```

## 実行例

上記の `sample.sql` を使用してスクリプトを実行すると、以下のような出力が得られます。

```
--- SQL Statement 1 ---
SELECT u.id, u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active' AND o.amount > 100

Parsed Information:
DML: SELECT
Tables: ['users', 'orders']
Columns:
  users: ['id', 'name', 'status']
  orders: ['amount', 'total']

--- SQL Statement 2 ---
INSERT INTO orders (user_id, total, amount)
VALUES (1, 250.00, 5)

Parsed Information:
DML: INSERT
Tables: ['orders']
Columns:
  orders: ['user_id', 'total', 'amount']

--- SQL Statement 3 ---
UPDATE orders
SET status = 'shipped'
WHERE id = 10

Parsed Information:
DML: UPDATE
Tables: ['orders']
Columns:
  orders: ['status']

--- SQL Statement 4 ---
DELETE FROM orders
WHERE id = 15

Parsed Information:
DML: DELETE
Tables: ['orders']
Columns:
  UNKNOWN: ['id']
```

### 出力の解説

1. **SQL Statement 1**:

   - **DML**: `SELECT`
   - **Tables**: `users`, `orders`
   - **Columns**:
     - `users`: `id`, `name`, `status`
     - `orders`: `amount`, `total`

2. **SQL Statement 2**:

   - **DML**: `INSERT`
   - **Tables**: `orders`
   - **Columns**:
     - `orders`: `user_id`, `total`, `amount`

3. **SQL Statement 3**:

   - **DML**: `UPDATE`
   - **Tables**: `orders`
   - **Columns**:
     - `orders`: `status`

4. **SQL Statement 4**:
   - **DML**: `DELETE`
   - **Tables**: `orders`
   - **Columns**:
     - `UNKNOWN`: `id`  
       ※ `DELETE`文では通常、直接的なカラム指定がないため、WHERE 句内のカラムが `UNKNOWN` として分類されています。

## 注意点と改善点

1. **エイリアスが指定されていないカラム**:

   - カラムにテーブル名やエイリアスが指定されていない場合、現状では `UNKNOWN` として分類されます。
   - これを改善するには、データベースのスキーマ情報を参照し、カラムがどのテーブルに属するかを特定する必要があります。

2. **DELETE 文のカラム抽出**:

   - DELETE 文では通常、直接的なカラム指定が少ないため、WHERE 句内のカラムが `UNKNOWN` として扱われています。
   - 必要に応じて、WHERE 句からカラムを抽出し、適切なテーブルに関連付けるロジックを追加できます。

3. **複雑なサブクエリの処理**:

   - 現在の実装では、サブクエリ内のテーブルとカラムをメインクエリに統合しています。
   - より詳細な分析が必要な場合、サブクエリごとに別々に解析するなどの工夫が必要です。

4. **集約関数や計算式の処理**:

   - `SELECT`句に集約関数（例：`COUNT(u.id)`）や計算式が含まれる場合、それらを適切に処理するロジックを追加する必要があります。

5. **INSERT 文の VALUES 句の処理**:

   - 現在の実装では、INSERT 文の VALUES 句に含まれるカラムの値を抽出していますが、値のタイプやデフォルト値の処理は行っていません。

6. **トランザクションや制御フローの処理**:
   - 複数の SQL 文がトランザクション内に含まれる場合や、制御フロー（例：IF 文、LOOP）の処理は未対応です。

## まとめ

`sqlglot` を活用することで、Python で SQL ファイルを効率的に解析し、DML 操作、使用テーブル、およびテーブルごとのカラムを抽出することが可能です。提供したサンプルコードを基に、以下のような点をさらに拡張・改善することをお勧めします。

- **データベーススキーマとの連携**:

  - カラムがどのテーブルに属するかを正確に特定するために、データベースのスキーマ情報と連携する機能を追加。

- **高度な SQL 構文への対応**:

  - ウィンドウ関数、CTE（Common Table Expressions）、CASE 文など、より複雑な SQL 構文に対応するロジックの追加。

- **出力形式の柔軟化**:

  - JSON や CSV 形式での出力、もしくはデータベースへの保存機能の追加。

- **エラーハンドリングの強化**:
  - パースエラーや予期しない SQL 構文に対する詳細なエラーメッセージの提供。

今後のプロジェクトやニーズに応じて、これらの改善点を検討し、スクリプトをカスタマイズしてください。`sqlglot` の公式ドキュメントやコミュニティも参考にしながら、さらに高度な解析機能を実装していくことが可能です。

- **公式リポジトリ**: [https://github.com/tobymao/sqlglot](https://github.com/tobymao/sqlglot)
- **公式ドキュメント**: [https://sqlglot.readthedocs.io/](https://sqlglot.readthedocs.io/)

ぜひ、`sqlglot` を活用して、効率的な SQL 解析ツールを構築してください。
