import json
import os
from difflib import get_close_matches
from pathlib import Path

# Correct path to faqs.json from actions.py
faq_path = os.path.join(os.path.dirname(__file__), "..", "faqs.json")

def load_faqs():
    """Load FAQ data from JSON file"""
    try:
        with open(faq_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"FAQ file not found at: {faq_path}")
        return []
    except json.JSONDecodeError:
        print(f"Invalid JSON in FAQ file: {faq_path}")
        return []
    

    print("Absolute FAQ path:", os.path.abspath(faq_path))
    print("File exists:", os.path.exists(faq_path))


def get_answer(user_input: str) -> str:
    """Return the best matching answer from the FAQs"""
    try:
        faqs = load_faqs()
        if not faqs:
            return "Sorry, FAQ data is not available at the moment. Please try again later."
        
        user_input = user_input.lower().strip()
        questions = [item["question"].lower().strip() for item in faqs]
        match = get_close_matches(user_input, questions, n=1, cutoff=0.5)
        
        if match:
            for item in faqs:
                if item["question"].lower().strip() == match[0]:
                    return item["answer"]
        
        return "Sorry, I couldn't find an answer to your question. Please check your question and try again."
    
    except Exception as e:
        print(f"Error in get_answer: {e}")
        return "Sorry, I encountered an error while processing your question. Please try again."
