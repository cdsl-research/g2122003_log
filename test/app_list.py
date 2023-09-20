# ライブラリのインポートと初期化
from flask import Flask, render_template, request, redirect, jsonify, session
import requests
import mysql.connector
import sys
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションのセキュリティキー
app.config['JSON_AS_ASCII'] = False # <-- JSON文字化け対策

try:
    # MySQL接続の設定
    db = mysql.connector.connect(
        host='barque1.a910.tak-cslab.org',
        user='user',
        password='pass',
        database='flask_db',
        charset  = 'utf8mb4',
        port = 31953,
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
        cursor.execute('SELECT isbn,title,image FROM books')
        response_data = []
        for books in cursor.fetchall():
            response_data.append({'isbn': books[0], 'title': books[1], 'image': books[2]})
        print(response_data)
        books_list = {'books': response_data}
    except mysql.connector.errors.ProgrammingError as e:
        print("/ :", e)
        sys.exit(1)
    return jsonify(books_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
