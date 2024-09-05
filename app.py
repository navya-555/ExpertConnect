from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import base64

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Main.db'  # SQLite database in the project root directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

class Expert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    photo = db.Column(db.LargeBinary, nullable=False)
    resume = db.Column(db.LargeBinary, nullable=False)
    cv = db.Column(db.LargeBinary, nullable=True)
    google_scholar_link = db.Column(db.String(200), nullable=True)
    github_link = db.Column(db.String(200), nullable=True)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    photo = db.Column(db.LargeBinary, nullable=False)
    resume = db.Column(db.LargeBinary, nullable=False)
    cv = db.Column(db.LargeBinary, nullable=True)
    google_scholar_link = db.Column(db.String(200), nullable=True)
    github_link = db.Column(db.String(200), nullable=True)


# Create the database tables
#with app.app_context():
#    db.create_all()


@app.template_filter('b64encode')
def b64encode_filter(data):
    """Encode binary data to base64 for displaying images or downloadable files."""
    if data is None:
        return ""
    return base64.b64encode(data).decode('utf-8')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    experts = Expert.query.all()
    candidates = Candidate.query.all()
    return render_template("dashboard.html",experts=experts,candidates=candidates)

@app.route('/logout')
def logout():
    return redirect("/")

@app.route('/candidate_form')
def candidate_form():
    return render_template("candidate_form.html")

@app.route('/add_expert', methods=['GET', 'POST'])
def add_expert():
    if request.method == 'POST':
        # Get form data
        name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']

        # Handle file uploads
        photo = request.files['photo']
        resume = request.files['resume']
        cv = request.files['cv'] if 'cv' in request.files else None

        # Read file data and save to the database
        photo_data = photo.read()
        resume_data = resume.read()
        cv_data = cv.read() if cv else None

        # Create a new Expert record without filenames
        new_expert = Expert(
            name=name,
            username=username,
            email=email,
            phone=phone,
            photo=photo_data,
            resume=resume_data,
            cv=cv_data,
            google_scholar_link=request.form.get('googleScholarLink'),
            github_link=request.form.get('githubLink')
        )

        # Add the record to the session and commit to the database
        db.session.add(new_expert)
        db.session.commit()

        # Redirect to dashboard or any other page
        return redirect('/dashboard')


@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']

        # Handle file uploads
        photo = request.files['photo']
        resume = request.files['resume']
        cv = request.files['cv'] if 'cv' in request.files else None

        # Read file data and save to the database
        photo_data = photo.read()
        resume_data = resume.read()
        cv_data = cv.read() if cv else None

        # Create a new Candidate record
        new_candidate = Candidate(
            name=name,
            username=username,
            email=email,
            phone=phone,
            photo=photo_data,
            resume=resume_data,
            cv=cv_data,
            google_scholar_link=request.form.get('google-scholar'),
            github_link=request.form.get('github')
        )

        # Add the record to the session and commit to the database
        db.session.add(new_candidate)
        db.session.commit()

        return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
