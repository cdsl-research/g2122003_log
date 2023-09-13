from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションの秘密鍵を設定

@app.route('/input', methods=['GET', 'POST'])
def input_data():
    if request.method == 'POST':
        # ユーザーからデータを受け取り、セッションに保存
        session['data'] = {
            'title': request.form['title'],
            'author': request.form['author'],
            # 他のデータフィールドも同様に取得
        }
        return redirect('/confirm')  # 確認画面にリダイレクト
    return render_template('input.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm_data():
    data = session.get('data')  # セッションからデータを取得
    if not data:
        return redirect('/input')  # データがない場合は入力画面にリダイレクト

    if request.method == 'POST':
        # ユーザーが確認画面でデータを承認した場合、データをデータベースに保存
        # ここでデータベースへの保存処理を実行
        # 保存が成功した場合、セッションからデータを削除
        session.pop('data', None)
        return redirect('/')  # 保存が成功したらホームページにリダイレクト

    return render_template('confirm.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)

