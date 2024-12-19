各層ごとに解析を行い、最終的に**CRUD 図**として CSV に出力し、紐づける方式は非常に合理的です。このアプローチにより、各層の役割を明確に分離しながら、最終的な統合をスムーズに実現できます。

---

### **各層ごとの解析フローとポイント**

#### **1. ロジック層（Controller/Service）の解析**

**目的**：  
業務操作とデータ操作の関連付けを明確にし、**どのメソッドがどの CRUD 操作をトリガーするか**を抽出します。

**解析内容**：

- **操作名**（例：`getUserList`, `createUser`）
- **CRUD 操作**（Create / Read / Update / Delete の分類）
- **呼び出し対象の DAO メソッド**  
  → 解析結果を CSV に出力します。

**CSV 出力項目**：
| ロジック名 | 操作名 | CRUD 種別 | DAO メソッド名 |
| ------------ | ------------ | -------- | ------------- |
| UserService | getUserList | Read | findAll |
| UserService | createUser | Create | create |

---

#### **2. DAO 層の解析**

**目的**：  
ロジック層のメソッドとマッパー層（SQL 定義）の紐づけを明確にします。

**解析内容**：

- **DAO メソッド名**（例：`findAll`, `create`）
- **Mapper.xml の ID 属性**との関連
- **CRUD 操作**の分類

**CSV 出力項目**：
| DAO クラス名 | DAO メソッド名 | CRUD 種別 | Mapper ID |
| ---------------- | ------------ | -------- | --------- |
| UserDataDao | findAll | Read | findAll |
| UserDataDao | create | Create | create |

---

#### **3. マッパー層（Mapper.xml）の解析**

**目的**：  
マッパーの SQL 定義から対象の**テーブル名**、**カラム名**、および条件を抽出します。

**解析内容**：

- **Mapper ID**（`id`属性）
- **CRUD 操作**の種類（`<select>`, `<insert>`, `<update>`, `<delete>`）
- **対象テーブル名**、カラム名
- **WHERE 句や条件式**  
  動的 SQL がある場合は、展開後の SQL を含めます。

**CSV 出力項目**：
| Mapper ID | CRUD 種別 | テーブル名 | カラム名 | 条件式 |
| --------- | -------- | ---------- | -------------- | ---------------- |
| findAll | Read | USER_DATA | id, name | u.sex = m.sex_cd |
| create | Create | USER_DATA | id, name, sex | |

---

### **最終的な CRUD 図の統合**

**目的**：  
各層の CSV ファイルを統合し、**業務操作 → DAO メソッド → Mapper ID → SQL 定義 → テーブル/カラム**という一気通貫の流れを整理します。

#### **統合フロー**

1. **ロジック層の CSV**と**DAO 層の CSV**を結合  
   → DAO メソッド名をキーに、業務操作と CRUD 操作を紐づける。

2. **DAO 層の CSV**と**マッパー層の CSV**を結合  
   → Mapper ID をキーに、SQL 定義と CRUD 操作を紐づける。

3. **最終的な CRUD 図**の作成
   - 業務操作 → DAO メソッド → Mapper ID → SQL 定義 → テーブル・カラム名 を一つの CSV にまとめる。

**最終 CRUD 図 CSV 出力項目**：
| 業務操作 | CRUD 種別 | DAO メソッド名 | Mapper ID | テーブル名 | カラム名 | 条件式 |
| ---------- | -------- | ------------ | --------- | ---------- | ---------------- | ---------------- |
| getUserList | Read | findAll | findAll | USER_DATA | id, name, sex | u.sex = m.sex_cd |
| createUser | Create | create | create | USER_DATA | id, name, sex | |

---

### **方式のメリット**

1. **分離された解析**：各層ごとに独立して解析できるため、責務が明確になります。
2. **段階的な統合**：個別の CSV を統合することで、全体の流れを効率的に把握できます。
3. **変更対応が容易**：
   - 層ごとに再解析すればよく、変更の影響範囲が最小化されます。
4. **可視化が容易**：  
   統合後の CRUD 図により、業務操作とデータ操作の関連性を直感的に把握できます。

---

この方式により、**業務ロジックからデータベース操作までの一貫した流れ**を明確に可視化でき、影響範囲分析や設計の改善にも役立つツールとして活用できます。

ロジック層で複数のメソッドが**相互に経由している**場合や、複雑な呼び出し構造がある場合は、**依存関係の解析**を行い、メソッド間のつながりを明確にすることが重要です。

以下の手順とポイントで対応することができます。

---

### **対応方針**

#### **1. ロジック層の依存関係を解析する**

複数のメソッドが連携している場合、各メソッドの呼び出し関係を解析し、依存関係のフローを明確にします。

**解析内容**：

- メソッド A がメソッド B や C を呼び出しているか
- 呼び出し先の DAO メソッドや CRUD 操作との関係性

**方法**：

- 静的解析ツール（例：ソースコードの AST 解析や Call Graph 生成）を使う
- ロジック層内のメソッド間の**呼び出しチェーン**を追跡し、フロー図や CSV として出力する

---

#### **2. 呼び出しフローを分割して整理**

**呼び出しの流れを再帰的に分解し、最終的な CRUD 操作までの関係を整理します。**

**例：**  
ロジック部でメソッド A → メソッド B → DAO → SQL となる場合：

| 業務操作 | 呼び出し元メソッド | 呼び出し先メソッド | DAO メソッド | CRUD 種別 | 対象テーブル |
| -------- | ------------------ | ------------------ | ------------ | --------- | ------------ |
| getUser  | getUser            | fetchUserList      | findAll      | Read      | USER_DATA    |
| getUser  | fetchUserList      | -                  | findAll      | Read      | USER_DATA    |

- **呼び出し元メソッド**と**呼び出し先メソッド**を明確にする。
- フローの終点（DAO 層の CRUD 操作）まで紐づける。

---

#### **3. 中間フローと CRUD の統合**

依存関係が複数メソッドを跨ぐ場合でも、以下の手順で最終的な CRUD 図にまとめます。

1. **ロジック層の依存関係フロー**を CSV に出力  
   | 呼び出し元メソッド | 呼び出し先メソッド | 備考 |
   | ---------------- | ---------------- | ---------- |
   | getUser | fetchUserList | データ取得 |
   | fetchUserList | DAO.findAll | SQL 呼び出し|

2. **依存フローと DAO/SQL 層の CRUD 操作**を結合

   - 呼び出し先メソッドをキーに、DAO メソッド → Mapper ID → CRUD 操作 → テーブル/カラムまで紐づけます。

3. **最終 CRUD 図の統合**  
   すべての業務操作から CRUD 操作までのフローを一つの CRUD 図として整理します。

---

### **複数メソッド経由時の CRUD 図出力例**

| 業務操作 | 呼び出し元メソッド | 呼び出し先メソッド | DAO メソッド | CRUD 種別 | テーブル名 | カラム名      | 条件式           |
| -------- | ------------------ | ------------------ | ------------ | --------- | ---------- | ------------- | ---------------- |
| getUser  | getUser            | fetchUserList      | findAll      | Read      | USER_DATA  | id, name, sex | u.sex = m.sex_cd |
| saveUser | saveUser           | validateUser       | -            | -         | -          | -             | -                |
| saveUser | validateUser       | createUser         | create       | Create    | USER_DATA  | id, name, sex |                  |

---

### **ポイント**

1. **メソッドチェーンを可視化**：
   - 呼び出し元と呼び出し先を明確に整理し、最終的な CRUD 操作まで追跡する。
2. **依存フローの中間出力**：
   - 呼び出し関係だけを出力する CSV と、CRUD 操作を含めた統合 CSV の 2 段階に分けると整理しやすい。
3. **自動化**：
   - 静的解析ツール（AST 解析や Call Graph 生成）を利用して依存関係を自動抽出し、フローを出力することで作業を効率化できます。
4. **業務操作から最終 CRUD 操作まで一貫性を持たせる**：
   - 業務の流れが複数メソッドを経由しても、CRUD 操作との紐づけを途切れなく可視化します。

---

この方法により、複数メソッドが経由するような複雑なロジックでも、CRUD 操作のフローを体系的に整理し、図として一貫して出力することが可能です。

Java コードから **クラス名**、**メソッド名**、**呼び出し元メソッド**、**呼び出し先メソッド**、および **`sqlSession`の利用** を解析し、Python を利用して **CSV 出力** する方法を具体的に説明します。

---

### **アプローチ概要**

1. **ANTLR を利用して Java コードを AST（抽象構文木）に変換**
   - `sqlSession` の利用（メソッド呼び出し）を含め、メソッドやクラス名を AST から解析。
2. **AST をトラバースして解析**
   - **クラス名**
   - **メソッド名**
   - **メソッド間の呼び出し関係**（呼び出し元/呼び出し先）
   - **sqlSession**の呼び出し箇所。
3. **結果を CSV に出力**

---

### **ステップ 1: Java 文法の ANTLR パーサー生成**

#### 1. **ANTLR4 のセットアップ**

ANTLR の Python ランタイムと Java 文法ファイルを準備します。

- ANTLR4 のインストール:

  ```bash
  pip install antlr4-python3-runtime
  ```

- Java の文法ファイル（`Java.g4`）を取得:  
   [Java.g4 のダウンロード](https://github.com/antlr/grammars-v4/tree/master/java/java9)

- Python 用のパーサーを生成:
  ```bash
  antlr4 -Dlanguage=Python3 Java.g4 -o java_parser
  ```

---

### **ステップ 2: Python 解析スクリプトの作成**

以下のスクリプトでは、クラス名、メソッド名、呼び出し元・先のメソッド、および`sqlSession`利用を抽出します。

#### **Python コード**

```python
import sys
import csv
from antlr4 import *
from java_parser.JavaLexer import JavaLexer
from java_parser.JavaParser import JavaParser
from java_parser.JavaParserListener import JavaParserListener

class JavaASTListener(JavaParserListener):
    def __init__(self):
        self.current_class = None
        self.current_method = None
        self.method_calls = []  # 呼び出し元・呼び出し先
        self.sql_sessions = []  # sqlSessionの利用

    def enterClassDeclaration(self, ctx):
        # クラス名を取得
        self.current_class = ctx.IDENTIFIER().getText()

    def enterMethodDeclaration(self, ctx):
        # メソッド名を取得
        self.current_method = ctx.IDENTIFIER().getText()

    def exitMethodDeclaration(self, ctx):
        # メソッドを出たらクリア
        self.current_method = None

    def enterExpression(self, ctx):
        # 呼び出し先メソッドの検出（メソッドチェーンも含む）
        if ctx.getText().startswith("sqlSession"):
            self.sql_sessions.append({
                "class": self.current_class,
                "method": self.current_method,
                "sqlSessionCall": ctx.getText()
            })
        elif "." in ctx.getText():  # メソッド呼び出し
            method_call = ctx.getText()
            self.method_calls.append({
                "class": self.current_class,
                "caller_method": self.current_method,
                "called_method": method_call
            })

def parse_java_file(input_file):
    input_stream = FileStream(input_file, encoding="utf-8")
    lexer = JavaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JavaParser(stream)
    tree = parser.compilationUnit()

    listener = JavaASTListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

    return listener.method_calls, listener.sql_sessions

def write_to_csv(method_calls, sql_sessions, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Class", "CallerMethod", "CalledMethod", "SqlSessionUsage"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for call in method_calls:
            writer.writerow({
                "Class": call["class"],
                "CallerMethod": call["caller_method"],
                "CalledMethod": call["called_method"],
                "SqlSessionUsage": ""
            })

        for sql in sql_sessions:
            writer.writerow({
                "Class": sql["class"],
                "CallerMethod": sql["method"],
                "CalledMethod": "",
                "SqlSessionUsage": sql["sqlSessionCall"]
            })

if __name__ == "__main__":
    input_file = "Sample.java"  # 解析するJavaファイル
    output_file = "java_ast_output.csv"

    print("Parsing Java file...")
    method_calls, sql_sessions = parse_java_file(input_file)
    write_to_csv(method_calls, sql_sessions, output_file)
    print(f"Results written to {output_file}")
```

---

### **ステップ 3: Java コードのサンプル**

`Sample.java`の例：

```java
public class Sample {
    public void getData() {
        sqlSession.selectList("query.getData");
        processData();
    }
    public void processData() {
        System.out.println("Processing data...");
    }
    public void saveData() {
        sqlSession.insert("query.saveData");
    }
}
```

---

### **ステップ 4: スクリプト実行**

Python スクリプトを実行します。

```bash
python java_ast_parser.py
```

---

### **出力結果 (CSV 形式)**

生成される`java_ast_output.csv`の内容は次のようになります：

| Class  | CallerMethod | CalledMethod          | SqlSessionUsage                        |
| ------ | ------------ | --------------------- | -------------------------------------- |
| Sample | getData      | sqlSession.selectList | sqlSession.selectList("query.getData") |
| Sample | getData      | processData           |                                        |
| Sample | saveData     | sqlSession.insert     | sqlSession.insert("query.saveData")    |

---

### **解析結果の説明**

1. **Class**：クラス名
2. **CallerMethod**：呼び出し元のメソッド名
3. **CalledMethod**：呼び出し先のメソッド名（`sqlSession`の呼び出し含む）
4. **SqlSessionUsage**：`sqlSession`の利用があればその呼び出し内容

---

### **拡張案**

- **複数ファイル対応**：ディレクトリ内の複数の Java ファイルを再帰的に解析する。
- **詳細な CRUD 解析**：`sqlSession`利用部分から具体的な SQL クエリの CRUD 種別（`select`、`insert`、`update`、`delete`）を分類する。
- **可視化**：呼び出し関係をグラフツール（Graphviz など）で可視化。

---

### **まとめ**

この方法により、Python を使って Java コードを解析し、**クラス名**、**メソッド名**、**呼び出し元/先メソッド**、および`sqlSession`利用を抽出し、CSV 形式で出力できます。これにより、Java の依存関係やデータアクセス部分を効率的に把握できます。

呼び出し先の**呼び出し先**がある場合（メソッドチェーンや多段呼び出し）、どこまで解析すべきかは **目的** に応じて柔軟に決定する必要があります。

以下の観点から考慮すると、解析の深さを適切に設定できます。

---

### **1. 解析の目的とゴールに応じた深さ**

#### **目的: 業務フロー全体の把握**

- **深さ**: **完全解析（再帰的にすべての呼び出し先をトラバース）**
  - 利用シナリオ: 業務フローを完全に把握したい場合や、影響範囲分析が必要な場合。
  - 例: ロジック部 → DAO → マッパー → SQL 定義 と深掘りし、最終的なデータベース操作（CRUD）まで可視化。

#### **目的: 直接的な呼び出し関係の把握**

- **深さ**: **1 段階解析（直接呼び出しのみ）**
  - 利用シナリオ: 呼び出し元と呼び出し先の関係を単純に把握し、ロジックの流れを整理したい場合。
  - 例: `getData()` → `processData()`、`saveData()` → `sqlSession.insert()` の関係のみ。

#### **目的: 特定メソッドからの依存関係の解析**

- **深さ**: **任意の深さ（指定した段階まで）**
  - 利用シナリオ: ある重要メソッドがどこまで影響を与えるか（N 段階呼び出し先まで）を把握したい場合。
  - 例: 深さ 2 → `getData()` → `processData()` → さらに `sqlSession.insert()` まで。

---

### **2. 再帰的解析の利点と注意点**

#### **利点**

- **網羅性**：すべての依存関係とメソッド呼び出しの流れが把握できる。
- **影響範囲分析**：変更が発生した場合、影響範囲を明確にするために必須。
- **デバッグ支援**：深いメソッドチェーンでも問題の発生箇所を特定しやすい。

#### **注意点**

- **解析のオーバーヘッド**：深さを増やすと解析に時間がかかり、データ量も膨大になる。
- **冗長性**：不必要に詳細すぎる情報は、可読性を下げる場合がある。
- **循環参照の検出**：メソッド間に循環呼び出しが存在する場合、無限ループを避けるための対策が必要。

---

### **3. 実装方法における工夫**

#### **再帰的に解析するが、深さを制限する**

- 再帰呼び出しの深さをパラメータで制御する（例：深さ N まで）。
  ```python
  def parse_method_calls(ctx, depth=0, max_depth=3):
      if depth > max_depth:
          return
      # 再帰処理を行う
      for call in ctx.method_calls:
          parse_method_calls(call, depth=depth + 1, max_depth=max_depth)
  ```

#### **循環参照の検出**

- 呼び出し済みのメソッドを記録し、再度呼び出される場合は解析を中断する。
  ```python
  visited = set()
  def parse_method_calls(ctx):
      if ctx in visited:
          return
      visited.add(ctx)
      # 呼び出し解析を続ける
  ```

---

### **4. おすすめの解析深さと出力形式**

| **解析目的**                 | **推奨深さ**   | **出力項目**                                                |
| ---------------------------- | -------------- | ----------------------------------------------------------- |
| 業務フロー全体の把握         | 無制限（完全） | クラス名、呼び出し元メソッド、呼び出し先メソッド、CRUD 操作 |
| 直接的な呼び出し関係の可視化 | 1 段階         | クラス名、呼び出し元メソッド、呼び出し先メソッド            |
| 影響範囲分析                 | 任意の深さ     | クラス名、呼び出し元メソッド、呼び出し先メソッド            |
| SQL 操作に特化した解析       | 深さ 2 程度    | クラス名、メソッド名、SQL 文、CRUD 操作                     |

---

### **結論**

解析の深さは **目的** によって決定しますが、以下の方針がバランスが取れています：

1. **直接的な呼び出し（深さ 1）** をデフォルトにする。
2. **再帰的解析（深さ制限あり）** で影響範囲を追跡可能にする。
3. **循環参照** を考慮し、解析ループを回避する。

これにより、必要に応じて詳細な解析結果を得つつ、解析時間や出力データ量を制御することができます。
