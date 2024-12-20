import xml.etree.ElementTree as ET
import os

def analyze_xml(file_path):
    """
    MyBatis XMLファイルを解析し、指定された情報を抽出します。

    Args:
        file_path (str): 解析対象のXMLファイルのパス。

    Returns:
        list: 抽出結果のリスト。各エントリは辞書形式。
    """
    results = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        file_name = os.path.basename(file_path)  # ファイル名を取得

        # <mapper> タグの namespace 属性を取得
        namespace = root.attrib.get("namespace", "N/A")

        # MyBatis タグを解析
        for element in root.findall(".//"):
            if element.tag in {"select", "insert", "update", "delete"}:
                tag_info = {
                    "file_name": file_name,
                    "namespace": namespace,  # namespace を追加
                    "tag": element.tag,
                    "id": element.attrib.get("id", "N/A"),
                    "sql": "".join(element.itertext()).strip()
                }
                results.append(tag_info)
    except ET.ParseError as e:
        print(f"XML解析エラー: {file_path} - {e}")

    return results