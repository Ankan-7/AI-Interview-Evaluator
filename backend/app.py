from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import bcrypt
from sqlalchemy.sql import func
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import json
import re
import random
from ai_evaluator import hybrid_evaluate
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# -------------------- BASIC APP SETUP -------------------- #

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
@app.route("/ping")
def ping():
    return "pong"
CORS(app)

# SQLite database file in backend folder
DATABASE_URL = os.getenv("DATABASE_URL")
engine = None
SessionLocal = None

def get_db():
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
Base = declarative_base()

# -------------------- DATABASE MODELS -------------------- #

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password_hash = Column(String(200))
    role = Column(String(20))  # 'student' or 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)
    interviews = relationship("Interview", back_populates="user")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question_text = Column(Text)
    category = Column(String(50))   # 'Technical' or 'HR'
    difficulty = Column(String(20)) # 'Easy', 'Medium', 'Hard'
    key_terms = Column(Text)        # JSON list of strings
    reference_answer = Column(Text)

class Interview(Base):
    __tablename__ = 'interviews'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    total_score = Column(Float)
    overall_feedback = Column(Text)
    user = relationship("User", back_populates="interviews")
    responses = relationship("Response", back_populates="interview")

class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_text = Column(Text)
    score = Column(Float)
    feedback = Column(Text)
    interview = relationship("Interview", back_populates="responses")

# Create tables if not exist
# Base.metadata.create_all(engine)

# -------------------- EVALUATION LOGIC -------------------- #

def preprocess_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def evaluate_answer(answer_text: str, key_terms: list) -> dict:
    """
    Implements: preprocess -> keyword match -> length bonus -> final score 0-10.
    Matches the simple rule-based design in your report.
    """
    clean_answer = preprocess_text(answer_text)
    words = clean_answer.split()
    word_set = set(words)

    total_keywords = len(key_terms)
    matched = 0
    for term in key_terms:
        term = term.lower().strip()
        if ' ' in term:
            if term in clean_answer:
                matched += 1
        else:
            if term in word_set:
                matched += 1

    keyword_score = 0.0
    if total_keywords > 0:
        keyword_score = (matched / total_keywords) * 8.0  # 0–8 base score

    length_bonus = 0.0
    word_count = len(words)
    if word_count >= 50:
        length_bonus += 1.0
    if word_count >= 100:
        length_bonus += 1.0
    if length_bonus > 2.0:
        length_bonus = 2.0

    final_score = keyword_score + length_bonus
    if final_score > 10.0:
        final_score = 10.0

    if final_score >= 8.0:
        feedback = "Excellent! You covered most of the important points."
    elif final_score >= 6.0:
        feedback = "Good answer, but you can add more details on some missing points."
    elif final_score >= 4.0:
        feedback = "Average answer. Revise this topic and try to include more key concepts."
    else:
        feedback = "Needs improvement. Review the concept and practice explaining it more clearly."

    return {"score": round(final_score, 1), "feedback": feedback}

# -------------------- BASIC ROUTE -------------------- #

@app.get("/")
def home():
    return jsonify({"message": "AI Interview Evaluator backend running"})

# -------------------- AUTH ROUTES -------------------- #

@app.post("/register")
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")  # default student

    if not all([name, email, password]):
        return jsonify({"error": "Name, email, and password are required"}), 400

    db = get_db()
    try:
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            return jsonify({"error": "Email already exists"}), 400

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(
            name=name,
            email=email,
            password_hash=hashed.decode('utf-8'),
            role=role
        )
        db.add(user)
        db.commit()

        return jsonify({"message": "Registered successfully", "user_id": user.id})
    finally:
        db.close()

@app.post("/login")
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    db = get_db()
    try:
        user = db.query(User).filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({"user_id": user.id, "role": user.role, "name": user.name})
    finally:
        db.close()

# -------------------- ADMIN: QUESTION MANAGEMENT -------------------- #

@app.post("/questions")
def add_question():
    data = request.json
    question_text = data.get("question_text")
    category = data.get("category", "Technical")
    difficulty = data.get("difficulty", "Easy")
    key_terms = data.get("key_terms", [])
    reference_answer = data.get("reference_answer", "")

    if not question_text:
        return jsonify({"error": "question_text is required"}), 400

    if not isinstance(key_terms, list):
        return jsonify({"error": "key_terms must be a list"}), 400

    db = SessionLocal()
    try:
        q = Question(
            question_text=question_text,
            category=category,
            difficulty=difficulty,
            key_terms=json.dumps(key_terms),
            reference_answer=reference_answer
        )
        db.add(q)
        db.commit()
        return jsonify({"message": "Question added", "id": q.id})
    finally:
        db.close()

@app.get("/questions")
def list_questions():
    db = SessionLocal()
    try:
        questions = db.query(Question).all()
        result = []
        for q in questions:
            result.append({
                "id": q.id,
                "question_text": q.question_text,
                "category": q.category,
                "difficulty": q.difficulty,
                "key_terms": json.loads(q.key_terms or "[]")
            })
        return jsonify(result)
    finally:
        db.close()

# -------------------- STUDENT: INTERVIEW FLOW -------------------- #

@app.post("/start_interview")
def start_interview():
    data = request.json
    user_id = data.get("user_id")
    category = data.get("category", "Technical")
    num_questions = data.get("num_questions", 5)

    db = SessionLocal()
    try:
        total_q = db.query(Question).filter_by(category=category).count()
        if total_q == 0:
            return jsonify({"error": "No questions available for this category"}), 400

        if total_q < num_questions:
            num_questions = total_q

        qs = (
            db.query(Question)
            .filter_by(category=category)
            .order_by(func.random())      # random, non‑repeating
            .limit(num_questions)
            .all()
        )

        interview = Interview(user_id=user_id, total_score=0.0, overall_feedback="")
        db.add(interview)
        db.commit()

        questions = [
            {"id": q.id, "question_text": q.question_text}
            for q in qs
        ]

        return jsonify({"interview_id": interview.id, "questions": questions})
    finally:
        db.close()



@app.post("/submit_interview")
def submit_interview():
    data = request.json
    interview_id = data.get("interview_id")
    answers = data.get("answers")  # list of {question_id, answer_text}

    if not isinstance(answers, list):
        return jsonify({"error": "answers must be a list"}), 400

    db = SessionLocal()
    try:
        interview = db.query(Interview).filter_by(id=interview_id).first()
        if not interview:
            return jsonify({"error": "Interview not found"}), 404

        total = 0.0
        response_payload = []

        for item in answers:
            qid = item["question_id"]
            ans_text = item["answer_text"]
            q = db.query(Question).filter_by(id=qid).first()
            if not q:
                continue

            key_terms = json.loads(q.key_terms or "[]")
            eval_result = hybrid_evaluate(
                q.reference_answer,
                ans_text,
                key_terms
            )
            score = eval_result["score"]
            feedback = eval_result["feedback"]

            resp = Response(
                interview_id=interview.id,
                question_id=qid,
                answer_text=ans_text,
                score=score,
                feedback=feedback
            )
            db.add(resp)
            total += score
            response_payload.append({
                "question_id": qid,
                "question_text": q.question_text,
                "answer_text": ans_text,
                "score": score,
                "feedback": feedback
            })

        avg_score = total / max(len(answers), 1)

        if avg_score >= 8.0:
            overall = "Strong performance. You are well prepared."
        elif avg_score >= 6.0:
            overall = "Good performance with some gaps. Revise a few topics."
        elif avg_score >= 4.0:
            overall = "Average performance. Practice more on fundamentals."
        else:
            overall = "Weak performance. Revisit core concepts and practice regularly."

        interview.total_score = round(avg_score, 1)
        interview.overall_feedback = overall
        db.commit()

        return jsonify({
            "interview_id": interview.id,
            "total_score": interview.total_score,
            "overall_feedback": interview.overall_feedback,
            "responses": response_payload
        })
    finally:
        db.close()

@app.get("/results/<int:interview_id>")
def get_results(interview_id):
    db = SessionLocal()
    try:
        interview = db.query(Interview).filter_by(id=interview_id).first()
        if not interview:
            return jsonify({"error": "Not found"}), 404

        responses = []
        for r in interview.responses:
            q = db.query(Question).filter_by(id=r.question_id).first()
            responses.append({
                "question_text": q.question_text if q else "",
                "answer_text": r.answer_text,
                "score": r.score,
                "feedback": r.feedback
            })

        return jsonify({
            "interview_id": interview.id,
            "total_score": interview.total_score,
            "overall_feedback": interview.overall_feedback,
            "responses": responses
        })
    finally:
        db.close()

# -------------------- MAIN -------------------- #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

