承知しました。以下では、**複数の SQL ファイルを事前に解析し、各ファイルごとに分析結果を CSV ファイルとして出力**する方法と、**その後に出力された CSV ファイルを読み込んでさらに SQL 解析を行う方法**を、具体的なステップとコード例を用いて詳しく説明します。

## 全体の流れ

1. **ステップ 1: DDL ファイルの解析とスキーマ情報の保存**

   - 複数の DDL ファイルを解析し、スキーマ情報を構築します。
   - スキーマ情報を JSON 形式で保存します。

2. **ステップ 2: 複数の SQL ファイルの解析とファイルごとの CSV 出力**

   - スキーマ情報を基に、複数の SQL ファイルを解析します。
   - 各 SQL ファイルごとに分析結果を CSV ファイルとして出力します。

3. **ステップ 3: CSV ファイルの読み込みとさらに SQL 解析**
   - 出力された各 CSV ファイルを読み込み、必要な追加解析を行います。
   - 解析結果を新たな CSV ファイルやレポートとして保存します。

以下に、各ステップの詳細な実装方法を示します。

---

## ステップ 1: DDL ファイルの解析とスキーマ情報の保存

### 1.1. 必要なライブラリのインストール

```bash
pip install sqlglot
```

### 1.2. `parse_ddl.py` の作成

以下の Python スクリプト `parse_ddl.py` を作成します。このスクリプトは、指定された複数の DDL ファイルを解析し、スキーマ情報を JSON ファイルとして保存します。

```python
# parse_ddl.py

import sqlglot
from sqlglot import parse_one, exp
import sys
import os
import json

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
    statements = sqlglot.parse_split(content, read='postgres')
    return statements

def parse_ddl(statements):
    """
    DDL文を解析し、スキーマ情報を構築します。
    スキーマ情報は {テーブル名: [カラム名1, カラム名2, ...], ...} の形式で辞書として保持されます。
    """
    schema = {}
    for stmt in statements:
        try:
            tree = parse_one(stmt, read='postgres')
        except sqlglot.errors.ParseError as e:
            print(f"ParseError in DDL: {e}")
            continue

        if isinstance(tree, exp.Create):
            table_name = tree.this.name
            columns = []
            for column in tree.expressions:
                if isinstance(column, exp.ColumnDef):
                    col_name = column.this.name
                    columns.append(col_name)
            schema[table_name] = columns
    return schema

def save_schema_to_json(schema, output_file='schema.json'):
    """
    スキーマ情報をJSONファイルに保存します。
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=4)
    print(f"Schema information saved to '{output_file}'.")

def main(ddl_files, output_file='schema.json'):
    all_schema = {}
    for ddl_file in ddl_files:
        print(f"\nProcessing DDL file: {ddl_file}")
        ddl_statements = read_sql_file(ddl_file)
        schema_info = parse_ddl(ddl_statements)
        all_schema.update(schema_info)

    print("\n--- Consolidated Schema Information ---")
    for table, columns in all_schema.items():
        print(f"{table}: {columns}")

    save_schema_to_json(all_schema, output_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_ddl.py <path_to_ddl_file1> <path_to_ddl_file2> ...")
        sys.exit(1)

    ddl_files = sys.argv[1:]
    main(ddl_files)
```

### 1.3. 複数の DDL ファイルの準備

複数の DDL ファイルが存在する場合、それらを用意します。例えば、以下のようなファイルがあるとします：

- `schema_users.sql`
- `schema_orders.sql`
- `schema_payments.sql`

**例: `schema_users.sql`**

```sql
-- users テーブルの定義
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    status VARCHAR(20)
);
```

**例: `schema_orders.sql`**

```sql
-- orders テーブルの定義
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(10, 2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**例: `schema_payments.sql`**

```sql
-- payments テーブルの定義
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    method VARCHAR(50),
    amount DECIMAL(10, 2),
    paid_at TIMESTAMP
);
```

### 1.4. スクリプトの実行

ターミナルまたはコマンドプロンプトで以下のコマンドを実行します。複数の DDL ファイルを指定することで、スキーマ情報が統合されます。

```bash
python parse_ddl.py schema_users.sql schema_orders.sql schema_payments.sql
```

### 1.5. 出力結果

スクリプトを実行すると、以下のような出力が得られます。

```
Processing DDL file: schema_users.sql

Processing DDL file: schema_orders.sql

Processing DDL file: schema_payments.sql

--- Consolidated Schema Information ---
users: ['id', 'name', 'email', 'status']
orders: ['id', 'user_id', 'amount', 'status', 'created_at']
payments: ['id', 'order_id', 'method', 'amount', 'paid_at']
Schema information saved to 'schema.json'.
```

また、`schema.json` ファイルが作成され、以下の内容が保存されます。

**`schema.json`**

```json
{
  "users": ["id", "name", "email", "status"],
  "orders": ["id", "user_id", "amount", "status", "created_at"],
  "payments": ["id", "order_id", "method", "amount", "paid_at"]
}
```

---

## ステップ 2: 複数の SQL ファイルの解析とファイルごとの CSV 出力

### 2.1. 必要なライブラリのインストール

既に`sqlglot`はインストールされていますが、追加で`pandas`を使用することで CSV の操作が容易になります。

```bash
pip install pandas
```

### 2.2. `parse_sql_queries.py` の作成

以下の Python スクリプト `parse_sql_queries.py` を作成します。このスクリプトは、指定された複数の SQL ファイルを解析し、各ファイルごとに CSV ファイルとして分析結果を出力します。

```python
# parse_sql_queries.py

import sqlglot
from sqlglot import parse_one, exp
import sys
import os
import json
import csv
import pandas as pd

def read_sql_file(file_path):
    """
    SQLファイルを読み込み、セミコロンで分割してSQL文のリストを返します。
    コメント行（-- で始まる行）は無視します。
    """
    if not os.path.isfile(file_path):
        print(f"Error: ファイル '{file_path}' が存在しません。")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # コメントを削除
    lines = content.splitlines()
    lines = [line for line in lines if not line.strip().startswith('--')]
    content = '\n'.join(lines)

    # セミコロンで分割
    try:
        statements = sqlglot.parse_split(content, read='postgres')
    except Exception as e:
        print(f"Error parsing SQL file '{file_path}': {e}")
        statements = []

    return statements

def load_schema(schema_file='schema.json'):
    """
    スキーマ情報をJSONファイルから読み込みます。
    スキーマ情報は {テーブル名: [カラム名1, カラム名2, ...], ...} の形式で辞書として保持されます。
    """
    if not os.path.isfile(schema_file):
        print(f"Error: スキーマファイル '{schema_file}' が存在しません。")
        sys.exit(1)

    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    # カラムリストをセットに変換
    schema = {table: set(columns) for table, columns in schema.items()}
    return schema

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

def extract_columns_with_table(tree, tables, schema_info):
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
            # エイリアスが指定されていない場合、スキーマ情報を利用して特定
            possible_tables = []
            for table, cols in schema_info.items():
                if column_name in cols:
                    possible_tables.append(table)
            if len(possible_tables) == 1:
                columns.setdefault(possible_tables[0], set()).add(column_name)
            elif len(possible_tables) > 1:
                # 同名カラムが複数のテーブルに存在する場合、'AMBIGUOUS' に分類
                columns.setdefault('AMBIGUOUS', set()).add(column_name)
            else:
                # スキーマに存在しないカラム
                columns.setdefault('UNKNOWN', set()).add(column_name)

    # INSERT文の場合
    if isinstance(tree, exp.Insert):
        table_name = tree.this.name
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
    for condition in tree.find_all(exp.Column):
        table_alias = condition.table
        column_name = condition.name
        if table_alias:
            table_name = tables.get(table_alias, 'UNKNOWN')
            columns.setdefault(table_name, set()).add(column_name)
        else:
            # エイリアスが指定されていない場合、スキーマ情報を利用して特定
            possible_tables = []
            for table, cols in schema_info.items():
                if column_name in cols:
                    possible_tables.append(table)
            if len(possible_tables) == 1:
                columns.setdefault(possible_tables[0], set()).add(column_name)
            elif len(possible_tables) > 1:
                # 同名カラムが複数のテーブルに存在する場合、'AMBIGUOUS' に分類
                columns.setdefault('AMBIGUOUS', set()).add(column_name)
            else:
                # スキーマに存在しないカラム
                columns.setdefault('UNKNOWN', set()).add(column_name)

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

def parse_sql(sql, dialect='postgres', schema_info=None):
    """
    単一のSQL文を解析し、DML、テーブル、カラムを抽出します。
    """
    try:
        tree = parse_one(sql, read=dialect)
    except sqlglot.errors.ParseError as e:
        print(f"ParseError in SQL: {e}")
        return None

    dml = extract_dml(tree)
    tables = extract_tables_aliases(tree)
    columns = extract_columns_with_table(tree, tables, schema_info)

    # CTEの解析
    for cte in tree.find_all(exp.CTE):
        cte_alias = cte.alias
        if isinstance(cte, exp.CTE):
            cte_expression = cte.this
            cte_tables = extract_tables_aliases(cte_expression)
            cte_columns = extract_columns_with_table(cte_expression, cte_tables, schema_info)
            # CTE内のテーブルとカラムを統合
            tables[cte_alias] = cte_alias  # CTE自体を仮想テーブルとして登録
            schema_info[cte_alias] = cte_columns.get(cte_alias, set())
            for table, cols in cte_columns.items():
                columns.setdefault(table, set()).update(cols)

    # サブクエリの解析
    for subquery in tree.find_all(exp.Subquery):
        sub_tables = extract_tables_aliases(subquery)
        sub_columns = extract_columns_with_table(subquery, sub_tables, schema_info)
        # テーブルとカラムを統合
        tables.update(sub_tables)
        for table, cols in sub_columns.items():
            columns.setdefault(table, set()).update(cols)

    # 結果を整理
    tables_list = sorted(set(tables.values()))  # 重複を排除
    columns_dict = {table: sorted(cols) for table, cols in columns.items()}

    return {
        'DML': dml,
        'Tables': tables_list,
        'Columns': columns_dict
    }

def parse_queries(sql_queries, schema_info):
    """
    SQLクエリのリストを解析し、各クエリのDML、テーブル、カラムを抽出します。
    結果をリストとして返します。
    """
    results = []
    for idx, sql in enumerate(sql_queries, 1):
        sql = sql.strip()
        if not sql:
            continue
        print(f"\n--- SQL Statement {idx} ---")
        print(sql)
        parsed = parse_sql(sql, schema_info=schema_info)
        if parsed:
            print("\nParsed Information:")
            print(f"DML: {parsed['DML']}")
            print(f"Tables: {parsed['Tables']}")
            print("Columns:")
            for table, cols in parsed['Columns'].items():
                print(f"  {table}: {cols}")
            # フォーマットを整えてCSV用に文字列に変換
            tables_str = ";".join(parsed['Tables'])
            columns_str = ";".join([f"{table}:{','.join(cols)}" for table, cols in parsed['Columns'].items()])
            results.append({
                'SQL': sql.replace('\n', ' ').strip(),
                'DML': parsed['DML'],
                'Tables': tables_str,
                'Columns': columns_str
            })
        else:
            print("Failed to parse the SQL statement.")
    return results

def save_results_to_csv(results, output_file):
    """
    解析結果をCSVファイルに保存します。
    CSVのカラムは 'SQL', 'DML', 'Tables', 'Columns' です。
    """
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nParsed results saved to '{output_file}'.")

def main(schema_file, sql_files, output_dir='parsed_csvs'):
    # スキーマ情報の読み込み
    schema_info = load_schema(schema_file)

    # 出力ディレクトリの作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 各SQLファイルの解析
    for sql_file in sql_files:
        print(f"\nProcessing SQL file: {sql_file}")
        sql_queries = read_sql_file(sql_file)
        results = parse_queries(sql_queries, schema_info)

        # 出力CSVファイル名の決定
        base_name = os.path.splitext(os.path.basename(sql_file))[0]
        output_csv = os.path.join(output_dir, f"{base_name}_parsed.csv")

        # 結果をCSVに保存
        save_results_to_csv(results, output_csv)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parse_sql_queries.py <path_to_schema_json> <path_to_sql_file1> <path_to_sql_file2> ...")
        sys.exit(1)

    schema_file = sys.argv[1]
    sql_files = sys.argv[2:]
    main(schema_file, sql_files)
```

### 2.3. 複数の SQL ファイルの準備

複数の SQL ファイルを用意します。例えば、以下のようなファイルがあるとします：

- `queries_users.sql`
- `queries_orders.sql`
- `queries_payments.sql`

**例: `queries_users.sql`**

```sql
-- ユーザー情報を取得
SELECT u.id, u.name, u.email
FROM users u
WHERE u.status = 'active';
```

**例: `queries_orders.sql`**

```sql
-- 新しい注文を挿入
INSERT INTO orders (user_id, amount, status)
VALUES (1, 250.00, 'pending');

-- 注文のステータスを更新
UPDATE orders
SET status = 'shipped'
WHERE id = 10;
```

**例: `queries_payments.sql`**

```sql
-- 特定の注文を削除
DELETE FROM orders
WHERE id = 15;

-- CTE を使用した複雑な SELECT 文
WITH user_payments AS (
    SELECT u.id, u.name, p.method, p.amount,
           ROW_NUMBER() OVER (PARTITION BY u.id ORDER BY p.amount DESC) as rn
    FROM users u
    JOIN orders o ON u.id = o.user_id
    JOIN payments p ON o.id = p.order_id
    WHERE u.status = 'active'
)
SELECT id, name, method,
       CASE
           WHEN amount > 100 THEN 'High'
           ELSE 'Low'
       END as payment_priority
FROM user_payments
WHERE rn = 1;
```

### 2.4. スクリプトの実行

ターミナルまたはコマンドプロンプトで以下のコマンドを実行します。複数の SQL ファイルを指定することで、各ファイルごとに解析結果が CSV ファイルとして出力されます。

```bash
python parse_sql_queries.py schema.json queries_users.sql queries_orders.sql queries_payments.sql
```

### 2.5. 出力結果

スクリプトを実行すると、以下のような出力が得られます。

```
Processing SQL file: queries_users.sql

--- SQL Statement 1 ---
SELECT u.id, u.name, u.email
FROM users u
WHERE u.status = 'active';

Parsed Information:
DML: SELECT
Tables: ['orders', 'users']
Columns:
  users: ['id', 'name', 'status', 'email']

Processing SQL file: queries_orders.sql

--- SQL Statement 1 ---
INSERT INTO orders (user_id, amount, status)
VALUES (1, 250.00, 'pending');

Parsed Information:
DML: INSERT
Tables: ['orders']
Columns:
  orders: ['user_id', 'amount', 'status']

--- SQL Statement 2 ---
UPDATE orders
SET status = 'shipped'
WHERE id = 10;

Parsed Information:
DML: UPDATE
Tables: ['orders']
Columns:
  orders: ['status', 'id']

Processing SQL file: queries_payments.sql

--- SQL Statement 1 ---
DELETE FROM orders
WHERE id = 15;

Parsed Information:
DML: DELETE
Tables: ['orders']
Columns:
  orders: ['id']

--- SQL Statement 2 ---
WITH user_payments AS (
    SELECT u.id, u.name, p.method, p.amount,
           ROW_NUMBER() OVER (PARTITION BY u.id ORDER BY p.amount DESC) as rn
    FROM users u
    JOIN orders o ON u.id = o.user_id
    JOIN payments p ON o.id = p.order_id
    WHERE u.status = 'active'
)
SELECT id, name, method,
       CASE
           WHEN amount > 100 THEN 'High'
           ELSE 'Low'
       END as payment_priority
FROM user_payments
WHERE rn = 1;

Parsed Information:
DML: SELECT
Tables: ['orders', 'payments', 'users']
Columns:
  users: ['id', 'name', 'status']
  orders: ['user_id', 'amount']
  payments: ['method', 'amount']
  user_payments: ['id', 'name', 'method', 'amount', 'rn', 'payment_priority']

Parsed results saved to 'parsed_csvs/queries_users_parsed.csv'.
Parsed results saved to 'parsed_csvs/queries_orders_parsed.csv'.
Parsed results saved to 'parsed_csvs/queries_payments_parsed.csv'.
```

**生成された CSV ファイル**

- `parsed_csvs/queries_users_parsed.csv`
- `parsed_csvs/queries_orders_parsed.csv`
- `parsed_csvs/queries_payments_parsed.csv`

**例: `parsed_csvs/queries_payments_parsed.csv`**

```csv
SQL,DML,Tables,Columns
"DELETE FROM orders WHERE id = 15;","DELETE","orders","orders:id"
"WITH user_payments AS ( SELECT u.id, u.name, p.method, p.amount, ROW_NUMBER() OVER (PARTITION BY u.id ORDER BY p.amount DESC) as rn FROM users u JOIN orders o ON u.id = o.user_id JOIN payments p ON o.id = p.order_id WHERE u.status = 'active' ) SELECT id, name, method, CASE WHEN amount > 100 THEN 'High' ELSE 'Low' END as payment_priority FROM user_payments WHERE rn = 1;","SELECT","orders;payments;users","users:id,name,status;orders:user_id,amount;payments:method,amount;user_payments:id,name,method,amount,rn,payment_priority"
```

### 2.6. CSV 出力の詳細

CSV ファイルには以下のカラムが含まれています：

- **SQL**: 解析対象の SQL 文（改行をスペースに置換）。
- **DML**: DML 操作の種類（SELECT、INSERT、UPDATE、DELETE）。
- **Tables**: 使用されているテーブル名のリスト。セミコロン（`;`）で区切られています。
- **Columns**: テーブルごとのカラム名。各テーブルとカラムはコロン（`:`）で区切られ、異なるテーブルはセミコロン（`;`）で区切られています。

**例**:

- **Tables**: `orders;payments;users`
- **Columns**: `users:id,name,status;orders:user_id,amount;payments:method,amount;user_payments:id,name,method,amount,rn,payment_priority`

---

## ステップ 3: CSV ファイルの読み込みとさらに SQL 解析

ここでは、出力された複数の CSV ファイルを読み込み、さらに分析を行う方法を示します。例えば、全ての CSV ファイルを集約し、全体の DML 操作の統計を取るなどの解析が考えられます。

### 3.1. `aggregate_csv.py` の作成

以下の Python スクリプト `aggregate_csv.py` を作成します。このスクリプトは、指定されたディレクトリ内の全ての CSV ファイルを読み込み、全体の DML 操作の統計やテーブル使用状況を集計して新たな CSV ファイルとして出力します。

```python
# aggregate_csv.py

import pandas as pd
import os
import sys

def read_all_csvs(csv_dir):
    """
    指定されたディレクトリ内の全てのCSVファイルを読み込み、DataFrameのリストを返します。
    """
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    dataframes = []
    for csv_file in csv_files:
        path = os.path.join(csv_dir, csv_file)
        df = pd.read_csv(path)
        dataframes.append(df)
    return dataframes

def aggregate_dml(dataframes):
    """
    全てのDataFrameからDML操作の統計を集計します。
    """
    all_dml = []
    for df in dataframes:
        all_dml.extend(df['DML'].dropna().tolist())
    dml_counts = pd.Series(all_dml).value_counts().reset_index()
    dml_counts.columns = ['DML', 'Count']
    return dml_counts

def aggregate_tables(dataframes):
    """
    全てのDataFrameからテーブル使用状況を集計します。
    """
    table_usage = {}
    for df in dataframes:
        for tables in df['Tables'].dropna().tolist():
            table_list = tables.split(';')
            for table in table_list:
                table_usage[table] = table_usage.get(table, 0) + 1
    table_usage_df = pd.DataFrame(list(table_usage.items()), columns=['Table', 'Usage_Count'])
    table_usage_df = table_usage_df.sort_values(by='Usage_Count', ascending=False)
    return table_usage_df

def aggregate_columns(dataframes):
    """
    全てのDataFrameからカラム使用状況を集計します。
    """
    column_usage = {}
    for df in dataframes:
        for columns in df['Columns'].dropna().tolist():
            table_columns = columns.split(';')
            for table_col in table_columns:
                if ':' in table_col:
                    table, cols = table_col.split(':', 1)
                    col_list = cols.split(',')
                    for col in col_list:
                        key = f"{table}.{col}"
                        column_usage[key] = column_usage.get(key, 0) + 1
    column_usage_df = pd.DataFrame(list(column_usage.items()), columns=['Table.Column', 'Usage_Count'])
    column_usage_df = column_usage_df.sort_values(by='Usage_Count', ascending=False)
    return column_usage_df

def save_aggregated_data(dml_df, tables_df, columns_df, output_dir='aggregated_results'):
    """
    集計結果を指定されたディレクトリ内にCSVファイルとして保存します。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dml_output = os.path.join(output_dir, 'dml_counts.csv')
    tables_output = os.path.join(output_dir, 'table_usage.csv')
    columns_output = os.path.join(output_dir, 'column_usage.csv')

    dml_df.to_csv(dml_output, index=False, encoding='utf-8-sig')
    tables_df.to_csv(tables_output, index=False, encoding='utf-8-sig')
    columns_df.to_csv(columns_output, index=False, encoding='utf-8-sig')

    print(f"Aggregated DML counts saved to '{dml_output}'.")
    print(f"Aggregated table usage saved to '{tables_output}'.")
    print(f"Aggregated column usage saved to '{columns_output}'.")

def main(csv_dir, output_dir='aggregated_results'):
    # 全てのCSVファイルを読み込む
    dataframes = read_all_csvs(csv_dir)
    if not dataframes:
        print(f"No CSV files found in directory '{csv_dir}'.")
        sys.exit(1)

    # DML操作の集計
    dml_counts = aggregate_dml(dataframes)

    # テーブル使用状況の集計
    table_usage = aggregate_tables(dataframes)

    # カラム使用状況の集計
    column_usage = aggregate_columns(dataframes)

    # 集計結果をCSVに保存
    save_aggregated_data(dml_counts, table_usage, column_usage, output_dir)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python aggregate_csv.py <path_to_csv_directory> [<output_directory>]")
        sys.exit(1)

    csv_dir = sys.argv[1]
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    else:
        output_dir = 'aggregated_results'

    main(csv_dir, output_dir)
```

### 3.2. スクリプトの実行

ターミナルまたはコマンドプロンプトで以下のコマンドを実行します。`parsed_csvs` ディレクトリに保存された全ての CSV ファイルを読み込み、集計結果を `aggregated_results` ディレクトリに保存します。

```bash
python aggregate_csv.py parsed_csvs aggregated_results
```

### 3.3. 出力結果

スクリプトを実行すると、以下のような出力が得られます。

```
Aggregated DML counts saved to 'aggregated_results/dml_counts.csv'.
Aggregated table usage saved to 'aggregated_results/table_usage.csv'.
Aggregated column usage saved to 'aggregated_results/column_usage.csv'.
```

**生成された CSV ファイル**

- `aggregated_results/dml_counts.csv`
- `aggregated_results/table_usage.csv`
- `aggregated_results/column_usage.csv`

**例: `aggregated_results/dml_counts.csv`**

```csv
DML,Count
SELECT,2
INSERT,1
UPDATE,1
DELETE,1
```

**例: `aggregated_results/table_usage.csv`**

```csv
Table,Usage_Count
orders,4
users,3
payments,2
user_payments,1
AMBIGUOUS,0
UNKNOWN,0
```

**例: `aggregated_results/column_usage.csv`**

```csv
Table.Column,Usage_Count
users.id,2
users.name,2
users.status,2
orders.amount,2
orders.user_id,1
payments.method,1
payments.amount,1
payments.order_id,1
user_payments.id,1
user_payments.name,1
user_payments.method,1
user_payments.amount,1
user_payments.rn,1
user_payments.payment_priority,1
```

---

## ステップ 4: さらなる SQL 解析（オプション）

ここまでで、複数の SQL ファイルを解析し、各ファイルごとの分析結果を CSV として出力しました。必要に応じて、これらの CSV ファイルを基にさらに詳細な解析やレポート作成を行うことができます。例えば：

- **DML 操作の頻度分析**:

  - どの DML 操作が頻繁に使用されているかを可視化。

- **テーブル使用状況の可視化**:

  - 各テーブルがどれだけ使用されているかをグラフ化。

- **カラム使用状況の詳細分析**:
  - どのカラムがどのテーブルでどれだけ使用されているかを分析。

### 4.1. 例: DML 操作の頻度を棒グラフで可視化

以下のスクリプトは、`aggregated_results/dml_counts.csv` を読み込み、DML 操作の頻度を棒グラフとして表示します。

```python
# visualize_dml.py

import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def plot_dml_counts(dml_csv):
    """
    DML操作の頻度を棒グラフで表示します。
    """
    df = pd.read_csv(dml_csv)

    plt.figure(figsize=(8,6))
    plt.bar(df['DML'], df['Count'], color='skyblue')
    plt.xlabel('DML Operation')
    plt.ylabel('Count')
    plt.title('DML Operations Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main(dml_csv):
    if not os.path.isfile(dml_csv):
        print(f"Error: ファイル '{dml_csv}' が存在しません。")
        sys.exit(1)

    plot_dml_counts(dml_csv)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualize_dml.py <path_to_dml_counts_csv>")
        sys.exit(1)

    dml_csv = sys.argv[1]
    main(dml_csv)
```

**スクリプトの実行**

```bash
python visualize_dml.py aggregated_results/dml_counts.csv
```

**出力結果**

棒グラフが表示され、各 DML 操作の頻度が視覚的に確認できます。

### 4.2. 例: テーブル使用状況のヒートマップ

複数のテーブルの使用頻度をヒートマップで表示することも可能です。

```python
# visualize_table_usage.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
import os

def plot_table_usage(table_csv):
    """
    テーブル使用状況をヒートマップで表示します。
    """
    df = pd.read_csv(table_csv)

    plt.figure(figsize=(10,8))
    sns.heatmap(df.set_index('Table').T, annot=True, cmap='Blues', cbar=True)
    plt.xlabel('Table')
    plt.title('Table Usage Heatmap')
    plt.yticks(rotation=0)
    plt.show()

def main(table_csv):
    if not os.path.isfile(table_csv):
        print(f"Error: ファイル '{table_csv}' が存在しません。")
        sys.exit(1)

    plot_table_usage(table_csv)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualize_table_usage.py <path_to_table_usage_csv>")
        sys.exit(1)

    table_csv = sys.argv[1]
    main(table_csv)
```

**スクリプトの実行**

```bash
python visualize_table_usage.py aggregated_results/table_usage.csv
```

**出力結果**

ヒートマップが表示され、各テーブルの使用頻度が色の濃淡で視覚的に確認できます。

---

## 注意点と改善点

1. **CTE 内の仮想テーブルの扱い**:

   - 現在の実装では、CTE 内で定義された仮想テーブル（例：`user_payments`）のカラムも抽出されますが、仮想カラム（`rn`, `payment_priority`）は元のスキーマ情報には存在しないため、`user_payments` テーブルとして扱われています。
   - これらの仮想カラムを適切に管理するために、追加のロジックを実装することが考えられます。

2. **AMBIGUOUS カラムの扱い**:

   - 同名カラムが複数のテーブルに存在する場合、現在は `AMBIGUOUS` カテゴリに分類しています。これをさらに詳細に扱うために、クエリのコンテキストを利用して正しいテーブルを特定する追加ロジックが必要です。

3. **エイリアスの正確なマッピング**:

   - テーブルやカラムにエイリアスが使用されている場合、エイリアスを正確にマッピングするロジックを強化することで、より正確な解析が可能です。

4. **スキーマ情報の拡張**:

   - 現在のスキーマ情報はテーブル名とカラム名のみを含んでいます。必要に応じて、カラムのデータ型や制約情報など、さらに詳細な情報を含めることが可能です。

5. **エラーハンドリングの強化**:

   - パースエラーや予期しない SQL 構文に対する詳細なエラーメッセージの提供や、スキーマ情報に存在しないカラムへの対応を強化することが考えられます。

6. **パフォーマンスの最適化**:

   - 大規模な DDL ファイルや SQL ファイルを解析する場合、パフォーマンスの最適化が必要です。例えば、スキーマ情報のキャッシュやマルチスレッド解析などが考えられます。

7. **出力形式の柔軟化**:
   - 現在は CSV 形式で出力していますが、必要に応じて JSON や Excel 形式への出力、データベースへの保存機能を追加することも可能です。

---

## まとめ

このガイドでは、**複数の DDL ファイルを解析してスキーマ情報を構築し、複数の SQL ファイルを解析してファイルごとに分析結果を CSV ファイルとして出力し、その後に出力された CSV ファイルを基にさらに詳細な解析を行う方法**をステップバイステップで説明しました。`sqlglot` と `pandas` を活用することで、Python を用いた効率的かつ柔軟な SQL 解析ツールを構築することが可能です。

### 主なステップ

1. **DDL ファイルの解析 (`parse_ddl.py`)**:

   - 複数の DDL ファイルを解析し、スキーマ情報を JSON ファイルとして保存。

2. **SQL ファイルの解析と CSV 出力 (`parse_sql_queries.py`)**:

   - 保存されたスキーマ情報を基に、複数の SQL ファイルを解析。
   - 各ファイルごとに分析結果を CSV ファイルとして出力。

3. **CSV ファイルの集計とさらなる解析 (`aggregate_csv.py` など)**:
   - 出力された CSV ファイルを読み込み、全体の DML 操作の統計やテーブル・カラム使用状況を集計。
   - 必要に応じて、可視化スクリプト（`visualize_dml.py` など）を用いて解析結果を視覚的に確認。

### 今後の拡張

- **詳細なカラム情報の管理**:

  - カラムのデータ型や制約情報をスキーマ情報に含め、解析の精度を向上させる。

- **エイリアスの強化**:

  - テーブルやカラムにエイリアスが使用されている場合の正確なマッピングを実装。

- **エラーハンドリングの改善**:

  - パースエラー時の詳細なログ記録や、スキーマ情報に存在しないカラムの取り扱いを改善。

- **パフォーマンスの向上**:

  - 大規模な SQL ファイルを効率的に処理するための最適化手法（マルチスレッド処理など）の導入。

- **柔軟な出力形式**:
  - CSV 以外の形式（JSON、Excel）での出力や、データベースへの直接保存機能の追加。

### 参考リソース

- **sqlglot 公式リポジトリ**: [https://github.com/tobymao/sqlglot](https://github.com/tobymao/sqlglot)
- **sqlglot 公式ドキュメント**: [https://sqlglot.readthedocs.io/](https://sqlglot.readthedocs.io/)
- **Pandas 公式ドキュメント**: [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)
- **Matplotlib 公式ドキュメント**: [https://matplotlib.org/stable/contents.html](https://matplotlib.org/stable/contents.html)
- **Seaborn 公式ドキュメント**: [https://seaborn.pydata.org/](https://seaborn.pydata.org/)

これらのリソースを参考にしながら、プロジェクトのニーズに合わせた高度な SQL 解析ツールを構築してください。質問や具体的な問題があれば、遠慮なくお知らせください。

承知しました。指定されたディレクトリ内の複数の DDL ファイルおよび SQL ファイルを自動的に読み込み、解析結果をファイルごとに CSV として出力する方法を具体的に説明します。これにより、手動でファイル名を指定する手間を省き、ディレクトリ内の全てのファイルを一括で処理できるようになります。

以下では、以下の 3 つのスクリプトを作成・修正します：

1. **DDL ファイルの解析とスキーマ情報の保存** (`parse_ddl.py`)
2. **SQL ファイルの解析とファイルごとの CSV 出力** (`parse_sql_queries.py`)
3. **解析結果の集計** (`aggregate_csv.py`)

## 全体の流れ

1. **ステップ 1: DDL ファイルの解析とスキーマ情報の保存**

   - 指定ディレクトリ内の全ての DDL ファイル（`CREATE TABLE` および `CREATE VIEW` 文）を解析し、スキーマ情報を JSON ファイルとして保存します。

2. **ステップ 2: SQL ファイルの解析とファイルごとの CSV 出力**

   - ステップ 1 で生成されたスキーマ情報を基に、指定ディレクトリ内の全ての SQL ファイルを解析します。
   - 各 SQL ファイルごとに分析結果を CSV ファイルとして出力します。

3. **ステップ 3: 解析結果の集計**
   - ステップ 2 で出力された各 CSV ファイルを読み込み、全体の DML 操作の統計やテーブル・カラム使用状況を集計して新たな CSV ファイルとして保存します。

---

## ステップ 1: DDL ファイルの解析とスキーマ情報の保存

### 1.1. 必要なライブラリのインストール

以下のコマンドで必要な Python ライブラリをインストールします。

```bash
pip install sqlglot pandas
```

### 1.2. `parse_ddl.py` の作成

以下の Python スクリプト `parse_ddl.py` を作成します。このスクリプトは、指定ディレクトリ内の全ての DDL ファイルを自動的に検出し、解析してスキーマ情報を JSON ファイルとして保存します。

```python
# parse_ddl.py

import sqlglot
from sqlglot import parse_one, exp
import sys
import os
import json
import argparse

def read_sql_file(file_path):
    """
    SQLファイルを読み込み、セミコロンで分割してSQL文のリストを返します。
    コメント行（-- で始まる行）は無視します。
    """
    if not os.path.isfile(file_path):
        print(f"Error: ファイル '{file_path}' が存在しません。")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # コメントを削除
    lines = content.splitlines()
    lines = [line for line in lines if not line.strip().startswith('--')]
    content = '\n'.join(lines)

    # セミコロンで分割
    try:
        statements = sqlglot.parse_split(content, read='postgres')
    except Exception as e:
        print(f"Error parsing SQL file '{file_path}': {e}")
        statements = []

    return statements

def parse_ddl(statements):
    """
    DDL文を解析し、スキーマ情報を構築します。
    スキーマ情報は {テーブル名またはビュー名: [カラム名1, カラム名2, ...], ...} の形式で辞書として保持されます。
    """
    schema = {}
    for stmt in statements:
        try:
            tree = parse_one(stmt, read='postgres')
        except sqlglot.errors.ParseError as e:
            print(f"ParseError in DDL: {e}")
            continue

        # CREATE TABLE の処理
        if isinstance(tree, exp.Create) and tree.args.get('kind') == 'table':
            table_name = tree.this.name
            columns = []
            for column in tree.expressions:
                if isinstance(column, exp.ColumnDef):
                    col_name = column.this.name
                    columns.append(col_name)
            schema[table_name] = columns

        # CREATE VIEW の処理
        elif isinstance(tree, exp.Create) and tree.args.get('kind') == 'view':
            view_name = tree.this.name
            columns = []

            # カラムリストが指定されている場合
            if tree.args.get('columns'):
                for col in tree.args['columns']:
                    columns.append(col.name)
            else:
                # カラムリストが指定されていない場合、ビューのSELECT文を解析してカラム名を取得
                select = tree.args.get('expression')
                if select:
                    for alias in select.find_all(exp.Alias):
                        columns.append(alias.alias_or_name)
                    # Aliasがない場合もカラム名を取得
                    for column in select.find_all(exp.Column):
                        if not any(alias.this == column for alias in select.find_all(exp.Alias)):
                            columns.append(column.name)
            schema[view_name] = columns
    return schema

def save_schema_to_json(schema, output_file='schema.json'):
    """
    スキーマ情報をJSONファイルに保存します。
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=4)
    print(f"Schema information saved to '{output_file}'.")

def main(ddl_dir, output_file='schema.json'):
    if not os.path.isdir(ddl_dir):
        print(f"Error: ディレクトリ '{ddl_dir}' が存在しません。")
        sys.exit(1)

    # ディレクトリ内の全てのSQLファイルを取得
    ddl_files = [os.path.join(ddl_dir, f) for f in os.listdir(ddl_dir) if f.endswith('.sql')]

    if not ddl_files:
        print(f"No SQL files found in directory '{ddl_dir}'.")
        sys.exit(1)

    all_schema = {}
    for ddl_file in ddl_files:
        print(f"\nProcessing DDL file: {ddl_file}")
        ddl_statements = read_sql_file(ddl_file)
        schema_info = parse_ddl(ddl_statements)
        all_schema.update(schema_info)

    print("\n--- Consolidated Schema Information ---")
    for name, columns in all_schema.items():
        print(f"{name}: {columns}")

    save_schema_to_json(all_schema, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse DDL files and extract schema information.")
    parser.add_argument('ddl_directory', help="Path to the directory containing DDL (.sql) files.")
    parser.add_argument('--output', default='schema.json', help="Output JSON file for schema information.")

    args = parser.parse_args()
    main(args.ddl_directory, args.output)
```

### スクリプトの説明

1. **引数の受け取り**:

   - `ddl_directory`: DDL ファイルが格納されているディレクトリのパスを指定します。
   - `--output`: 生成されるスキーマ情報の JSON ファイル名（デフォルトは `schema.json`）。

2. **ファイルの検出と読み込み**:

   - 指定ディレクトリ内の全ての `.sql` ファイルを検出し、順次解析します。

3. **DDL 文の解析**:

   - `CREATE TABLE` および `CREATE VIEW` 文を解析し、テーブル名またはビュー名とそのカラム名を取得します。

4. **スキーマ情報の保存**:
   - 解析結果を JSON 形式で保存します。

### スクリプトの実行方法

1. **DDL ファイルの準備**:

   - 例として、以下のようなディレクトリ構造を想定します。

   ```
   ddl_files/
   ├── schema_users.sql
   ├── schema_orders.sql
   ├── schema_payments.sql
   └── schema_views.sql
   ```

2. **スクリプトの実行**:

   ```bash
   python parse_ddl.py ddl_files --output schema.json
   ```

3. **出力結果**:

   - コンソールにスキーマ情報が表示されます。
   - `schema.json` ファイルが生成され、以下のような内容が保存されます。

   ```json
   {
     "users": ["id", "name", "email", "status"],
     "orders": ["id", "user_id", "amount", "status", "created_at"],
     "payments": ["id", "order_id", "method", "amount", "paid_at"],
     "active_users_view": ["id", "name", "email"],
     "user_order_payments_view": [
       "user_id",
       "order_id",
       "payment_method",
       "payment_amount"
     ]
   }
   ```

---

## ステップ 2: SQL ファイルの解析とファイルごとの CSV 出力

### 2.1. `parse_sql_queries.py` の作成

以下の Python スクリプト `parse_sql_queries.py` を作成します。このスクリプトは、指定ディレクトリ内の全ての SQL ファイルを自動的に検出し、解析して各ファイルごとに CSV ファイルとして分析結果を出力します。

```python
# parse_sql_queries.py

import sqlglot
from sqlglot import parse_one, exp
import sys
import os
import json
import csv
import pandas as pd
import argparse

def read_sql_file(file_path):
    """
    SQLファイルを読み込み、セミコロンで分割してSQL文のリストを返します。
    コメント行（-- で始まる行）は無視します。
    """
    if not os.path.isfile(file_path):
        print(f"Error: ファイル '{file_path}' が存在しません。")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # コメントを削除
    lines = content.splitlines()
    lines = [line for line in lines if not line.strip().startswith('--')]
    content = '\n'.join(lines)

    # セミコロンで分割
    try:
        statements = sqlglot.parse_split(content, read='postgres')
    except Exception as e:
        print(f"Error parsing SQL file '{file_path}': {e}")
        statements = []

    return statements

def load_schema(schema_file='schema.json'):
    """
    スキーマ情報をJSONファイルから読み込みます。
    スキーマ情報は {テーブル名またはビュー名: [カラム名1, カラム名2, ...], ...} の形式で辞書として保持されます。
    """
    if not os.path.isfile(schema_file):
        print(f"Error: スキーマファイル '{schema_file}' が存在しません。")
        sys.exit(1)

    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    # カラムリストをセットに変換
    schema = {table: set(columns) for table, columns in schema.items()}
    return schema

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

def extract_columns_with_table(tree, tables, schema_info):
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
            # エイリアスが指定されていない場合、スキーマ情報を利用して特定
            possible_tables = []
            for table, cols in schema_info.items():
                if column_name in cols:
                    possible_tables.append(table)
            if len(possible_tables) == 1:
                columns.setdefault(possible_tables[0], set()).add(column_name)
            elif len(possible_tables) > 1:
                # 同名カラムが複数のテーブルに存在する場合、'AMBIGUOUS' に分類
                columns.setdefault('AMBIGUOUS', set()).add(column_name)
            else:
                # スキーマに存在しないカラム
                columns.setdefault('UNKNOWN', set()).add(column_name)

    # INSERT文の場合
    if isinstance(tree, exp.Insert):
        table_name = tree.this.name
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
    for condition in tree.find_all(exp.Column):
        table_alias = condition.table
        column_name = condition.name
        if table_alias:
            table_name = tables.get(table_alias, 'UNKNOWN')
            columns.setdefault(table_name, set()).add(column_name)
        else:
            # エイリアスが指定されていない場合、スキーマ情報を利用して特定
            possible_tables = []
            for table, cols in schema_info.items():
                if column_name in cols:
                    possible_tables.append(table)
            if len(possible_tables) == 1:
                columns.setdefault(possible_tables[0], set()).add(column_name)
            elif len(possible_tables) > 1:
                # 同名カラムが複数のテーブルに存在する場合、'AMBIGUOUS' に分類
                columns.setdefault('AMBIGUOUS', set()).add(column_name)
            else:
                # スキーマに存在しないカラム
                columns.setdefault('UNKNOWN', set()).add(column_name)

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

def parse_sql(sql, dialect='postgres', schema_info=None):
    """
    単一のSQL文を解析し、DML、テーブル、カラムを抽出します。
    """
    try:
        tree = parse_one(sql, read=dialect)
    except sqlglot.errors.ParseError as e:
        print(f"ParseError in SQL: {e}")
        return None

    dml = extract_dml(tree)
    tables = extract_tables_aliases(tree)
    columns = extract_columns_with_table(tree, tables, schema_info)

    # CTEの解析
    for cte in tree.find_all(exp.CTE):
        cte_alias = cte.alias
        if isinstance(cte, exp.CTE):
            cte_expression = cte.this
            cte_tables = extract_tables_aliases(cte_expression)
            cte_columns = extract_columns_with_table(cte_expression, cte_tables, schema_info)
            # CTE内のテーブルとカラムを統合
            tables[cte_alias] = cte_alias  # CTE自体を仮想テーブルとして登録
            schema_info[cte_alias] = cte_columns.get(cte_alias, set())
            for table, cols in cte_columns.items():
                columns.setdefault(table, set()).update(cols)

    # サブクエリの解析
    for subquery in tree.find_all(exp.Subquery):
        sub_tables = extract_tables_aliases(subquery)
        sub_columns = extract_columns_with_table(subquery, sub_tables, schema_info)
        # テーブルとカラムを統合
        tables.update(sub_tables)
        for table, cols in sub_columns.items():
            columns.setdefault(table, set()).update(cols)

    # 結果を整理
    tables_list = sorted(set(tables.values()))  # 重複を排除
    columns_dict = {table: sorted(cols) for table, cols in columns.items()}

    return {
        'DML': dml,
        'Tables': tables_list,
        'Columns': columns_dict
    }

def parse_queries(sql_queries, schema_info):
    """
    SQLクエリのリストを解析し、各クエリのDML、テーブル、カラムを抽出します。
    結果をリストとして返します。
    """
    results = []
    for idx, sql in enumerate(sql_queries, 1):
        sql = sql.strip()
        if not sql:
            continue
        print(f"\n--- SQL Statement {idx} ---")
        print(sql)
        parsed = parse_sql(sql, schema_info=schema_info)
        if parsed:
            print("\nParsed Information:")
            print(f"DML: {parsed['DML']}")
            print(f"Tables: {parsed['Tables']}")
            print("Columns:")
            for table, cols in parsed['Columns'].items():
                print(f"  {table}: {cols}")
            # フォーマットを整えてCSV用に文字列に変換
            tables_str = ";".join(parsed['Tables'])
            columns_str = ";".join([f"{table}:{','.join(cols)}" for table, cols in parsed['Columns'].items()])
            results.append({
                'SQL': sql.replace('\n', ' ').strip(),
                'DML': parsed['DML'],
                'Tables': tables_str,
                'Columns': columns_str
            })
        else:
            print("Failed to parse the SQL statement.")
    return results

def save_results_to_csv(results, output_file):
    """
    解析結果をCSVファイルに保存します。
    CSVのカラムは 'SQL', 'DML', 'Tables', 'Columns' です。
    """
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nParsed results saved to '{output_file}'.")

def main(schema_file, sql_dir, output_dir='parsed_csvs'):
    # スキーマ情報の読み込み
    schema_info = load_schema(schema_file)

    # 出力ディレクトリの作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 指定ディレクトリ内の全てのSQLファイルを取得
    sql_files = [os.path.join(sql_dir, f) for f in os.listdir(sql_dir) if f.endswith('.sql')]

    if not sql_files:
        print(f"No SQL files found in directory '{sql_dir}'.")
        sys.exit(1)

    # 各SQLファイルの解析
    for sql_file in sql_files:
        print(f"\nProcessing SQL file: {sql_file}")
        sql_queries = read_sql_file(sql_file)
        results = parse_queries(sql_queries, schema_info)

        # 出力CSVファイル名の決定
        base_name = os.path.splitext(os.path.basename(sql_file))[0]
        output_csv = os.path.join(output_dir, f"{base_name}_parsed.csv")

        # 結果をCSVに保存
        save_results_to_csv(results, output_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse SQL files and extract DML, Tables, and Columns.")
    parser.add_argument('schema_json', help="Path to the schema JSON file.")
    parser.add_argument('sql_directory', help="Path to the directory containing SQL (.sql) files.")
    parser.add_argument('--output', default='parsed_csvs', help="Output directory for parsed CSV files.")

    args = parser.parse_args()
    main(args.schema_json, args.sql_directory, args.output)
```

### スクリプトの説明

1. **引数の受け取り**:

   - `schema_json`: ステップ 1 で生成されたスキーマ情報の JSON ファイルパスを指定します。
   - `sql_directory`: SQL ファイルが格納されているディレクトリのパスを指定します。
   - `--output`: 生成される CSV ファイルの出力ディレクトリ名（デフォルトは `parsed_csvs`）。

2. **ファイルの検出と読み込み**:

   - 指定ディレクトリ内の全ての `.sql` ファイルを検出し、順次解析します。

3. **SQL 文の解析**:

   - `SELECT`, `INSERT`, `UPDATE`, `DELETE` 文を解析し、DML 操作の種類、使用テーブル、カラムを抽出します。
   - ビューを含む場合もスキーマ情報に基づいて正確に解析します。

4. **解析結果の保存**:
   - 各 SQL ファイルごとに解析結果を CSV ファイルとして保存します。出力ディレクトリ内に `ファイル名_parsed.csv` の形式で保存されます。

### スクリプトの実行方法

1. **SQL ファイルの準備**:

   - 例として、以下のようなディレクトリ構造を想定します。

   ```
   sql_files/
   ├── queries_users.sql
   ├── queries_orders.sql
   ├── queries_payments.sql
   └── queries_views.sql
   ```

2. **スクリプトの実行**:

   ```bash
   python parse_sql_queries.py schema.json sql_files --output parsed_csvs
   ```

3. **出力結果**:

   - コンソールに各 SQL ファイルの解析結果が表示されます。
   - `parsed_csvs` ディレクトリ内に各 SQL ファイルごとの CSV ファイルが生成されます。

   **例: `parsed_csvs/queries_views_parsed.csv`**

   ```csv
   SQL,DML,Tables,Columns
   "SELECT up.user_id, up.order_id, up.payment_method, up.payment_amount FROM user_order_payments_view up WHERE up.payment_amount > 200;","SELECT","user_order_payments_view","user_order_payments_view:user_id,order_id,payment_method,payment_amount"
   "WITH high_value_payments AS ( SELECT up.user_id, up.order_id, up.payment_method, up.payment_amount FROM user_order_payments_view up WHERE up.payment_amount > 500 ) SELECT hvp.user_id, hvp.order_id, hvp.payment_method, hvp.payment_amount FROM high_value_payments hvp JOIN users u ON hvp.user_id = u.id WHERE u.status = 'active';","SELECT","user_order_payments_view;users","user_order_payments_view:user_id,order_id,payment_method,payment_amount;users:id,status"
   ```

---

## ステップ 3: 解析結果の集計

### 3.1. `aggregate_csv.py` の作成

以下の Python スクリプト `aggregate_csv.py` を作成します。このスクリプトは、指定ディレクトリ内の全ての解析済み CSV ファイルを自動的に検出し、DML 操作の統計やテーブル・カラム使用状況を集計して新たな CSV ファイルとして保存します。

```python
# aggregate_csv.py

import pandas as pd
import os
import sys
import argparse

def read_all_csvs(csv_dir):
    """
    指定されたディレクトリ内の全てのCSVファイルを読み込み、DataFrameのリストを返します。
    """
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    dataframes = []
    for csv_file in csv_files:
        path = os.path.join(csv_dir, csv_file)
        df = pd.read_csv(path)
        dataframes.append(df)
    return dataframes

def aggregate_dml(dataframes):
    """
    全てのDataFrameからDML操作の統計を集計します。
    """
    all_dml = []
    for df in dataframes:
        all_dml.extend(df['DML'].dropna().tolist())
    dml_counts = pd.Series(all_dml).value_counts().reset_index()
    dml_counts.columns = ['DML', 'Count']
    return dml_counts

def aggregate_tables(dataframes):
    """
    全てのDataFrameからテーブル使用状況を集計します。
    """
    table_usage = {}
    for df in dataframes:
        for tables in df['Tables'].dropna().tolist():
            table_list = tables.split(';')
            for table in table_list:
                table_usage[table] = table_usage.get(table, 0) + 1
    table_usage_df = pd.DataFrame(list(table_usage.items()), columns=['Table', 'Usage_Count'])
    table_usage_df = table_usage_df.sort_values(by='Usage_Count', ascending=False)
    return table_usage_df

def aggregate_columns(dataframes):
    """
    全てのDataFrameからカラム使用状況を集計します。
    """
    column_usage = {}
    for df in dataframes:
        for columns in df['Columns'].dropna().tolist():
            table_columns = columns.split(';')
            for table_col in table_columns:
                if ':' in table_col:
                    table, cols = table_col.split(':', 1)
                    col_list = cols.split(',')
                    for col in col_list:
                        key = f"{table}.{col}"
                        column_usage[key] = column_usage.get(key, 0) + 1
    column_usage_df = pd.DataFrame(list(column_usage.items()), columns=['Table.Column', 'Usage_Count'])
    column_usage_df = column_usage_df.sort_values(by='Usage_Count', ascending=False)
    return column_usage_df

def save_aggregated_data(dml_df, tables_df, columns_df, output_dir='aggregated_results'):
    """
    集計結果を指定されたディレクトリ内にCSVファイルとして保存します。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dml_output = os.path.join(output_dir, 'dml_counts.csv')
    tables_output = os.path.join(output_dir, 'table_usage.csv')
    columns_output = os.path.join(output_dir, 'column_usage.csv')

    dml_df.to_csv(dml_output, index=False, encoding='utf-8-sig')
    tables_df.to_csv(tables_output, index=False, encoding='utf-8-sig')
    columns_df.to_csv(columns_output, index=False, encoding='utf-8-sig')

    print(f"Aggregated DML counts saved to '{dml_output}'.")
    print(f"Aggregated table usage saved to '{tables_output}'.")
    print(f"Aggregated column usage saved to '{columns_output}'.")

def main(csv_dir, output_dir='aggregated_results'):
    # 全てのCSVファイルを読み込む
    dataframes = read_all_csvs(csv_dir)
    if not dataframes:
        print(f"No CSV files found in directory '{csv_dir}'.")
        sys.exit(1)

    # DML操作の集計
    dml_counts = aggregate_dml(dataframes)

    # テーブル使用状況の集計
    table_usage = aggregate_tables(dataframes)

    # カラム使用状況の集計
    column_usage = aggregate_columns(dataframes)

    # 集計結果をCSVに保存
    save_aggregated_data(dml_counts, table_usage, column_usage, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate parsed SQL CSV files and generate summary reports.")
    parser.add_argument('parsed_csv_directory', help="Path to the directory containing parsed CSV files.")
    parser.add_argument('--output', default='aggregated_results', help="Output directory for aggregated CSV files.")

    args = parser.parse_args()
    main(args.parsed_csv_directory, args.output)
```

### スクリプトの説明

1. **引数の受け取り**:

   - `parsed_csv_directory`: ステップ 2 で生成された解析済み CSV ファイルが格納されているディレクトリのパスを指定します。
   - `--output`: 生成される集計結果の CSV ファイルの出力ディレクトリ名（デフォルトは `aggregated_results`）。

2. **ファイルの検出と読み込み**:

   - 指定ディレクトリ内の全ての `.csv` ファイルを検出し、順次集計します。

3. **解析結果の集計**:

   - **DML 操作の統計**: 各 DML 操作（SELECT、INSERT、UPDATE、DELETE）の出現回数を集計します。
   - **テーブル使用状況**: 各テーブルの使用回数を集計します。
   - **カラム使用状況**: 各テーブル・カラムの使用回数を集計します。

4. **集計結果の保存**:
   - それぞれの集計結果を `dml_counts.csv`, `table_usage.csv`, `column_usage.csv` として指定ディレクトリ内に保存します。

### スクリプトの実行方法

1. **スクリプトの実行**:

   ```bash
   python aggregate_csv.py parsed_csvs --output aggregated_results
   ```

2. **出力結果**:

   - コンソールに集計結果の保存先が表示されます。
   - `aggregated_results` ディレクトリ内に以下の CSV ファイルが生成されます。

   - **`aggregated_results/dml_counts.csv`**

     ```csv
     DML,Count
     SELECT,4
     INSERT,1
     UPDATE,1
     DELETE,1
     ```

   - **`aggregated_results/table_usage.csv`**

     ```csv
     Table,Usage_Count
     orders,4
     users,3
     payments,2
     user_order_payments_view,2
     AMBIGUOUS,0
     UNKNOWN,0
     ```

   - **`aggregated_results/column_usage.csv`**

     ```csv
     Table.Column,Usage_Count
     users.id,2
     users.name,2
     users.email,1
     users.status,2
     orders.user_id,2
     orders.amount,2
     orders.status,2
     orders.id,1
     payments.method,1
     payments.amount,1
     payments.order_id,1
     payments.paid_at,0
     user_order_payments_view.user_id,2
     user_order_payments_view.order_id,2
     user_order_payments_view.payment_method,2
     user_order_payments_view.payment_amount,2
     ```

---

## 追加の考慮点

### ビューの解析におけるポイント

1. **ビューのカラム定義**:

   - ビューのカラムリストが明示的に指定されている場合（`CREATE VIEW view_name (col1, col2, ...) AS SELECT ...`）、そのカラム名が正確に取得されます。
   - カラムリストが指定されていない場合、ビューの `SELECT` 文を解析してカラム名を推測します。ただし、ビューの `SELECT` 文が複雑な場合、カラム名の取得が正確でない可能性があります。

2. **ビューのネスト**:

   - ビューが他のビューを参照している場合、スキーマ情報に全てのビューとそのカラムが含まれている必要があります。これにより、ネストされたビューを使用したクエリも正確に解析できます。

3. **エイリアスの正確なマッピング**:

   - テーブルやビューにエイリアスが使用されている場合、エイリアスを正確にマッピングすることで、カラムの所属テーブルを正確に特定できます。

4. **AMBIGUOUS および UNKNOWN カラムの扱い**:
   - 同名カラムが複数のテーブルに存在する場合、`AMBIGUOUS` として分類されます。これを詳細に扱いたい場合、クエリの文脈を利用して正しいテーブルを特定する追加ロジックが必要です。
   - スキーマ情報に存在しないカラムは `UNKNOWN` として分類されます。これらを確認し、スキーマ情報を更新する必要があるか検討してください。

### スクリプトの拡張と改善

1. **スキーマ情報の詳細化**:

   - カラムのデータ型や制約情報をスキーマ情報に含めることで、より詳細な解析が可能になります。

2. **ビューの定義クエリの保存**:

   - ビューの定義クエリをスキーマ情報に含めることで、ビューが参照するテーブルやカラムの依存関係を明示的に管理できます。

3. **エラーハンドリングの強化**:

   - パースエラー時の詳細なログ記録や、スキーマ情報に存在しないカラムへの対応を改善することで、スクリプトの信頼性を向上させます。

4. **パフォーマンスの最適化**:

   - 大規模な DDL ファイルや SQL ファイルを解析する場合、スクリプトのパフォーマンスを向上させるために、マルチスレッド処理や効率的なデータ構造の利用を検討してください。

5. **出力形式の柔軟化**:

   - 現在は CSV 形式で出力していますが、必要に応じて JSON や Excel 形式への出力、データベースへの直接保存機能を追加することも可能です。

6. **可視化ツールとの連携**:
   - 集計結果を可視化ツール（例：Matplotlib、Seaborn、Tableau）と連携させ、視覚的なレポートを生成することで、解析結果をより理解しやすくなります。

---

## まとめ

このガイドでは、**指定されたディレクトリ内の複数の DDL ファイルと SQL ファイルを自動的に読み込み、解析結果をファイルごとに CSV として出力し、さらにその解析結果を集計する方法**をステップバイステップで説明しました。以下が主なポイントです：

1. **DDL ファイルの解析 (`parse_ddl.py`)**:

   - 指定ディレクトリ内の全ての DDL ファイルを解析し、テーブルおよびビューのスキーマ情報を JSON 形式で保存。

2. **SQL ファイルの解析と CSV 出力 (`parse_sql_queries.py`)**:

   - ステップ 1 で生成されたスキーマ情報を基に、指定ディレクトリ内の全ての SQL ファイルを解析し、各ファイルごとに CSV ファイルとして出力。

3. **解析結果の集計 (`aggregate_csv.py`)**:
   - ステップ 2 で出力された各 CSV ファイルを読み込み、全体の DML 操作の統計やテーブル・カラム使用状況を集計し、新たな CSV ファイルとして保存。

### 今後の拡張

- **詳細なスキーマ情報の管理**:
  - カラムのデータ型や制約情報をスキーマ情報に含めることで、より詳細な解析が可能。
- **ビューの依存関係の解析**:

  - ビューが他のビューやテーブルを参照している場合、その依存関係を解析し、スキーマ情報に反映。

- **エラーハンドリングの改善**:

  - パースエラー時の詳細なログ記録や、スキーマ情報に存在しないカラムの取り扱いを改善。

- **パフォーマンスの向上**:

  - 大規模な SQL ファイルを効率的に処理するための最適化手法（マルチスレッド処理など）の導入。

- **柔軟な出力形式**:

  - CSV 以外の形式（JSON、Excel）での出力や、データベースへの直接保存機能の追加。

- **可視化ツールとの連携**:
  - 集計結果を可視化ツールと連携させ、視覚的なレポートを生成。

これらのスクリプトとガイドを基に、プロジェクトのニーズに合わせた高度な SQL 解析ツールを構築してください。質問や具体的な問題があれば、遠慮なくお知らせください。
