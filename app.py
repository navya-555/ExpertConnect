from flask import Flask, redirect, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
import base64
import json
import numpy as np
import threading
from utils.llm_func import process_resume_cv,process_gscholar,compute_infoSource_pair

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

class Expert_Emb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    resume_emb = db.Column(db.Text, nullable=False)  # Store as JSON
    cv_emb = db.Column(db.Text, nullable=True)       # Store as JSON
    gscholar_emb = db.Column(db.Text, nullable=True) # Store as JSON
    git_emb = db.Column(db.Text, nullable=True)      # Store as JSON

    def set_embeddings(self, resume_emb, cv_emb, gscholar_emb, git_emb):
        self.resume_emb = json.dumps(resume_emb)
        self.cv_emb = json.dumps(cv_emb) if cv_emb is not None else None
        self.gscholar_emb = json.dumps(gscholar_emb) if gscholar_emb is not None else None
        self.git_emb = json.dumps([emb for emb in git_emb]) if git_emb else None

    def get_embeddings(self):
        return {
            "resume_emb": json.loads(self.resume_emb),
            "cv_emb": json.loads(self.cv_emb) if self.cv_emb else None,
            "gscholar_emb": json.loads(self.gscholar_emb) if self.gscholar_emb else None,
            "git_emb": [emb for emb in json.loads(self.git_emb)] if self.git_emb else None
        }

class Candidate_Emb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    resume_emb = db.Column(db.Text, nullable=False)  # Store as JSON
    cv_emb = db.Column(db.Text, nullable=True)       # Store as JSON
    gscholar_emb = db.Column(db.Text, nullable=True) # Store as JSON
    git_emb = db.Column(db.Text, nullable=True)      # Store as JSON

    def set_embeddings(self, resume_emb, cv_emb, gscholar_emb, git_emb):
        self.resume_emb = json.dumps(resume_emb)
        self.cv_emb = json.dumps(cv_emb) if cv_emb is not None else None
        self.gscholar_emb = json.dumps(gscholar_emb) if gscholar_emb is not None else None
        self.git_emb = json.dumps([emb for emb in git_emb]) if git_emb else None

    def get_embeddings(self):
        return {
            "resume_emb": json.loads(self.resume_emb),
            "cv_emb": json.loads(self.cv_emb) if self.cv_emb else None,
            "gscholar_emb": json.loads(self.gscholar_emb) if self.gscholar_emb else None,
            "git_emb": [emb for emb in json.loads(self.git_emb)] if self.git_emb else None
        }


# Create the database tables
with app.app_context():
    db.create_all()


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

        threading.Thread(target=process_expert, args=(username,)).start()

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

        threading.Thread(target=process_candidate, args=(username,)).start()

        return redirect('/')


def process_expert(user_name):
    with app.app_context():
        expert=Expert.query.filter_by(username=user_name).first()

        user_name=expert.username

        if expert.resume:
            resume_emb=process_resume_cv(expert.resume)
        else:
            resume_emb=None

        if expert.cv:
            cv_emb=process_resume_cv(expert.cv)
        else:
            cv_emb=None

        if expert.google_scholar_link:
            gs_emb=process_gscholar(expert.google_scholar_link)
        else:
            gs_emb=None

        new_expert_embeddings = Expert_Emb(username=user_name)
        new_expert_embeddings.set_embeddings(resume_emb, cv_emb, gs_emb, None)
        db.session.add(new_expert_embeddings)
        db.session.commit()
    
def process_candidate(user_name):
    with app.app_context():
        candidate = Candidate.query.filter_by(username=user_name).first()

        user_name = candidate.username
        if candidate.resume:
            resume_emb = process_resume_cv(candidate.resume)
        else:
            resume_emb = None

        if candidate.cv:
            cv_emb = process_resume_cv(candidate.cv)
        else:
            cv_emb = None

        if candidate.google_scholar_link:
            gs_emb = process_gscholar(candidate.google_scholar_link)
        else:
            gs_emb = None

        git_emb = None

        # Create a new Candidate_Emb record and save the embeddings
        new_candidate_embeddings = Candidate_Emb(username=user_name)
        new_candidate_embeddings.set_embeddings(resume_emb, cv_emb, gs_emb, git_emb)
        db.session.add(new_candidate_embeddings)
        db.session.commit()


@app.route('/test')
def test():
    can=Candidate_Emb.query.filter_by(username='sufyan').first()
    exp=Expert_Emb.query.filter_by(username='Exp1').first()

    exp_emb=exp.get_embeddings()
    can_emb=can.get_embeddings()

    relevency_list=[]
    for can_field in can_emb.keys():
        if not can_emb[can_field]:
            continue
        field_score=[]
        for exp_field in exp_emb.keys():
            if not exp_emb[exp_field]:
                continue
            field_score.append(compute_infoSource_pair(can_emb[can_field],exp_emb[exp_field]))
        relevency_list.append(max(field_score))
    
    relevency_score=(np.mean(relevency_list))

    return str(relevency_score)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
