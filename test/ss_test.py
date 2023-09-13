from flask import Flask, render_template, request, redirect, session
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションの秘密鍵を設定

@app.route('/input', methods=['GET', 'POST'])
def input_data():
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

