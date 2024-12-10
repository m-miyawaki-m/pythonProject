import os

# 作業ディレクトリを変更
new_dir = "./sample/file"
os.chdir(new_dir)

print(f"変更後の作業ディレクトリ: {os.getcwd()}")

# 変更後のディレクトリにファイルを保存
with open("sample.txt", "w") as file:
    file.write("変更後のディレクトリに保存しました。")
