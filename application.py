import os
import datetime
import requests
from flask import Flask, session,render_template,request,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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

@app.route("/success",methods=["POST"])
def success():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    db.execute("INSERT INTO users (username, email,password) VALUES (:username, :email,:password)",
            {"username": username, "email": email,"password":password})
    db.commit()
    return render_template("success.html",message="Thanks for registering.")

@app.route("/sign_in",methods=["POST","GET"])
def sign_in():
    if request.method == "GET":
        return render_template("sign_in.html")
    username = request.form.get("username")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE username = :username and password = :password", {"username": username, "password":password}).rowcount !=0:
        user_details = db.execute("SELECT * FROM users WHERE username = :username and password = :password", {"username": username, "password":password}).fetchall()
        session["user_id"] = []
        session["user_id"].append(user_details[0].id)
        print(session["user_id"])
        return render_template('search.html')
    return render_template("error.html")
@app.route("/search",methods=["POST","GET"])
def search():
    isb = request.form.get("isb")
    isb1 = "%" + isb + "%"
    s = db.execute("select * from books where title like :title or author like :author or isbn like :isbn",{"title":isb1,"author":isb1,"isbn":isb1}).fetchall()
    #s = db.execute( "SELECT * from books WHERE isbn like :isb1",{"isb1":isb1}).fetchall()
    ''''if s is None:
        return render_template('error.html',message="Could not find anything. Please search with different title or author name or isbn no")
    '''
    return render_template('search.html',s = s)

@app.route("/book/<string:val>",methods=["POST","GET"])
def book(val):
    
    review = request.form.get("review")
    rating = request.form.get("rating")
    book_details = db.execute("select * from books where isbn =:isbn",{"isbn":val}).fetchall()
    review_details = db.execute("select * from reviews where book_id =:book_id",{"book_id":book_details[0].book_id}).fetchall()
    #b = book_details[0].isbn
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Amc7XHIh2hnyroPOqS4haQ", "isbns": val})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    avg_rating = data["books"][0]["average_rating"]
    work_ratings_count = data["books"][0]["work_ratings_count"]
    if review is not None and rating is not None:
        if db.execute("select * from reviews where book_id=:book_id and user_id=:user_id",{"book_id" : book_details[0].book_id,"user_id":session["user_id"][0]}).rowcount==0:
            db.execute("Insert into reviews(review,book_id,user_id,rating) values(:review,:book_id,:user_id,:rating)",{"review" : review,"book_id" : book_details[0].book_id,"user_id":session["user_id"][0],"rating" : rating})
            db.commit()
        else:
            return render_template('book.html',book_details=book_details,review_details=review_details,message="You have already submitted your review for this book.",avg_rating=avg_rating,work_ratings_count=work_ratings_count) 
    review_details = db.execute("select * from reviews where book_id =:book_id",{"book_id":book_details[0].book_id}).fetchall()
    return render_template('book.html',book_details=book_details,review_details=review_details,avg_rating=avg_rating,work_ratings_count=work_ratings_count)

@app.route("/api/<string:isbn>")
def book_api(isbn):
    

    # Make sure book exists.
    f = db.execute("select * from books where isbn=:isbn",{"isbn":isbn}).fetchall()
    f3 = db.execute("select * from books where isbn=:isbn",{"isbn":isbn}).rowcount
    if f3 == 0:
        return jsonify({"error": "Invalid book isbn number"}), 404
    #f1 = db.execute("SELECT avg(rating) as average_score,count(*) as Review_count FROM reviews group by book_id having book_id=:book_id",{"book_id":f[0].book_id}).fetchall()
    f1 = db.execute("select * from reviews where book_id=:book_id",{"book_id":f[0].book_id}).fetchall()
    r = db.execute("select * from reviews where book_id=:book_id",{"book_id":f[0].book_id}).rowcount
    sum=0
    for i in range(0,r):
        sum +=f1[i].rating
    f2 = sum/r
    return jsonify({
        "title": f[0].title,
        "author": f[0].author,
        "year": f[0].year,
        "isbn": f[0].isbn,
        "review_count": r,
        "average_score": f2
            })

"""def say_hello():
    if session.get("hi") is None:
        session["hi"] = []
    if request.method == "POST":
        name = request.form.get("name")
        session["hi"].append(name)
    
    return render_template("say_hello.html",hi=session["hi"])
@app.route("/index")
def index():
    #d1 = datetime.datetime.now()
    #newYear = d1.month == 1 and d1.date == 1
    return render_template("index.html")

@app.route("/morning",methods=["POST","GET"])
def morning():
    if request.method == "GET":
        return "<h1>Please submit the form</h1>"
    name = request.form.get("name")
    return render_template("morning.html",name=name)"""
