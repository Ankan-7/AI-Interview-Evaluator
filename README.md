# AI Interview Evaluator

AI Interview Evaluator is a full-stack web application that allows students to practice HR and Technical interview questions while receiving AI-based evaluation of their answers.

The system evaluates responses using semantic similarity (Sentence Transformers), keyword matching, and a hybrid scoring model.

---

## Features

- Student login and registration
- Admin panel for managing interview questions
- HR interview mode
- Technical interview mode
- AI answer evaluation using semantic similarity
- Keyword based scoring
- Hybrid scoring system
- Interview timer with auto-submit
- Automatic feedback generation
- SQLite database storage

---

## Tech Stack

Frontend:
- React
- Axios

Backend:
- Flask
- SQLAlchemy
- Flask-CORS

AI / NLP:
- Sentence Transformers
- Semantic similarity using `all-MiniLM-L6-v2`

Database:
- SQLite

---

## Project Structure
AI-Interview-Evaluator
│
├── backend
│ ├── app.py
│ ├── ai_evaluator.py
│ ├── requirements.txt
│ └── ai_interview.db
│
├── frontend
│ ├── src
│ ├── public
│ └── package.json
│
└── README.md

---

## How the AI Evaluation Works

The system evaluates answers using a hybrid scoring approach:

1. **Semantic Similarity**
   - Uses Sentence Transformers to compare the student answer with the reference answer.

2. **Keyword Matching**
   - Checks if important key concepts are included.

3. **Length Bonus**
   - Encourages more detailed answers.

Final Score:
Final Score = 0.8 × Semantic Score + 0.2 × Keyword Score + Length Bonus

The score is then mapped to feedback categories.

---

## Installation

### 1. Clone the Repository
git clone https://github.com/yourusername/AI-Interview-Evaluator.git

### 2. Backend Setup

Navigate to backend folder:
cd backend

Create virtual environment:
python -m venv venv

Activate environment:

Windows:
venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Run backend:
python app.py

---

### 3. Frontend Setup

Navigate to frontend folder:
cd frontend

Install dependencies:
npm install

Start React app:
npm start

---

## First Run Note

The first run will download the Sentence Transformer model:
all-MiniLM-L6-v2 (~90MB)

This may take a few seconds.

---

## Future Improvements

- Interview history and progress tracking
- Performance analytics dashboard
- More advanced NLP evaluation
- UI improvements
- AI generated personalized feedback

---

## Contributors

- Ankan Kundu
- Kaushik Shikari
- Soumyadeep Mridha
- Nafizal Arafat Prince

---

## License

This project is developed for academic and learning purposes.