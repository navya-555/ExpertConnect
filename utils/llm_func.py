import google.generativeai as genai
import os
import PyPDF2
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API"])
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
emb_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')



def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text




def skill_domain_from_txt(text,model):
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




def similarity_score(tup1,tup2):

    skill_similarity = cosine_similarity([tup1[0]], [tup2[0]])
    domain_similarity = cosine_similarity([tup1[1]], [tup2[1]])

    similarity = (0.4 * skill_similarity) + (0.6 * domain_similarity)

    return similarity

