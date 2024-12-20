from flask import Flask, render_template, request
import os
import json
import sqlparse

app = Flask(__name__)

# データ読み込み関数
def load_data():
    data_dir = os.path.join(os.getcwd(), "./sample/test100_flask/input")
    data = []
    if os.path.exists(data_dir):
        for file_name in os.listdir(data_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(data_dir, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    for row in file_data:
                        # SQLを整形
                        sql = row.get("sql", "")
                        formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
                        row["sql"] = formatted_sql
                        # 行数を計算して追加
                        row["line_count"] = len(formatted_sql.split("\n"))
                        data.append(row)
    return data

@app.route("/")
def index():
    # 検索時に毎回データを読み込む
    data = load_data()

    # 検索クエリを取得
    query = request.args.get("query", "").lower()

    # データをフィルタリング
    filtered_data = []
    for row in data:
        sql = row.get("sql", "").lower()
        file_name = row.get("file_name", "").lower()
        if query in sql or query in file_name:
            filtered_data.append(row)

    return render_template("index.html", data=filtered_data, query=query)

if __name__ == "__main__":
    app.run(debug=True)
