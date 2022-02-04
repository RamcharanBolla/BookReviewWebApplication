import os
import datetime
from flask import Flask, session,render_template,request
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
        
        return render_template('success.html',message="Thanks for signing in.",username="username",password="password")
    return render_template("error.html")
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
