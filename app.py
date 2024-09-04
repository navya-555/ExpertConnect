from flask import Flask,redirect,render_template,request, session
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///expert.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


class Expert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    fullName = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    file1= db.Column(db.LargeBinary)
    file2= db.Column(db.LargeBinary)
    file3= db.Column(db.LargeBinary)
    link1 = db.Column(db.String(255), nullable=True)
    link2 = db.Column(db.String(255), nullable=True)



@app.route('/add_expert', methods=['GET', 'POST'])
def expertAdd_page():
    if request.method == 'POST':
        full_name = request.form['Fullname']
        username= request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        img_data = request.files['photo'].read() if 'photo' in request.files else None
        link1 = request.form['googleScholarLink']
        link2 = request.form['githubLink']
        new_expert = Expert(full_name=full_name, username=username,email=email,phone=phone,img_data=img_data,link1=link1,link2=link2) 
        db.session.add(new_expert)
        db.session.commit()
        print("Added")




@app.route('/')
def index():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/logout')
def logout():
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True,port=5000)