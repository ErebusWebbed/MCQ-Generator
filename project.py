import streamlit as st
import google.generativeai as genai
import re
from dotenv import load_dotenv
import os
import time
import random

# Load the API key from the .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure page
st.set_page_config(page_title="MCQ Generator", page_icon="📝", layout="wide")

# Initialize session state for user answers if not already present
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# App title and description
st.title("📝 Multiple Choice Question Generator")
st.markdown("Generate custom MCQs on any topic with different difficulty levels")

# Main input fields
topic = st.text_input("Enter a topic", placeholder="e.g., Photosynthesis, Machine Learning, World War II")
col1, col2 = st.columns(2)
with col1:
    difficulty = st.selectbox("Select difficulty level", ["Easy", "Medium", "Hard"])
with col2:
    num_questions = st.slider("Number of questions", min_value=1, max_value=10, value=3)

# Configure Gemini API
def configure_genai(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# Generate MCQs
def generate_mcqs(topic, difficulty, num_questions, model):
    prompt = f"""
    Generate {num_questions} unique and varied multiple-choice questions about '{topic}' at a {difficulty.lower()} difficulty level.

    Each time this is requested, regenerate different versions of questions and options to avoid repetition. Add slight randomness to question framing, options order, and phrasing.

    For each question:
    1. Provide the question
    2. Provide four options labeled a), b), c), and d)
    3. Indicate the correct answer
    4. Give a brief explanation of why that answer is correct

    Format your response as:

    Question 1: [Question text]
    a) [Option a]
    b) [Option b]
    c) [Option c]
    d) [Option d]
    Correct Answer: [Letter of correct option]
    Explanation: [Explanation text]

    Question 2: ...
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating questions: {str(e)}"

# Parse and display MCQs
def parse_and_display_mcqs(mcq_text):
    # When generating new questions, reset the check buttons but keep any existing answers
    for key in list(st.session_state.keys()):
        if key.startswith("check_"):
            del st.session_state[key]
    
    # Split by questions
    questions_blocks = re.split(r'Question \d+:', mcq_text)[1:]

    if not questions_blocks:
        st.error("Could not parse the generated MCQs. Please try again.")
        return

    for i, q_block in enumerate(questions_blocks):
        question_id = f"q{i}"
        
        # Split the question block into lines
        lines = q_block.strip().split('\n')
        
        # Extract question text (first line)
        question_text = lines[0].strip()
        
        # Extract options (lines starting with a), b), c), d))
        options = []
        for line in lines:
            if re.match(r'^[a-d]\)', line.strip()):
                options.append(line.strip())
        
        # Extract option values without the a), b), c), d) prefixes for radio button
        option_values = [opt[3:].strip() for opt in options]
        
        # Extract correct answer
        correct_line = next((line for line in lines if line.strip().startswith("Correct Answer:")), "")
        correct_answer_text = correct_line.split(":", 1)[1].strip() if correct_line else ""
        # Extract just the first letter (a, b, c, or d)
        correct_answer_letter = re.search(r'[a-d]', correct_answer_text.lower()) if correct_answer_text else None
        correct_answer_letter = correct_answer_letter.group(0) if correct_answer_letter else ""
        
        # Extract explanation
        explanation_line = next((line for line in lines if line.strip().startswith("Explanation:")), "")
        explanation = explanation_line.split(":", 1)[1].strip() if explanation_line else ""
        
        # Find the correct option's index (0-3 for a-d)
        correct_idx = ord(correct_answer_letter) - ord('a') if correct_answer_letter else -1
        
        with st.expander(f"Question {i+1}", expanded=True):
            st.markdown(f"**{question_text}**")
            
            # Define a callback for when an answer is selected
            def on_answer_change(question_id=question_id):
                st.session_state.user_answers[question_id] = {"selected": st.session_state[f"{question_id}_radio"], 
                                                             "correct_index": correct_idx,
                                                             "options": options,
                                                             "explanation": explanation}
            
            # The radio button selection
            # Use a unique key for each question and default to no selection (None)
            if len(option_values) > 0:
                selected_index = st.radio(
                    "Select your answer:",
                    range(len(option_values)),
                    format_func=lambda i: options[i],
                    key=f"{question_id}_radio",
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                # Add a "Check Answer" button for each question
                check_key = f"check_{question_id}"
                if check_key not in st.session_state:
                    st.session_state[check_key] = False
                    
                if st.button("Check Answer", key=f"verify_{question_id}"):
                    st.session_state[check_key] = True
                    # Store the answer
                    st.session_state.user_answers[question_id] = {
                        "selected": selected_index,
                        "correct_index": correct_idx,
                        "options": options,
                        "explanation": explanation
                    }
                
                # Show results only after checking
                if st.session_state[check_key]:
                    selected = st.session_state.user_answers[question_id]["selected"]
                    correct_idx = st.session_state.user_answers[question_id]["correct_index"]
                    
                    if selected == correct_idx:
                        st.success(f"✅ Correct! {options[correct_idx]}")
                        st.info(f"**Explanation:** {explanation}")
                    else:
                        st.error(f"❌ Wrong! You selected: {options[selected]}")
                        st.warning(f"The correct answer is: {options[correct_idx]}")
                        st.info(f"**Explanation:** {explanation}")
            else:
                st.error("Could not parse options for this question.")

# Generate and store MCQs
if st.button("Generate MCQs", type="primary"):
    if not api_key:
        st.error("API key not found. Please check your .env file.")
    elif not topic:
        st.error("Please enter a topic")
    else:
        with st.spinner("Generating MCQs..."):
            try:
                model = configure_genai(api_key)
                # Add a timestamp parameter to ensure we get fresh results each time
                timestamp = int(time.time())
                mcq_text = generate_mcqs(f"{topic} (request: {timestamp})", difficulty, num_questions, model)
                # Remove the timestamp from displayed success message
                display_topic = topic
                st.session_state["mcq_text"] = mcq_text
                # Reset user answers when generating new questions
                st.session_state.user_answers = {}
                st.success(f"Generated {num_questions} MCQs on {display_topic} ({difficulty})")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Show MCQs if already generated
if "mcq_text" in st.session_state:
    parse_and_display_mcqs(st.session_state["mcq_text"])
    
    # Add a "Try Again" button at the bottom
    if st.button("Try Again with a New Topic"):
        # Clear the session state to start fresh
        for key in list(st.session_state.keys()):
            if key != "user_answers":  # Keep the user_answers dictionary
                del st.session_state[key]
        st.experimental_rerun()

# Sample question if nothing yet entered
if not topic and "mcq_text" not in st.session_state:
    st.markdown("### Sample MCQ")
    with st.expander("Sample Question on Photosynthesis", expanded=True):
        st.markdown("**What is the main product of photosynthesis?**")
        
        sample_options = [
            "a) Oxygen", 
            "b) Carbon dioxide", 
            "c) Glucose", 
            "d) Water"
        ]
        
        # Display sample options as radio buttons for consistency with the real app
        selected_option = st.radio(
            "Select your answer:",
            range(len(sample_options)),
            format_func=lambda i: sample_options[i],
            key="sample_radio",
            horizontal=True
        )
        
        # Add a "Check Answer" button for the sample
        if "sample_checked" not in st.session_state:
            st.session_state.sample_checked = False
            
        if st.button("Check Answer", key="verify_sample"):
            st.session_state.sample_checked = True
        
        # Show results only after checking
        if st.session_state.sample_checked:
            if selected_option == 2:  # c) Glucose is correct (index 2)
                st.success("✅ Correct! c) Glucose")
            else:
                st.error(f"❌ Wrong! You selected: {sample_options[selected_option]}")
                st.warning("The correct answer is: c) Glucose")
            
            st.info("**Explanation:** While oxygen is released as a byproduct, the main product of photosynthesis is glucose, which plants use for energy and growth.")