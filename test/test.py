import requests
import json

isbn = 9784041041772
url = "https://www.googleapis.com/books/v1/volumes?"
payload = {"q": "isbn:"+str(isbn)}

r = requests.get(url, params=payload)
print(json.dumps(r.json(), indent=2))
results = r.json()
#print(results["items"])
#items = results["items"] 
#volumeInfo = items["volumeInfo"]
#title = volumeInfo["title"]
#authors = volumeInfo["authors"]
#publishedDat = volumeInfo["publishedDate"]
#description = volumeInfo["description"]
#imageLinks = items["imageLinks"]
#thumbnail = imageLinks["thumbnail"]
#print("title:", title)
#print("authors:", authors)
#print("publishedDate:", publishedDate)
#print("description:",description) 
#print("image:", thumbnail)
# 必要なデータを抽出
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

# MySQL接続の設定
db = mysql.connector.connect(
    host='mysql-hoge',
    user='user',
    password='pass',
    database='flask_db'
)

check = true

cursor = db.cursor()
cursor.execute('SELECT MAX(post_number) FROM books')
result = cursor.fetchone()
# もし値が存在しない場合、0を代入
num = result[0] if result[0] is not None else 0
post_number = num + 1
cursor.execute('INSERT INTO books (isbn, title, author, image, check, publicer_date, description, post_number) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (isbn, title, ",".join(authors), thumbnail, check, publicer_date, description, post_number))
db.commit()
