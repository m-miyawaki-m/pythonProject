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