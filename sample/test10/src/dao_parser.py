import javalang

# CRUD操作のマッピング
CRUD_METHODS = {
    "selectOne": "Read",
    "selectList": "Read",
    "insert": "Create",
    "update": "Update",
    "delete": "Delete",
}

def parse_dao_file(dao_file):
    """DAOファイルを解析し、MyBatisのnamespace, id, パラメータを取得"""
    dao_methods = {}

    with open(dao_file, "r", encoding="utf-8") as f:
        java_code = f.read()
    tree = javalang.parse.parse(java_code)

    class_name = None
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            class_name = node.name
        elif isinstance(node, javalang.tree.MethodDeclaration):
            method_name = node.name
            for _, method_invocation in node.filter(javalang.tree.MethodInvocation):
                if "sqlSession" in str(method_invocation.qualifier or ""):
                    called_method = method_invocation.member
                    namespace_id = method_invocation.arguments[0].value if isinstance(method_invocation.arguments[0], javalang.tree.Literal) else "-"
                    parameters = [str(arg) for arg in method_invocation.arguments[1:]]

                    namespace, id = "-", "-"
                    if "." in namespace_id:
                        namespace, id = namespace_id.split(".")

                    # クラス名の先頭を小文字に変換
                    class_name_modified = class_name[:1].lower() + class_name[1:]

                    # DAOメソッド情報を格納
                    dao_methods[f"{class_name_modified}.{method_name}"] = {
                        "DAO メソッド": called_method,
                        "CRUD 種別": CRUD_METHODS.get(called_method, "-"),
                        "MyBatis Namespace": namespace,
                        "MyBatis Id": id,
                        "パラメータ": ", ".join(parameters)
                    }
    return dao_methods
