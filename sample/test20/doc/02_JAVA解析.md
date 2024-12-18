操作対象のテーブルを除いた処理の手順を以下に再整理します。

---

### **ステップ 1: ロジック層の解析**

#### **目的**

- 全てのメソッドを解析し、呼び出し関係を再帰的に追跡。
- ロジック層のメソッド一覧とその呼び出しチェーンを記録。

#### **手順**

1. 対象のディレクトリからロジック層（例: Controller や Service クラス）の Java ファイルを収集。
2. 各ファイルを静的解析ツール（例: `javalang`）で解析。
3. 以下を抽出:
   - クラス名。
   - メソッド名（定義された全メソッド）。
   - 各メソッドが呼び出している他のメソッド（ロジック内および DAO メソッド含む）。
4. 再帰的に呼び出し関係を追跡し、呼び出しチェーンをリスト化。
5. 抽出結果を`logic_calls.csv`に出力。

---

### **ステップ 2: DAO 層の解析**

#### **目的**

- DAO クラスで使用される MyBatis の SQL 操作を特定。
- MyBatis ID を記録。

#### **手順**

1. 対象のディレクトリから DAO クラスの Java ファイルを収集。
2. 各ファイルを静的解析ツールで解析。
3. 以下を抽出:
   - クラス名。
   - メソッド名（DAO クラス内の全メソッド）。
   - `sqlSession.select`, `sqlSession.insert`, `sqlSession.update`, `sqlSession.delete`などの SQL 操作を呼び出している箇所。
   - MyBatis ID（例: `findAll`, `findById`）。
4. 抽出結果を`dao_calls.csv`に出力。

---

### **ステップ 3: `sqlSession`利用箇所の解析**

#### **目的**

- DAO 内での`sqlSession`呼び出しを詳細に解析。
- MyBatis ID、SQL 操作、渡されるパラメータを記録。

#### **手順**

1. DAO 層解析の結果を入力として使用。
2. `sqlSession.○○`呼び出し箇所を再解析し、以下を抽出:
   - 呼び出し元クラス名。
   - 呼び出し元メソッド名。
   - `sqlSession`操作種別（例: select, insert）。
   - MyBatis ID。
   - 渡されるパラメータ（例: `#{id}`, `#{name}`）。
3. 抽出結果を`sqlsession_calls.csv`に出力。

---

### **各ステップのアウトプット**

#### **1. ロジック解析 (`logic_calls.csv`)**

| **ファイル名**  | **クラス名** | **メソッド名** | **呼び出しメソッド** |
| --------------- | ------------ | -------------- | -------------------- |
| LogicClass.java | LogicClass   | methodA        | methodB              |
| LogicClass.java | LogicClass   | methodB        | dao.methodC          |

#### **2. DAO 解析 (`dao_calls.csv`)**

| **ファイル名** | **クラス名** | **メソッド名** | **MyBatis ID** | **操作種別** |
| -------------- | ------------ | -------------- | -------------- | ------------ |
| DAOClass.java  | DAOClass     | methodC        | findAll        | SELECT       |

#### **3. `sqlSession`利用箇所解析 (`sqlsession_calls.csv`)**

| **ファイル名** | **クラス名** | **メソッド名** | **SQL 操作**      | **MyBatis ID** | **パラメータ** |
| -------------- | ------------ | -------------- | ----------------- | -------------- | -------------- |
| DAOClass.java  | DAOClass     | methodC        | sqlSession.select | findAll        | #{id}, #{name} |

---

### **ステップ 4: 結果の統合と確認**

#### **目的**

- 各 CSV を確認し、ロジック層・DAO 層・SQL 呼び出しの全体像を把握。

#### **手順**

1. 各 CSV をレビューし、プロジェクト全体の呼び出し関係が正確に記録されているか確認。
2. 必要に応じて以下を実施:
   - ロジック層と DAO 層の呼び出し関係を結合して統一的なマッピング表を作成。
   - SQL 呼び出しと MyBatis ID の依存関係を可視化。

---

### **懸念点への対応**

- **MyBatis ID の精度**:
  - 動的に決定される MyBatis ID やパラメータ（変数やリフレクションなど）の補完が必要。
- **深度制限**:
  - ロジック層の再帰呼び出しに対して、適切な深度制限を設ける。
- **パフォーマンス**:
  - 並列処理を導入してファイル単位で解析を並列化し、処理時間を短縮。

---

この手順を実施することで、ロジック層・DAO 層・SQL 利用箇所を独立して解析でき、結果を簡単に統合できます。追加要望や調整が必要であればお知らせください。

`javalang` を使用して、Java ファイルの解析を行うように実装を変更します。`javalang` は Java 構文の解析に適したライブラリであり、クラス、メソッド、呼び出し関係などの情報を簡単に抽出できます。

---

### 実装概要

- **`javalang`を利用した構文解析**

  - クラス名、メソッド名、メソッド内の呼び出し関係を抽出します。

- **呼び出しメソッドをカラム化**
  - 各メソッドの呼び出し関係を列ごとに分割して出力します。

---

### 必要な準備

`javalang` をインストールします。

```bash
pip install javalang
```

---

### ロジック層解析モジュール

以下は、`javalang` を使用して Java ファイルを解析し、クラス名、メソッド名、呼び出しメソッドを抽出するコードです。

#### **コード例**

```python
import javalang

def analyze_logic_with_javalang(file_path):
    """
    `javalang` を使用してロジック層の Java ファイルを解析します。

    Args:
        file_path (str): Java ファイルのパス。

    Returns:
        list: 抽出結果のリスト。各エントリは辞書形式。
    """
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Java ファイルを解析
        tree = javalang.parse.parse(content)

        # クラス名を抽出
        class_declarations = [node for path, node in tree.filter(javalang.tree.ClassDeclaration)]
        for class_decl in class_declarations:
            class_name = class_decl.name

            # メソッドを解析
            for method in class_decl.methods:
                method_name = method.name
                called_methods = []

                # メソッド内の呼び出しを追跡
                for path, node in method.filter(javalang.tree.MethodInvocation):
                    called_methods.append(node.member)

                # 呼び出しメソッドをカラム化
                result = {
                    "class_name": class_name,
                    "method_name": method_name,
                }
                for i, called_method in enumerate(called_methods, start=1):
                    result[f"called_method_{i}"] = called_method

                results.append(result)

    except Exception as e:
        print(f"解析エラー: {file_path} - {e}")

    return results
```

---

### メインスクリプト

解析結果をプロパティ単位、クラス単位で出力するコードを以下に示します。

#### **コード例**

```python
import csv
import os
from logic_parser import analyze_logic_with_javalang

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_files_with_output(input_csv, output_base_dir):
    property_dirs = {
        "LOGIC": os.path.join(output_base_dir, "LOGIC"),
        "DAO": os.path.join(output_base_dir, "DAO"),
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
                results = analyze_logic_with_javalang(file_path)
            else:
                print(f"未対応の解析: {property_type}")
                results = []

            # クラスごとに CSV を出力
            if results:
                # 動的にカラムを取得
                all_columns = set(key for result in results for key in result.keys())
                with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
                    writer = csv.DictWriter(output_file, fieldnames=list(all_columns))
                    writer.writeheader()
                    writer.writerows(results)
                print(f"結果を出力: {output_csv}")

# 実行例
process_files_with_output("./file_properties.csv", "./output")
```

---

### 出力結果例

#### 対象ファイル: `LogicClass.java`

```java
class LogicClass {
    void methodA() {
        methodB();
        methodC();
    }
    void methodB() {
        methodD();
    }
}
```

#### **CSV 例**

| class_name | method_name | called_method_1 | called_method_2 |
| ---------- | ----------- | --------------- | --------------- |
| LogicClass | methodA     | methodB         | methodC         |
| LogicClass | methodB     | methodD         | None            |

---

### この設計のメリット

1. **構文解析の信頼性**

   - `javalang` を使用して正確な Java 構文解析を実現。

2. **動的カラム生成**

   - 呼び出しメソッド数に応じて列を自動的に増やす。

3. **簡潔なロジック**
   - メソッドの呼び出し解析が簡潔で拡張性が高い。

必要に応じて、DAO 層解析の実装も追加できます。このスクリプトを基にプロジェクトに適用してください！

以下に、`javalang` を利用した DAO 層解析のコードを提供します。これにより、Java ファイル内での SQL 操作（`sqlSession` の利用箇所）を解析し、操作種別（`select`, `insert`, `update`, `delete`）やパラメータを抽出できます。

---

### DAO 層解析モジュール

#### **コード例**

`dao_parser.py`

```python
import javalang

def analyze_dao_with_javalang(file_path):
    """
    DAO層の Java ファイルを解析し、SQL 操作の利用箇所を抽出。

    Args:
        file_path (str): Java ファイルのパス。

    Returns:
        list: 抽出結果のリスト。各エントリは辞書形式。
    """
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Java ファイルを解析
        tree = javalang.parse.parse(content)

        # クラス名を抽出
        class_declarations = [node for path, node in tree.filter(javalang.tree.ClassDeclaration)]
        for class_decl in class_declarations:
            class_name = class_decl.name

            # メソッドを解析
            for method in class_decl.methods:
                method_name = method.name
                sql_operations = []

                # メソッド内の sqlSession 呼び出しを解析
                for path, node in method.filter(javalang.tree.MethodInvocation):
                    if node.qualifier == "sqlSession":  # sqlSession を呼び出している箇所
                        sql_operations.append({
                            "sql_operation": node.member,  # 操作種別 (select, insert, etc.)
                            "parameters": ", ".join(arg.member if hasattr(arg, 'member') else str(arg) for arg in node.arguments)
                        })

                # SQL 操作を結果に追加
                for operation in sql_operations:
                    results.append({
                        "class_name": class_name,
                        "method_name": method_name,
                        "sql_operation": operation["sql_operation"],
                        "parameters": operation["parameters"]
                    })

    except Exception as e:
        print(f"DAO解析エラー: {file_path} - {e}")

    return results
```

---

### メインスクリプトの統合

`process_files_with_output` に DAO 層解析を統合します。

#### **修正版メインスクリプト**

```python
import csv
import os
from logic_parser import analyze_logic_with_javalang
from dao_parser import analyze_dao_with_javalang

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_files_with_output(input_csv, output_base_dir):
    property_dirs = {
        "LOGIC": os.path.join(output_base_dir, "LOGIC"),
        "DAO": os.path.join(output_base_dir, "DAO"),
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
                results = analyze_logic_with_javalang(file_path)
            elif property_type == "DAO":
                print(f"DAO解析: {file_path}")
                results = analyze_dao_with_javalang(file_path)
            else:
                print(f"未対応の解析: {property_type}")
                results = []

            # クラスごとに CSV を出力
            if results:
                # 動的にカラムを取得
                all_columns = set(key for result in results for key in result.keys())
                with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
                    writer = csv.DictWriter(output_file, fieldnames=list(all_columns))
                    writer.writeheader()
                    writer.writerows(results)
                print(f"結果を出力: {output_csv}")

# 実行例
process_files_with_output("./file_properties.csv", "./output")
```

---

### 出力結果例

#### 対象ファイル: `UserDao.java`

```java
class UserDao {
    public List<User> findAll() {
        return sqlSession.select("UserMapper.findAll");
    }

    public void insertUser(User user) {
        sqlSession.insert("UserMapper.insertUser", user);
    }
}
```

#### **CSV 例**

| class_name | method_name | sql_operation | parameters                    |
| ---------- | ----------- | ------------- | ----------------------------- |
| UserDao    | findAll     | select        | "UserMapper.findAll"          |
| UserDao    | insertUser  | insert        | "UserMapper.insertUser, user" |

---

### この設計の利点

1. **正確な構文解析**

   - `javalang` を使用して、SQL 操作に関連するすべての呼び出しを解析。

2. **柔軟な出力**

   - SQL 操作やパラメータを簡単に確認可能。

3. **再利用性**
   - 他の解析（例: トランザクション管理の解析）に拡張可能。

必要に応じてさらなるカスタマイズが可能です。このスクリプトをベースにプロジェクトに適用してください！

以下に、`javalang` を利用した DAO 層解析のコードを提供します。これにより、Java ファイル内での SQL 操作（`sqlSession` の利用箇所）を解析し、操作種別（`select`, `insert`, `update`, `delete`）やパラメータを抽出できます。

---

### DAO 層解析モジュール

#### **コード例**

`dao_parser.py`

```python
import javalang

def analyze_dao_with_javalang(file_path):
    """
    DAO層の Java ファイルを解析し、SQL 操作の利用箇所を抽出。

    Args:
        file_path (str): Java ファイルのパス。

    Returns:
        list: 抽出結果のリスト。各エントリは辞書形式。
    """
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Java ファイルを解析
        tree = javalang.parse.parse(content)

        # クラス名を抽出
        class_declarations = [node for path, node in tree.filter(javalang.tree.ClassDeclaration)]
        for class_decl in class_declarations:
            class_name = class_decl.name

            # メソッドを解析
            for method in class_decl.methods:
                method_name = method.name
                sql_operations = []

                # メソッド内の sqlSession 呼び出しを解析
                for path, node in method.filter(javalang.tree.MethodInvocation):
                    if node.qualifier == "sqlSession":  # sqlSession を呼び出している箇所
                        sql_operations.append({
                            "sql_operation": node.member,  # 操作種別 (select, insert, etc.)
                            "parameters": ", ".join(arg.member if hasattr(arg, 'member') else str(arg) for arg in node.arguments)
                        })

                # SQL 操作を結果に追加
                for operation in sql_operations:
                    results.append({
                        "class_name": class_name,
                        "method_name": method_name,
                        "sql_operation": operation["sql_operation"],
                        "parameters": operation["parameters"]
                    })

    except Exception as e:
        print(f"DAO解析エラー: {file_path} - {e}")

    return results
```

---

### メインスクリプトの統合

`process_files_with_output` に DAO 層解析を統合します。

#### **修正版メインスクリプト**

```python
import csv
import os
from logic_parser import analyze_logic_with_javalang
from dao_parser import analyze_dao_with_javalang

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_files_with_output(input_csv, output_base_dir):
    property_dirs = {
        "LOGIC": os.path.join(output_base_dir, "LOGIC"),
        "DAO": os.path.join(output_base_dir, "DAO"),
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
                results = analyze_logic_with_javalang(file_path)
            elif property_type == "DAO":
                print(f"DAO解析: {file_path}")
                results = analyze_dao_with_javalang(file_path)
            else:
                print(f"未対応の解析: {property_type}")
                results = []

            # クラスごとに CSV を出力
            if results:
                # 動的にカラムを取得
                all_columns = set(key for result in results for key in result.keys())
                with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
                    writer = csv.DictWriter(output_file, fieldnames=list(all_columns))
                    writer.writeheader()
                    writer.writerows(results)
                print(f"結果を出力: {output_csv}")

# 実行例
process_files_with_output("./file_properties.csv", "./output")
```

---

### 出力結果例

#### 対象ファイル: `UserDao.java`

```java
class UserDao {
    public List<User> findAll() {
        return sqlSession.select("UserMapper.findAll");
    }

    public void insertUser(User user) {
        sqlSession.insert("UserMapper.insertUser", user);
    }
}
```

#### **CSV 例**

| class_name | method_name | sql_operation | parameters                    |
| ---------- | ----------- | ------------- | ----------------------------- |
| UserDao    | findAll     | select        | "UserMapper.findAll"          |
| UserDao    | insertUser  | insert        | "UserMapper.insertUser, user" |

---

### この設計の利点

1. **正確な構文解析**

   - `javalang` を使用して、SQL 操作に関連するすべての呼び出しを解析。

2. **柔軟な出力**

   - SQL 操作やパラメータを簡単に確認可能。

3. **再利用性**
   - 他の解析（例: トランザクション管理の解析）に拡張可能。

必要に応じてさらなるカスタマイズが可能です。このスクリプトをベースにプロジェクトに適用してください！
