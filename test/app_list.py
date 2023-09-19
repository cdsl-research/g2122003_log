# ライブラリのインポートと初期化
from flask import Flask, render_template, request, redirect, jsonify, session
import requests
import mysql.connector
import sys
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションのセキュリティキー

try:
    # MySQL接続の設定
    db = mysql.connector.connect(
        host='mysql-hoge.novel-back-end.svc.cluster.local',
        user='user',
        password='pass',
        database='flask_db'
        charset  = 'utf8mb4'
    )
    
    
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS books (`isbn` BIGINT PRIMARY KEY, `title` TEXT, `author` TEXT, `image` TEXT, `check` BOOLEAN, `publisher_date` TEXT, `description` TEXT, `post_number` INT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS sequels (id INT AUTO_INCREMENT PRIMARY KEY, main_novel_id BIGINT, sequel_novel_id BIGINT)')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            novel_id BIGINT,
            user_id INT,
            comment TEXT,
            post_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            review_type ENUM("book", "web", "both"),
            spoiler_alert BOOLEAN
        )
    ''')
except mysql.connector.errors.ProgrammingError as e:
    print("first run : ", e)
    sys.exit(1)

@app.route('/books', methods=['GET'])
def index():
    print("start index()!!!!!")
    try:
        # コネクションが切れた時に再接続してくれるよう設定
        db.ping(reconnect=True)
        # 接続できているかどうか確認
        print("db.is_connected():",db.is_connected())

        # 書籍をデータベースから取得して表示する
        cursor = db.cursor()
        cursor.execute('SELECT title,isbn FROM books')
        books = cursor.fetchall()
    except mysql.connector.errors.ProgrammingError as e:
        print("/ :", e)
        sys.exit(1)
    return json.dumps(books, indent=4)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
