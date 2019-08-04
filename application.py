import os
import requests
import json
from flask import Flask, session,render_template,request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.debug=True
# DATABASE_URL="postgres://fvidljvruvkrzp:ffb41b6e98aff605a0fe67eec67a1b902f9199e8f57d9fa2c8f50a26e4e13537@ec2-174-129-41-127.compute-1.amazonaws.com:5432/d4vutjco33gbab"
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search",methods=["POST","GET"])
def log_in():
    print(request)
    if request.method=="POST":
        name=request.form.get("username")
        password=request.form.get("password")
        db.execute('''CREATE TABLE IF NOT EXISTS users(
            username VARCHAR NOT NULL,
            password VARCHAR,
            id SERIAL NOT NULL
        )''')
        db.commit()
        db.execute("INSERT INTO users(username,password) VALUES(:username,:password)",{"username":name,"password":password})
        print("inserted user %s"%name)
        db.commit()
        return render_template("search.html",username=name)
    else:
        return "Please log in first"

@app.route("/logout/<username>")
def log_out(username):
    print(username)
    db.execute("DELETE FROM users WHERE username=:name",{"name":username})
    db.commit()
    return "you've logged out"

@app.route("/result",methods=["POST"])
def search():
    search_str=request.form.get("wd")
    results=db.execute("SELECT * FROM books where isbn like :t  OR title like :t OR author like :t",{"t":"%"+search_str+"%"}).fetchall()
    print(db.query)
    db.commit()
    print(results)
    if results is None:
        return render_template("error.html")
    else:
        return render_template("search.html",results=results)


@app.route("/book/<isbn>",methods=["POST","GET"])
def get_book_detail(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "N3g1rlvCzMUIcPwnIiCMSA", "isbns":isbn})
    res2=db.execute("SELECT title,author,year FROM books where isbn=:isbn",{"isbn":isbn}).fetchone()
    db.commit()
    title=res2.title
    author=res2.author
    year=res2.year
    if request.method=="POST":
        if session.get("comments") is None:
            session["comments"]=[]    
        comment=request.form.get("comment")
        session["comments"].append(comment)
        # print("comment added")

    return render_template("book.html",book=res.json(),year=year,author=author,title=title,comments=session["comments"])

