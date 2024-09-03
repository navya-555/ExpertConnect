from flask import Flask,redirect,render_template
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

if __name__=="__main__":
    app.run(debug=True,port=5000)