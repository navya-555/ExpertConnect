import google.generativeai as genai
import os
from utils.scrapers import gscholar_scraper, github_scraper
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from io import BytesIO

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API"])
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
emb_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')



def extract_text_from_pdf(pdf_data):
  # Create a BytesIO stream from the binary data
    pdf_stream = BytesIO(pdf_data)
    reader = PdfReader(pdf_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def skill_domain_from_txt(text,model=gemini_model):
    prompt = f"""
    You are analyzing a candidate's resume. Identify the key skills and domains based on their resume. Do not include any other information. Also make sure you only highlight prominent skills.

    Output only the keywords for:
    Skills: (e.g., Object Detection, OpenCV, Python)
    Domains: (e.g., Computer Vision, Machine Learning)

    You are supposed to follow these instructions while giving the output strictly.
    1. Don't write anything else apart from skills and domain.
    2. Use only ',' for separating two skills or domains.
    3. Strictly follow the output format of the sample output.

    Sample output:
    Object Detection, OpenCV, Python
    Computer Vision, Machine Learning
    """
    
    response = model.generate_content([prompt, text])
    output = response.text.strip().split('\n')
    return output

def skill_domain_from_job_des(text,model=gemini_model):
    prompt = f"""
    You are analyzing a job description. Identify the key skills and domains based on the description. Do not include any other information. Also make sure you only highlight prominent skills.

    Output only the keywords for:
    Skills: (e.g., Object Detection, OpenCV, Python)
    Domains: (e.g., Computer Vision, Machine Learning)

    You are supposed to follow these instructions while giving the output strictly.
    1. Don't write anything else apart from skills and domain.
    2. Use only ',' for separating two skills or domains.
    3. Strictly follow the output format of the sample output.

    Sample output:
    Object Detection, OpenCV, Python
    Computer Vision, Machine Learning
    """
    
    response = model.generate_content([prompt, text])
    output = response.text.strip().split('\n')
    return output

def skill_domain_from_readme(text,model=gemini_model):
    prompt = f"""
    You are analyzing a github project readme . Identify the key skills and domains based on the description. Do not include any other information. Also make sure you only highlight prominent skills.

    Output only the keywords for:
    Skills: (e.g., Object Detection, OpenCV, Python)
    Domains: (e.g., Computer Vision, Machine Learning)

    You are supposed to follow these instructions while giving the output strictly.
    1. Don't write anything else apart from skills and domain.
    2. Use only ',' for separating two skills or domains.
    3. Strictly follow the output format of the sample output.

    Sample output:
    Object Detection, OpenCV, Python
    Computer Vision, Machine Learning
    """
    
    response = model.generate_content([prompt, text])
    output = response.text.strip().split('\n')
    return output

def similarity_score(tup1,tup2):
    skill_similarity = cosine_similarity([tup1[0]], [tup2[0]])
    domain_similarity = cosine_similarity([tup1[1]], [tup2[1]])

    similarity = (0.4 * skill_similarity) + (0.6 * domain_similarity)
    return similarity

def compute_infoSource_pair(source1,source2):
    if(len(source1)==2 and len(source2)==2):
        return similarity_score(source1,source2)[0][0]
    elif (len(source1)==2):
        return max(cosine_similarity([source1[0]],[source2]),cosine_similarity([source1[1]],[source2]))[0][0]
    elif (len(source2)==2):
        return max(cosine_similarity([source1],[source2[0]]),cosine_similarity([source1],[source2[1]]))[0][0]
    else:
        return cosine_similarity([source1],[source2])[0][0]


def generate_embeddings(string,model=emb_model):
    embeddings = model.encode(string)
    return embeddings.tolist()

def process_resume_cv(pdf_data):
    text=extract_text_from_pdf(pdf_data)
    skill_domain=skill_domain_from_txt(text)
    emb=[generate_embeddings(skill_domain[0]),generate_embeddings(skill_domain[1])]
    return emb

def process_job_des(pdf_data):
    text=extract_text_from_pdf(pdf_data)
    skill_domain=skill_domain_from_job_des(text)
    emb=[generate_embeddings(skill_domain[0]),generate_embeddings(skill_domain[1])]
    return emb

def process_gscholar(url):
    domain=gscholar_scraper(url)
    emb=generate_embeddings(domain)
    return emb

def process_github(url):
    readmes=github_scraper(url)
    project_embs=[]
    for readme in readmes:
        skill_domain=skill_domain_from_readme(readme)
        emb=[generate_embeddings(skill_domain[0]),generate_embeddings(skill_domain[1])]
        project_embs.append(emb)
    return project_embs