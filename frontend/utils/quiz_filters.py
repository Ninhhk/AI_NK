import streamlit as st
import time
import re

def filter_quiz_text(quiz_text):
    """Filter out 'Questions generated: x/y' or similar patterns from quiz text."""
    lines = quiz_text.split('\n')
    filtered_lines = []
    
    for line in lines:
        # Skip lines with "Questions generated" or similar metrics
        if ("Questions generated" in line or 
            "generated:" in line or 
            "📊" in line or
            re.search(r'\d+/\d+', line)):  # Matches patterns like 10/5
            continue
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

def parse_quiz_questions(quiz_content):
    """Parse quiz content into separate questions with better Vietnamese support."""
    questions = []
    current = ""
    
    # Split the content by lines
    lines = quiz_content.split('\n')
    for line in lines:
        # Check for both English and Vietnamese question patterns
        if re.match(r'^Question\s+\d+', line.strip()) or line.strip().startswith("Câu "):
            if current:
                questions.append(current.strip())
            current = line
        # Also check for option patterns as fallback
        elif re.match(r'^[A-D]\.', line.strip()) and not current:
            # If we find an option without a question, create a placeholder question
            current = f"Question {len(questions) + 1}:\n{line}"
        elif current:
            current += "\n" + line
            
    # Add the last question
    if current:
        questions.append(current.strip())
    
    # Remove any "Questions generated: x/y" texts that might be in the questions
    cleaned_questions = []
    for q in questions:
        if ("Questions generated" in q or 
            "generated:" in q or 
            "📊" in q or
            re.search(r'\d+/\d+', q)):  # Matches patterns like 10/5
            continue
        cleaned_questions.append(q)
    
    return cleaned_questions

def apply_quiz_filters_to_frontend():
    """Add this to the top of your file to include filtering functionality."""
    # Then in your quiz display code, add:
    # 
    # # Filter out noise from quiz text
    # quiz_text = filter_quiz_text(quiz_text)
    # 
    # # When parsing questions:
    # questions = parse_quiz_questions(quiz_content)
    
    print("Quiz filter functions added.")
    
if __name__ == "__main__":
    apply_quiz_filters_to_frontend()
