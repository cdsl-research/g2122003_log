from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL接続の設定
db = mysql.connector.connect(
    host='mysql-hoge',
    user='user',
    password='pass',
    database='flask_db'
)

cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS comments (id INT AUTO_INCREMENT PRIMARY KEY, comment TEXT)')

cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'comments' AND column_name = 'stamp'")
result = cursor.fetchone()
if result[0] == 0:
    # カラムが存在しない場合の処理
    cursor.execute('ALTER TABLE comments ADD COLUMN stamp INT DEFAULT 0')

@app.route('/')
def index():
    # コメントをデータベースから取得して表示する
    cursor = db.cursor()
    cursor.execute('SELECT * FROM comments')
    comments = cursor.fetchall()
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
