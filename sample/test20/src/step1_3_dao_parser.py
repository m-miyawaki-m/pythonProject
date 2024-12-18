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
