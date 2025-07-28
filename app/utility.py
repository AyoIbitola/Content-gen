import os 
import google.generativeai as genai

from sqlalchemy.orm import Session
from dotenv import load_dotenv

import crud,models
import threading
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=GEMINI_KEY)

semaphore = threading.Semaphore(5)

def generate_content(db: Session , topic: str) :
    with semaphore:
        search_term = crud.create_search_term(db,topic)
        if not search_term:
            search_term = crud.create_search_term(db,topic)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        response = model.generate_content(
            
    f"Write a clean, detailed article about {topic} in plain text only. No markdown, no headings, no bold, no lists, and no extra instructions."


        )
        
        generated_text = response.text.strip()

            # Save to database
        crud.create_generated_content(db, generated_text, search_term.id)
        return generated_text
    

def analyze_content(db: Session,content: str):
    with semaphore:
        search_term = crud.get_search_term(db,content)
    if not search_term:
        search_term = crud.create_search_term(db,content)
    readability = get_readability_score(content)
    sentiment = get_sentiment_analysis(content)
    crud.create_sentiment_analysis(db,readability,sentiment,search_term.id)

    return readability,sentiment

def get_readability_score(content: str):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    response = model.generate_content(
            f"Look at this content and give a readability score from 1-10 ,just say the number{content}"
        )
        
    generated_score = response.text.strip()

            # Save to database
   
    return generated_score

def get_sentiment_analysis(content: str):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")

    response = model.generate_content(
            f"Look at this content and give a short sentiment analysis, make a very and don't add reason{content}"
        )
        
    sentiment = response.text.strip()

            # Save to database
   
    return sentiment