# ライブラリのインポートと初期化
from flask import Flask, render_template, request, redirect, jsonify, session
import requests
import mysql.connector
import sys

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションのセキュリティキー

try:
    # MySQL接続の設定
    db = mysql.connector.connect(
        host='mysql-hoge',
        user='user',
        password='pass',
        database='flask_db'
    )
    
    
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS comments (id INT AUTO_INCREMENT PRIMARY KEY, comment TEXT)')
    
    cursor.execute('CREATE TABLE IF NOT EXISTS books (`isbn` BIGINT PRIMARY KEY, `title` TEXT, `author` TEXT, `image` TEXT, `check` BOOLEAN, `publisher_date` TEXT, `description` TEXT, `post_number` INT)')
    cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'comments' AND column_name = 'stamp'")
    result = cursor.fetchone()
    if result[0] == 0:
        # カラムが存在しない場合の処理
        cursor.execute('ALTER TABLE comments ADD COLUMN stamp INT DEFAULT 0')
    print("create Tables!!!!!")
except mysql.connector.errors.ProgrammingError as e:
    print("first run : ", e)
    sys.exit(1)

@app.route('/')
def index():
    print("start index()!!!!!")
    try:
        # コネクションが切れた時に再接続してくれるよう設定
        db.ping(reconnect=True)
        # 接続できているかどうか確認
        print("db.is_connected():",db.is_connected())

        # コメントをデータベースから取得して表示する
        cursor = db.cursor()
        cursor.execute('SELECT * FROM comments')
        comments = cursor.fetchall()
    except mysql.connector.errors.ProgrammingError as e:
        print("/ :", e)
        sys.exit(1)
    return render_template('index.html', comments=comments)

@app.route('/comment', methods=['POST'])
def add_comment():
    # コメントをフォームから受け取り、データベースに保存する
    comment = request.form.get('comment')
    cursor = db.cursor()
    cursor.execute('INSERT INTO comments (comment) VALUES (%s)', (comment,))
    db.commit()
    return redirect('/')

@app.route('/stamp/<int:comment_id>', methods=['POST'])
def stamp_comment(comment_id):
    cursor = db.cursor()
    cursor.execute('UPDATE comments SET stamp = 1 WHERE id = %s', (comment_id,))
    db.commit()
    return jsonify({'success': True})

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("input_data!!!")
    if request.method == 'POST':
        print("post!!!")
        isbn = request.form['isbn']
        print("isbn")
        is_check = request.form.get('checkboxName')
        print("check")
        print(is_check)
        if is_check == "on":
            check = "はい"
        else:
            check = "いいえ"
        url = "https://www.googleapis.com/books/v1/volumes?"
        payload = {"q": "isbn:"+str(isbn)}

        r = requests.get(url, params=payload)
        #print(json.dumps(r.json(), indent=2))
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
            # 他のデータフィールドも同様に取得
        }
        return redirect('/confirm')  # 確認画面にリダイレクト
    return render_template('input.html')

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
        if data['is_check'] == "on":
            check = True
        else:
            check = False
        print("register MySQL")
        cursor.execute('INSERT INTO books (`isbn`, `title`, `author`, `image`, `check`, `publisher_date`, `description`, `post_number`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (data['isbn'], data['title'], data['authors'], data['image'], check, data['published_date'], data['description'], post_number))
        db.commit()
        session.pop('data', None)
        return redirect('/comp')  # 保存が成功したらホームページにリダイレクト

    return render_template('confirm.html', data=data)

@app.route('/comp', methods=['GET'])
def comp_data():
    return render_template('comp-of-registration.html')




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
