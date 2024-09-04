from flask import Flask,redirect,render_template,request, session
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)



@app.route('/')
def index():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/logout')
def logout():
    return redirect("/")

@app.route('/candidate_form')
def candidate_form():
    return render_template("candidate_form.html")

if __name__=="__main__":
    app.run(debug=True,port=5000)