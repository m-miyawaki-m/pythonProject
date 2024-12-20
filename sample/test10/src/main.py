from dao_parser import parse_dao_file
from logic_parser import parse_logic_file
from crud_csv_writer import save_to_csv

if __name__ == "__main__":
    logic_file = "./sample/test10/input/UserLogic.java"  # Logicファイル
    dao_file = "./sample/test10/input/UserDao.java"  # DAOファイル
    output_csv = "./sample/test10/output/crud_output_with_namespace_id.csv"

    # DAOファイル解析
    dao_methods = parse_dao_file(dao_file)
    print("DAOファイルの解析が完了しました。")

    # Logicファイル解析
    print(dao_methods)
    call_relations = parse_logic_file(logic_file, dao_methods)
    print("Logicファイルの解析が完了しました。")

    # CSV出力
    print(call_relations)
    save_to_csv(output_csv, call_relations)
    print(f"CRUD情報をCSVに出力しました: {output_csv}")
