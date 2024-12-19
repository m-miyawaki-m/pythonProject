import javalang

def parse_logic_file(logic_file, dao_methods):
    """Logicファイルを解析し、DAOメソッドの呼び出しを検出"""
    call_relations = []

    with open(logic_file, "r", encoding="utf-8") as f:
        java_code = f.read()
    tree = javalang.parse.parse(java_code)

    class_name = None
    for path, node in tree:
        # Logicクラス名の検出
        if isinstance(node, javalang.tree.ClassDeclaration):
            class_name = node.name
            print(f"Class Found: {class_name}")  # デバッグ出力

        # Logicクラス内のメソッド検出
        elif isinstance(node, javalang.tree.MethodDeclaration):
            current_method = node.name
            print(f"Method Found: {current_method}")  # デバッグ出力

            # DAOメソッドの呼び出し検出
            for _, method_invocation in node.filter(javalang.tree.MethodInvocation):
                # qualifierがNoneの場合、memberのみで検出
                qualifier = method_invocation.qualifier if method_invocation.qualifier else ""
                dao_method_call = f"{qualifier}.{method_invocation.member}".strip(".")
                print(f"Detected Method Call: {dao_method_call}")  # デバッグ出力

                if dao_method_call in dao_methods:
                    mybatis_info = dao_methods[dao_method_call]
                    call_relations.append({
                        "業務操作": class_name,
                        "呼び出し元メソッド": current_method,
                        "呼び出し先メソッド": dao_method_call,
                        "DAO メソッド": mybatis_info["DAO メソッド"],
                        "CRUD 種別": mybatis_info["CRUD 種別"],
                        "MyBatis Namespace": mybatis_info["MyBatis Namespace"],
                        "MyBatis Id": mybatis_info["MyBatis Id"],
                        "パラメータ": mybatis_info["パラメータ"]
                    })
    return call_relations
