from sentence_transformers import SentenceTransformer, util

# Load model once
model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

def keyword_score(answer_text, key_terms):
    if not key_terms:
        return 0

    answer = answer_text.lower()
    words = set(answer.split())

    matched = 0
    for term in key_terms:
        term = term.lower().strip()

        if " " in term:
            if term in answer:
                matched += 1
        else:
            if term in words:
                matched += 1

    return (matched / len(key_terms)) * 10


def semantic_score(reference_answer, student_answer, key_terms):

    # If no reference answer exists, create pseudo reference using keywords
    if not reference_answer and key_terms:
        reference_answer = (
        "A good answer should discuss concepts such as "
        + ", ".join(key_terms)
        + " in a clear explanation."
    )

    if not reference_answer:
        return 0

    model_instance = get_model()
    embeddings = model_instance.encode([reference_answer, student_answer])

    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

    score = (similarity + 0.3) * 10
    if score < 0:
        score = 0
    if score > 10:
        score = 10
    return score

def hybrid_evaluate(reference_answer, student_answer, key_terms):

    sem_score = semantic_score(reference_answer, student_answer, key_terms)
    key_score = keyword_score(student_answer, key_terms)

    
    final_score = (0.8 * sem_score) + (0.2 * key_score)

    # length bonus
    word_count = len(student_answer.split())

    if word_count >= 60:
        final_score += 1
    elif word_count >= 30:
        final_score += 0.5

    if final_score > 10:
        final_score = 10

    if final_score >= 8:
        feedback = "Excellent answer. Strong understanding."
    elif final_score >= 6:
        feedback = "Good answer but could include more detail."
    elif final_score >= 4:
        feedback = "Average answer. Revise this concept."
    else:
        feedback = "Weak answer. Review the topic and practice."

    return {
        "score": round(final_score, 1),
        "feedback": feedback
    }