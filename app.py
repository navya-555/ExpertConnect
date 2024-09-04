from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import base64

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///experts.db'  # SQLite database in the project root directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the Expert model without filename fields
class Expert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
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

# Custom Jinja2 filter to base64 encode binary data
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
    return render_template("dashboard.html",experts=experts)

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
        full_name = request.form['full_name']
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
            full_name=full_name,
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
