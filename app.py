from flask import Flask, redirect, render_template, request, Response,flash
from flask_sqlalchemy import SQLAlchemy
import base64
import json
import numpy as np
import threading
from utils.llm_func import process_resume_cv,process_gscholar,compute_infoSource_pair,process_job_des,process_github

app = Flask(__name__)
app.config['SECRET_KEY'] = "apppication"

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


class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    jd = db.Column(db.LargeBinary, nullable=False)
    jd_emb = db.Column(db.Text, nullable=False)

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
    jobs=Jobs.query.all()
    return render_template("dashboard.html",experts=experts,candidates=candidates,experts_scores=None,
                           candidate=None,jobs=jobs)

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
        try:
            photo_data = photo.read()
        except:
            photo_data=None
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
    return redirect('/dashboard')

@app.route('/add_candidate', methods=['GET', 'POST'])
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
    return redirect('/')

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    job_title = request.form.get('username')
    jd_file = request.files['jd']
    jd_data = jd_file.read()
    emb=process_job_des(jd_data)
    jd_embedding = json.dumps(emb)

    new_job = Jobs(title=job_title, jd=jd_data, jd_emb=jd_embedding)

    db.session.add(new_job)
    db.session.commit()
    return redirect('/dashboard')

@app.route('/match', methods=['POST'])
def match():
    can_username = request.form.get('username')
    candidate=Candidate.query.filter_by(username=can_username).first()
    if candidate is None:
        return redirect('/dashboard')

    jd_file = request.files['jd']
    jd_data = jd_file.read()
    experts_list=jd_expert_score(jd_data)
    if len(experts_list)>10:
        experts_list=experts_list[:10]
    
    experts_scores=[]
    for exp_username,jd_score in experts_list:
        rel_score=candidate_expert_score(can_username,exp_username)

        rel_score = round(rel_score * 100, 3)
        jd_score = round(jd_score * 100, 3)

        experts_scores.append((exp_username,rel_score,jd_score))
    
    experts_scores=sorted(experts_scores, key=lambda x: x[1], reverse=True)

    experts = Expert.query.all()
    candidates = Candidate.query.all()
    return render_template("dashboard.html",experts=experts,candidates=candidates,experts_scores=experts_scores,candidate=candidate)

@app.route('/expert/photo/<username>')
def get_expert_photo(username):
    expert = Expert.query.filter_by(username=username).first()
    if expert and expert.photo:
        return Response(expert.photo, mimetype='image/jpeg')  # Adjust mimetype as needed (e.g., image/png)

@app.route('/candidate/photo/<username>')
def get_candidate_photo(username):
    candidate = Candidate.query.filter_by(username=username).first()
    if candidate and candidate.photo:
        return Response(candidate.photo, mimetype='image/jpeg')  # Adjust mimetype as needed (e.g., image/png)

@app.route('/delete_candidate/<int:id>')                  
def delete_candidate(id):

    candidate = Candidate.query.filter_by(id=id).first()
    db.session.delete(candidate)
    db.session.commit()
    return redirect("/dashboard")

@app.route('/delete_expert/<int:id>')                  
def delete_expert(id):
  
    expert = Expert.query.filter_by(id=id).first()
    expert_emb=Expert_Emb.query.filter_by(id=id).first()
    candidate_emb=Candidate_Emb.query.filter_by(id=id).first()
    db.session.delete(expert)
    db.session.delete(expert_emb)
    db.session.delete(candidate_emb)
    db.session.commit()
    return redirect("/dashboard")

@app.route('/delete_job/<int:id>')                  
def delete_job(id):
    job=Jobs.query.filter_by(id=id).first()
    db.session.delete(job)
    db.session.commit()
    return redirect("/dashboard")


@app.route('/cdashboard')
def cdashboard():
    return render_template("/Candidate_dashboard.html")


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

        if expert.github_link:
            git_emb=process_github(expert.google_scholar_link)
        else:
            git_emb=None

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

        if candidate.github_link:
            git_emb=process_github(candidate.google_scholar_link)
        else:
            git_emb=None

        # Create a new Candidate_Emb record and save the embeddings
        new_candidate_embeddings = Candidate_Emb(username=user_name)
        new_candidate_embeddings.set_embeddings(resume_emb, cv_emb, gs_emb, None)
        db.session.add(new_candidate_embeddings)
        db.session.commit()

def candidate_expert_score(can_username,exp_username):
    can=Candidate_Emb.query.filter_by(username=can_username).first()
    exp=Expert_Emb.query.filter_by(username=exp_username).first()

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

    return (relevency_score)

def jd_expert_score(jd_data):
    jd_emb=process_job_des(jd_data)

    experts=Expert_Emb.query.all()

    expert_list=[]
    for expert in experts:
        exp_emp=expert.get_embeddings()
        score_list=[]
        for source in exp_emp.keys():
            if not exp_emp[source]:
                continue
            score_list.append(compute_infoSource_pair(jd_emb,exp_emp[source]))
        expert_list.append((expert.username,
                            max(score_list)))
        
    return sorted(expert_list, key=lambda x: x[1], reverse=True)

if __name__ == "__main__":
    app.run(debug=True, port=5500)
