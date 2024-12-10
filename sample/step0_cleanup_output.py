import os
import shutil
from datetime import datetime

# 定数
OUTPUT_DIR = "sample/output/"
BK_DIR = os.path.join(OUTPUT_DIR, "bk")
MAX_BACKUPS = 5


# JSONファイルをバックアップに移動する関数
def backup_json_files():
    # 出力ディレクトリをチェック
    if not os.path.exists(OUTPUT_DIR):
        print(f"{OUTPUT_DIR} ディレクトリが存在しません。")
        return

    # バックアップ先ディレクトリを作成
    os.makedirs(BK_DIR, exist_ok=True)

    # 現在の日時をフォーマットしてサブディレクトリ名に使用
    current_time = datetime.now().strftime("%Y%m%d%H%M")
    backup_dir = os.path.join(BK_DIR, current_time)
    os.makedirs(backup_dir, exist_ok=True)

    # JSONファイルを移動
    for file_name in os.listdir(OUTPUT_DIR):
        if file_name.endswith(".json"):
            source_path = os.path.join(OUTPUT_DIR, file_name)
            destination_path = os.path.join(backup_dir, file_name)
            shutil.move(source_path, destination_path)
            print(f"{file_name} を {backup_dir} に移動しました。")

    # 古いバックアップを削除
    cleanup_old_backups()


# 古いバックアップを削除する関数
def cleanup_old_backups():
    # バックアップディレクトリ内のサブディレクトリを取得
    backups = [
        d for d in os.listdir(BK_DIR) if os.path.isdir(os.path.join(BK_DIR, d))
    ]
    backups.sort()  # 古い順に並べ替え

    # 保持数を超えた古いバックアップを削除
    while len(backups) > MAX_BACKUPS:
        oldest_backup = backups.pop(0)
        oldest_backup_path = os.path.join(BK_DIR, oldest_backup)
        shutil.rmtree(oldest_backup_path)
        print(f"古いバックアップ {oldest_backup_path} を削除しました。")


if __name__ == "__main__":
    backup_json_files()
