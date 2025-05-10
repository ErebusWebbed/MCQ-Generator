# 📝 MCQ Generator using Generative AI (Gemini)

A web-based multiple-choice question (MCQ) generator built using **Streamlit** and **Google Generative AI (Gemini 1.5 Flash)**. This app allows users to generate topic-specific, difficulty-adjusted MCQs on the fly — complete with answer validation and explanations.

---

## 🚀 Features

- 🎯 Input-based MCQ generation (Topic + Difficulty)
- 🤖 Powered by Gemini 1.5 Flash (Google Generative AI)
- ✅ Correct answer checking with instant feedback
- 💬 Explanations provided for each question
- 🌐 Interactive and user-friendly web interface
- 🔐 Secure API key management using `.env`

---

## 🛠️ Tech Stack

- **Python**  
- **Streamlit** (UI Framework)  
- **Google Generative AI** (Gemini API)  
- **dotenv** (Environment variable handling)  
- **re** (Regex-based output parsing)  

---

## 📦 Installation

1. **Clone the Repository**

git clone https://github.com/your-username/mcq-generator.git
cd mcq-generator

2. **Create a Virtual Environment** (Optional)

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies**

pip install -r requirements.txt

4. **Set Up Environment Variables**

Create a .env file in the root directory:

GOOGLE_API_KEY=your_gemini_api_key_here  # Get your Gemini API key from Google AI Studio

## ▶️ Run the App

streamlit run app.py

## 🧠 How It Works

1. The user inputs a topic and selects a difficulty level.

2. The app sends a structured prompt to Gemini 1.5 Flash to generate multiple MCQs.
 
3. Questions are parsed, displayed interactively, and the user can:

• Select an answer

• Click "Check Answer"

• Get immediate feedback and explanation
