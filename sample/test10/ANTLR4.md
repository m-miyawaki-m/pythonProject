ANTLR4 を利用して**Java の文法ファイルを作成し、ソースコードを解析**する手順を以下に詳しく説明します。

---

## **1. ANTLR4 の環境構築**

### **1.1 必要なツールのインストール**

- **Java**: ANTLR は Java ベースで動作するため、Java（JDK 8 以上）が必要です。
- **ANTLR4**: パーサー生成ツールです。
- **Python**: Python ランタイムを使って生成されたパーサーを実行します。

### **1.2 ANTLR4 のダウンロード**

1. ANTLR4 の JAR ファイルをダウンロードします。  
   [ANTLR4 公式サイト](https://www.antlr.org/download.html) から最新版の `antlr-4.x-complete.jar` を取得します。

2. コマンドラインでエイリアスを設定します。  
   （ダウンロードした JAR のパスに置き換えてください）

   ```bash
   alias antlr4='java -jar antlr-4.13.2-complete.jar'
   alias grun='java org.antlr.v4.gui.TestRig'
   ```

3. Python 用のランタイムをインストールします。
   ```bash
   pip install antlr4-python3-runtime
   ```

---

## **2. Java 文法ファイルの作成**

ANTLR はすでに**Java の文法定義ファイル**を提供しています。これを使えば、手作業で文法を作成する必要はありません。

### **2.1 文法ファイルの取得**

Java の ANTLR 文法ファイル（Java.g4）は、ANTLR 公式の GitHub リポジトリからダウンロードできます。

**ダウンロード先**:  
[Java.g4（Java 9 の文法）](https://github.com/antlr/grammars-v4/tree/master/java/java9)

---

## **3. Java.g4 を基に Lexer と Parser を生成**

ダウンロードした`Java.g4`を利用して、Lexer および Parser を生成します。

### **3.1 コマンド実行**

以下のコマンドを実行し、Python 向けの Lexer と Parser を生成します。

```bash
antlr4 -Dlanguage=Python3 Java.g4 -o java_parser
```

| **オプション**       | **説明**                                              |
| -------------------- | ----------------------------------------------------- |
| `-Dlanguage=Python3` | Python 3 向けのコードを生成します。                   |
| `Java.g4`            | 文法ファイルです（Java の文法定義）。                 |
| `-o java_parser`     | 出力先ディレクトリとして `java_parser` を指定します。 |

**実行結果**:

- `java_parser`ディレクトリ内に以下のファイルが生成されます：
  - `JavaLexer.py`: Lexer（字句解析器）
  - `JavaParser.py`: Parser（構文解析器）
  - `JavaParserListener.py`: AST を走査するためのリスナー
  - `Java.tokens`: トークン定義

---

## **4. Python で Java コードを解析**

生成された Lexer と Parser を利用して、Java ソースコードを解析します。

### **4.1 Java ソースコードの準備**

解析対象の Java ファイル `Sample.java` を用意します。

```java
public class Sample {
    public void sayHello() {
        System.out.println("Hello, ANTLR4!");
    }

    public int add(int a, int b) {
        return a + b;
    }
}
```

---

### **4.2 Python で解析スクリプトを作成**

Python スクリプト `parse_java.py` を作成します。

```python
from antlr4 import *
from java_parser.JavaLexer import JavaLexer
from java_parser.JavaParser import JavaParser
from java_parser.JavaParserListener import JavaParserListener

# カスタムリスナー: クラスとメソッド名を出力
class CustomJavaListener(JavaParserListener):
    def enterClassDeclaration(self, ctx):
        class_name = ctx.IDENTIFIER().getText()
        print(f"Class: {class_name}")

    def enterMethodDeclaration(self, ctx):
        method_name = ctx.IDENTIFIER().getText()
        print(f"Method: {method_name}")

def main(input_file):
    # 入力ファイルの読み込み
    input_stream = FileStream(input_file, encoding="utf-8")
    lexer = JavaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JavaParser(stream)

    # AST（構文木）の生成
    tree = parser.compilationUnit()

    # カスタムリスナーを使ってASTを走査
    listener = CustomJavaListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

if __name__ == "__main__":
    input_file = "Sample.java"  # 解析するJavaファイル
    main(input_file)
```

---

### **4.3 Python スクリプトの実行**

以下のコマンドでスクリプトを実行します。

```bash
python parse_java.py
```

**出力結果**:

```text
Class: Sample
Method: sayHello
Method: add
```

---

## **5. 出力データの拡張**

### **5.1 呼び出し関係の解析**

- **`enterMethodCall`** などのイベントを利用すれば、メソッド呼び出しを検出できます。
- `ctx.getText()` を使って、メソッドの引数や呼び出し先を解析します。

```python
def enterExpression(self, ctx):
    if '(' in ctx.getText():
        print(f"Method Call: {ctx.getText()}")
```

---

### **5.2 CSV 形式で出力**

結果を CSV に書き出すことで、解析結果をわかりやすく整理できます。

```python
import csv

# メソッド情報を保存するリスト
methods = []

def enterMethodDeclaration(self, ctx):
    method_name = ctx.IDENTIFIER().getText()
    methods.append({"Method": method_name})

# CSV出力
with open('output.csv', 'w', newline='') as csvfile:
    fieldnames = ['Method']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(methods)
```

**CSV 出力結果**:

```csv
Method
sayHello
add
```

---

## **まとめ**

ANTLR4 を利用して Java コードを解析する手順は以下の通りです：

1. **Java 文法ファイル（Java.g4）の取得**
2. **ANTLR4 を使って Lexer と Parser を生成**
3. **Python スクリプトを作成して構文解析**
4. **AST をトラバースし、情報を抽出（クラス、メソッド、呼び出し関係）**
5. **結果を表示または CSV ファイルに出力**

この手順により、Java コードの解析、依存関係の抽出、AST を用いた高度な解析が Python から実行できます。

`alias` は **Unix/Linux/macOS** 環境で使われるシェルコマンドで、Windows の **コマンドプロンプト**（CMD）ではサポートされていません。Windows 環境で ANTLR4 を設定する場合は、代わりに **環境変数** を利用します。

---

## **1. ANTLR4 コマンドの設定（Windows 環境）**

### **手順**

1. **ANTLR4 JAR ファイルをダウンロード**  
   [ANTLR4 公式サイト](https://www.antlr.org/download.html) から `antlr-4.x-complete.jar` をダウンロードします。

2. **JAR ファイルを保存**  
   ダウンロードした JAR ファイルを **`C:\tools\antlr`** など任意のディレクトリに保存します。  
   （例: `C:\tools\antlr-4.13.0-complete.jar`）

3. **環境変数を設定**

   - **システム環境変数**を編集して、以下の設定を追加します。

   **例: ANTLR のパス設定** LINUX

   - **名前**: `CLASSPATH`
   - **値**: `.;C:\tools\antlr-4.13.0-complete.jar`

   - **名前**: `ANTLR4`（任意）
   - **値**: `java -jar C:\tools\antlr-4.13.0-complete.jar`

4. **簡易コマンドエイリアスとしてバッチファイルを作成**  
   `antlr4.bat` ファイルを作成し、以下の内容を記述します。

   **antlr4.bat（ファイル内容）**

   ```bat
   @echo off
   java -jar C:\tools\antlr-4.13.0-complete.jar %*
   ```

   **grun.bat（オプション: GUI テスト用）**

   ```bat
   @echo off
   java org.antlr.v4.gui.TestRig %*
   ```

5. **バッチファイルの場所を PATH に追加**  
   `antlr4.bat` と `grun.bat` を保存したディレクトリ（例: `C:\tools`）を **PATH 環境変数** に追加します。

---

### **確認手順**

コマンドプロンプトを開き、以下のコマンドを実行します。

```cmd
antlr4 -version
```

出力結果:

```plaintext
ANTLR Parser Generator  Version 4.x
```

---

## **2. コマンドの実行例**

ANTLR4 の文法ファイルを Python 用にパーサーと Lexer を生成する例です。

```cmd
antlr4 -Dlanguage=Python3 Java9Lexer.g4 Java9Parser.g4 -o java_parser
```

### **説明**

- **`antlr4`**: `antlr4.bat` を呼び出して ANTLR4 を実行。
- **`-Dlanguage=Python3`**: Python 3 向けのコードを生成。
- **`Java9Lexer.g4 Java9Parser.g4`**: 文法ファイルの指定。
- **`-o java_parser`**: 生成されたファイルを `java_parser` ディレクトリに出力。

---

## **3. 注意点**

- コマンドプロンプトを **再起動** しないと環境変数が反映されません。
- **PowerShell**を利用する場合は、`function`を使って同様のエイリアス設定ができます。

**PowerShell 例**:

```powershell
function antlr4 { java -jar "C:\tools\antlr-4.13.0-complete.jar" $args }
```

---

## **まとめ**

- **`alias` コマンドは Windows CMD では利用できない**ため、バッチファイル（`antlr4.bat`）を作成することでエイリアスの代替ができます。
- **環境変数**（`CLASSPATH` と `PATH`）を正しく設定し、ANTLR4 を Windows 環境で使えるようにします。
