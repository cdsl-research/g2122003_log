# ライブラリのインポートと初期化
from flask import Flask, render_template, request, redirect, jsonify, session, flash
import requests
import mysql.connector
import sys
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションのセキュリティキー
app.config['JSON_AS_ASCII'] = False  # JSON文字化け対策

try:
    # MySQL接続の設定
    db = mysql.connector.connect(
        host='barque1.a910.tak-cslab.org',
        user='user',
        password='pass',
        database='flask_db',
        charset='utf8mb4',
        port=31953,
        auth_plugin='mysql_native_password',  # mysql.connector.errors.NotSupportedError: Authentication plugin 'caching_sha2_password' is not supported 防止
    )

    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS books (`isbn` BIGINT PRIMARY KEY, `title` TEXT, `author` TEXT, `image` TEXT, `check` BOOLEAN, `publisher_date` TEXT, `description` TEXT, `post_number` INT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS sequels (id INT AUTO_INCREMENT PRIMARY KEY, main_novel_id BIGINT, sequel_novel_id BIGINT)')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            isbn BIGINT,
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
        print("db.is_connected():", db.is_connected())

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


@app.route('/novel/id<int:novel_id>')
def novel_detail(novel_id):
    # MySQLから小説の詳細情報を取得するクエリを実行します
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM sequels  WHERE `main_novel_id` = %s', (novel_id,))
    novel_list = cursor.fetchall()
    # image_list = []
    # for novel in novel_list:
    # cursor.execute('SELECT image FROM books  WHERE `main_novel_id` = %s', (novel,))
    # image_list.append(cursor.fethone())

    cursor.execute('SELECT * FROM books WHERE `isbn` = %s AND `check` = 1', (novel_id,))
    novel = cursor.fetchone()
    print(novel)

    review_page = {'novel': novel}
    cursor.execute('SELECT * FROM reviews WHERE `isbn` = %s', (novel_id,))
    reviews = cursor.fetchall()
    review_page.update({'review': reviews})

    return jsonify(review_page)

# 書籍を登録している.
@app.route('/register', methods=['GET', 'POST'])    # 登録ページに確認の内容を返してあげる
def register():
    print("input_data!!!")
    if request.method == 'POST':
        print("post!!!")
        isbn = request.form['isbn']
        print("isbn")
        is_check = request.form.get('checkboxName')
        print("check")
        print(is_check)
        volume1_isbn = request.form.get('volume1_isbn')
        if is_check == "on":
            check = "はい"
            volume1_title = ""  # チェックがついている場合、第1巻のタイトルは空
        else:
            check = "いいえ"
            # 第1巻のISBNを使用してGoogle Books APIから第1巻のタイトルを取得
            volume1_title = fetch_volume1_title(volume1_isbn)

        # Google Books APIから主要な情報を取得
        url = "https://www.googleapis.com/books/v1/volumes?"
        payload = {"q": "isbn:" + str(isbn)}
        r = requests.get(url, params=payload)
        print(json.dumps(r.json(), indent=2))
        results = r.json()
        volume_info = results["items"][0]["volumeInfo"]
        title = volume_info.get("title", "")
        authors = volume_info.get("authors", [])
        published_date = volume_info.get("publishedDate", "")
        description = volume_info.get("description", "")
        thumbnail = volume_info.get("imageLinks", {}).get("thumbnail", "")

        # 抽出したデータを表示
        print("Title:", title)
        print("Authors:", ", ".join(authors))
        print("Published Date:", published_date)
        print("Description:", description)
        print("Thumbnail URL:", thumbnail)

        # ユーザーからデータを受け取り、セッションに保存
        session['data'] = {
            'isbn': str(isbn),
            'check': check,
            'is_check': is_check,
            'title': title,
            'authors': ",".join(authors),
            'published_date': published_date,
            'description': description,
            'image': thumbnail,
            'volume1_title': volume1_title,  # 第1巻のタイトルをセッションに追加
            'volume1_isbn': volume1_isbn,
            # 他のデータフィールドも同様に取得
        }
        return redirect('/confirm')  # 確認画面にリダイレクト
        check = jsonify(session['data'])
        print(check)
        return check
    else:
        print("not post!")

    return render_template('register.html') # ここをjsonの形式直した状態で送り返してあげる

# registerのときに, 1巻のタイトル情報取得.
def fetch_volume1_title(volume1_isbn): # GoogleAPI -> DBに聞き返す.
    url = "https://www.googleapis.com/books/v1/volumes?"
    payload = {"q": "isbn:" + str(volume1_isbn)}

    r = requests.get(url, params=payload)
    results = r.json()
    if "items" in results and len(results["items"]) > 0:
        volume_info = results["items"][0]["volumeInfo"]
        title = volume_info.get("title", "")
        thumbnail = volume_info.get("imageLinks", {}).get("thumbnail", "")
        return title
    return "情報なし"  # 第1巻が見つからない場合のデフォルト値


# ここで最終的な登録を行っている.
@app.route('/confirm', methods=['GET', 'POST'])
def confirm_data():
    data = session.get('data')  # セッションからデータを取得
    if not data:
        return redirect('/register')  # データがない場合は入力画面にリダイレクト


    if request.method == 'POST':
        # ユーザーが確認画面でデータを承認した場合、データをデータベースに保存
        # ここでデータベースへの保存処理を実行
        # 保存が成功した場合、セッションからデータを削除

        # コネクションが切れた時に再接続してくれるよう設定
        db.ping(reconnect=True)
        # 接続できているかどうか確認
        print("db.is_connected():",db.is_connected())

        cursor = db.cursor()
        cursor.execute('SELECT MAX(post_number) FROM books')
        result = cursor.fetchone()
        # もし値が存在しない場合、0を代入
        num = result[0] if result[0] is not None else 0
        post_number = num + 1
        print("data['is_check']: ", data['is_check'])
        if data['is_check'] == "on":
            check = True
        else:
            check = False
            print(data['volume1_isbn'])
            cursor.execute('INSERT INTO sequels (main_novel_id, sequel_novel_id) VALUES (%s, %s)', (int(data['volume1_isbn']), int(data['isbn'])))
            db.commit()

        print("register MySQL")
        cursor.execute('INSERT INTO books (`isbn`, `title`, `author`, `image`, `check`, `publisher_date`, `description`, `post_number`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (data['isbn'], data['title'], data['authors'], data['image'], check, data['published_date'], data['description'], post_number))
        db.commit()
        
        session.pop('data', None)
        return redirect('/comp')  # 保存が成功したらホームページにリダイレクト

    return render_template('confirm.html', data=data) # data=data がreturnの値(jsonfy(data)) -> 確認取れているかどうか

# 登録完了画面どうするか
@app.route('/comp', methods=['GET'])
def comp_data():
    return render_template('comp-of-registration.html')

# review投稿させている.
@app.route('/novel/id<int:novel_id>/review', methods=['POST'])
def add_review(novel_id):
    # フォームから新しい情報を受け取る
    comment = request.form.get('comment')
    user_id = 1  # 仮のユーザーID、必要に応じて変更
    review_type = request.form.get('review_type')
    spoiler_alert = bool(request.form.get('spoiler_alert'))

    # レビューをデータベースに保存する
    cursor = db.cursor()
    cursor.execute('INSERT INTO reviews (novel_id, user_id, comment, review_type, spoiler_alert) VALUES (%s, %s, %s, %s, %s)', (novel_id, user_id, comment, review_type, spoiler_alert))
    db.commit()
    return redirect(f'/novel/id{novel_id}') # React側でリダイレクト行ってもらう. (投稿したよという確認メッセージ返すことぐらいあってもいいかも.(なくてもいい))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)