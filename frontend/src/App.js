import React, { useState } from "react";
import axios from "axios";

axios.defaults.baseURL = "http://127.0.0.1:5000";

function App() {
  const [page, setPage] = useState("login");
  const [user, setUser] = useState(null); // {user_id, role, name}
  const [interview, setInterview] = useState(null); // {interview_id, questions}
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [timerActive, setTimerActive] = useState(false);

  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [registerForm, setRegisterForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "student",
  });

  // ---------- AUTH ----------

  const handleRegister = async () => {
    try {
      await axios.post("/register", registerForm);
      alert("Registered! Now login.");
      setPage("login");
    } catch (err) {
      alert("Register error");
      console.error(err);
    }
  };

  const handleLogin = async () => {
    try {
      const res = await axios.post("/login", loginForm);
      setUser(res.data);
      if (res.data.role === "admin") {
        setPage("admin");
      } else {
        setPage("student");
      }
    } catch (err) {
      alert("Login error");
      console.error(err);
    }
  };

  // ---------- STUDENT: INTERVIEW ----------

  const startInterview = async () => {
    try {
      const res = await axios.post("/start_interview", {
        user_id: user.user_id,
        category: "Technical",
        num_questions: 3,
      });
      setInterview(res.data);
      setAnswers({});
      setResult(null);
      setTimeLeft(15 * 60); // 15 minutes
      setTimerActive(true);
      setPage("interview");
    } catch (err) {
      alert("Could not start interview");
      console.error(err);
    }
  };

  const startHrInterview = async () => {
    try {
      const res = await axios.post("/start_interview", {
        user_id: user.user_id,
        category: "HR",
        num_questions: 3,
      });
      setInterview(res.data);
      setAnswers({});
      setResult(null);
      setTimeLeft(15 * 60);
      setTimerActive(true);
      setPage("interview");
    } catch (err) {
      alert("Could not start HR interview");
      console.error(err);
    }
  };

  const submitInterview = async () => {
    try {
      setTimerActive(false);
      const answersArray = interview.questions.map((q) => ({
        question_id: q.id,
        answer_text: answers[q.id] || "",
      }));

      const res = await axios.post("/submit_interview", {
        interview_id: interview.interview_id,
        answers: answersArray,
      });

      setResult(res.data);
      setPage("result");
    } catch (err) {
      alert("Could not submit interview");
      console.error(err);
    }
  };

  // ---------- ADMIN: ADD QUESTION ----------

  const [newQuestion, setNewQuestion] = useState({
    question_text: "",
    category: "Technical",
    difficulty: "Easy",
    key_terms_text: "",
    reference_answer: "",
  });

  const addQuestion = async () => {
    try {
      const key_terms = newQuestion.key_terms_text
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      await axios.post("/questions", {
        question_text: newQuestion.question_text,
        category: newQuestion.category,
        difficulty: newQuestion.difficulty,
        key_terms: key_terms,
        reference_answer: newQuestion.reference_answer,
      });

      alert("Question added");
      setNewQuestion({
        question_text: "",
        category: "Technical",
        difficulty: "Easy",
        key_terms_text: "",
        reference_answer: "",
      });
    } catch (err) {
      alert("Error adding question");
      console.error(err);
    }
  };

  // ---------- PAGES ----------
  React.useEffect(() => {
    if (!timerActive || timeLeft <= 0) return;

    const id = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(id);
          setTimerActive(false);
          submitInterview(); // auto-submit once time is over
          return 0;
        }
        return t - 1;
      });
    }, 1000);

    return () => clearInterval(id);
  }, [timerActive, timeLeft]);

  if (page === "login") {
    return (
      <>
        <div
          style={{
            position: "sticky",
            top: 0,
            zIndex: 10,
            backgroundColor: "#4f46e5",
            color: "white",
            padding: "10px 20px",
          }}
        >
          <strong>🤖 AI Interview Evaluator</strong>
        </div>

        <div className="app-container">
          <h2>AI Interview Evaluator - Login</h2>
          <div>
            <input
              placeholder="Email"
              value={loginForm.email}
              onChange={(e) =>
                setLoginForm({ ...loginForm, email: e.target.value })
              }
            />
          </div>
          <div>
            <input
              placeholder="Password"
              type="password"
              value={loginForm.password}
              onChange={(e) =>
                setLoginForm({ ...loginForm, password: e.target.value })
              }
            />
          </div>
          <button onClick={handleLogin}>Login</button>

          <hr />
          <h3>Or Register</h3>
          <div>
            <input
              placeholder="Name"
              value={registerForm.name}
              onChange={(e) =>
                setRegisterForm({ ...registerForm, name: e.target.value })
              }
            />
          </div>
          <div>
            <input
              placeholder="Email"
              value={registerForm.email}
              onChange={(e) =>
                setRegisterForm({ ...registerForm, email: e.target.value })
              }
            />
          </div>
          <div>
            <input
              placeholder="Password"
              type="password"
              value={registerForm.password}
              onChange={(e) =>
                setRegisterForm({ ...registerForm, password: e.target.value })
              }
            />
          </div>
          <div>
            <label>
              Role:
              <select
                value={registerForm.role}
                onChange={(e) =>
                  setRegisterForm({ ...registerForm, role: e.target.value })
                }
              >
                <option value="student">Student</option>
                <option value="admin">Admin</option>
              </select>
            </label>
          </div>
          <button onClick={handleRegister}>Register</button>
          <p
            style={{
              marginTop: 24,
              fontSize: 12,
              color: "#6b7280",
              textAlign: "right",
              whiteSpace: "pre-line",
            }}
          >
            <strong>PROJECT BY</strong>
            {"\n"}
            Ankan Kundu{"\n"}
            Kaushik Shikari{"\n"}
            Soumyadeep Mridha{"\n"}
            Nafizal Arafat Prince
          </p>
        </div>
      </>
    );
  }

  if (page === "student") {
    return (
      <>
        <div
          style={{
            position: "sticky",
            top: 0,
            zIndex: 10,
            backgroundColor: "#4f46e5",
            color: "white",
            padding: "10px 20px",
          }}
        >
          <strong>🤖 AI Interview Evaluator</strong>
        </div>

        <div className="app-container">
          <h2>Student Dashboard</h2>
          <p>Welcome, {user.name}</p>
          <button onClick={startInterview}>Start Technical Interview</button>
          <button style={{ marginLeft: 10 }} onClick={startHrInterview}>
            Start HR Interview
          </button>
          <button
            style={{ marginLeft: 10 }}
            onClick={() => {
              setUser(null);
              setPage("login");
            }}
          >
            Logout
          </button>
        </div>
      </>
    );
  }

  if (page === "interview") {
    return (
      <>
        <div
          style={{
            position: "sticky",
            top: 0,
            zIndex: 10,
            backgroundColor: "#4f46e5",
            color: "white",
            padding: "10px 20px",
          }}
        >
          <strong>🤖 AI Interview Evaluator</strong>
        </div>

        <div className="app-container">
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 10,
            }}
          >
            <h2>Interview</h2>
            <p>
              Answered {
              Object.values(answers).filter(
                (ans) => ans && ans.trim() !== ""
              ).length
              } / {interview.questions.length}
            </p>
            <span
              style={{
                fontSize: "26px",
                fontWeight: "bold",
                color: timeLeft <= 120 ? "red" : "black",
              }}
            >
              Time left:{" "}
              {Math.floor(timeLeft / 60)
                .toString()
                .padStart(2, "0")}
              :{(timeLeft % 60).toString().padStart(2, "0")}
            </span>
          </div>

          {interview.questions.map((q) => (
            <div key={q.id} style={{ marginBottom: 20 }}>
              <h4>{q.question_text}</h4>
              <textarea
                rows={5}
                cols={60}
                value={answers[q.id] || ""}
                onChange={(e) =>
                  setAnswers({ ...answers, [q.id]: e.target.value })
                }
              />
            </div>
          ))}
          <button onClick={submitInterview}>Submit Interview</button>
        </div>
      </>
    );
  }

  if (page === "result") {
    return (
      <>
        <div
          style={{
            position: "sticky",
            top: 0,
            zIndex: 10,
            backgroundColor: "#4f46e5",
            color: "white",
            padding: "10px 20px",
          }}
        >
          <strong>🤖 AI Interview Evaluator</strong>
        </div>

        <div className="app-container">
          <h2>Results</h2>
          <p>
            Total Score: <b>{result.total_score}</b>
          </p>
          <p>{result.overall_feedback}</p>
          <hr />
          {result.responses.map((r, idx) => (
            <div key={idx} style={{ marginBottom: 20 }}>
              <h4>Question: {r.question_text}</h4>
              <p>
                <b>Your Answer:</b> {r.answer_text}
              </p>
              <p>
                <b>Score:</b> {r.score}
              </p>
              <p>
                <b>Feedback:</b> {r.feedback}
              </p>
            </div>
          ))}
          <button onClick={() => setPage("student")}>Back to Dashboard</button>
        </div>
      </>
    );
  }

  if (page === "admin") {
    return (
      <>
        <div
          style={{
            position: "sticky",
            top: 0,
            zIndex: 10,
            backgroundColor: "#4f46e5",
            color: "white",
            padding: "10px 20px",
          }}
        >
          <strong>🤖 AI Interview Evaluator</strong>
        </div>

        <div className="app-container">
          <h2>Admin Dashboard</h2>
          <p>Welcome, {user.name}</p>

          <h3>Add Question</h3>
          <div>
            <textarea
              placeholder="Question text"
              rows={3}
              cols={60}
              value={newQuestion.question_text}
              onChange={(e) =>
                setNewQuestion({
                  ...newQuestion,
                  question_text: e.target.value,
                })
              }
            />
          </div>
          <div>
            <label>
              Category:
              <select
                value={newQuestion.category}
                onChange={(e) =>
                  setNewQuestion({ ...newQuestion, category: e.target.value })
                }
              >
                <option value="Technical">Technical</option>
                <option value="HR">HR</option>
              </select>
            </label>
          </div>
          <div>
            <label>
              Difficulty:
              <select
                value={newQuestion.difficulty}
                onChange={(e) =>
                  setNewQuestion({ ...newQuestion, difficulty: e.target.value })
                }
              >
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </label>
          </div>
          <div>
            <div>
              <textarea
                placeholder="Reference Answer (for AI evaluation)"
                rows={3}
                cols={60}
                value={newQuestion.reference_answer}
                onChange={(e) =>
                  setNewQuestion({
                    ...newQuestion,
                    reference_answer: e.target.value,
                  })
                }
              />
            </div>

            <div>
              <textarea
                placeholder="Key terms (comma separated, e.g. encapsulation, inheritance, polymorphism)"
                rows={2}
                cols={60}
                value={newQuestion.key_terms_text}
                onChange={(e) =>
                  setNewQuestion({
                    ...newQuestion,
                    key_terms_text: e.target.value,
                  })
                }
              />
            </div>
          </div>
          <button onClick={addQuestion}>Add Question</button>

          <div style={{ marginTop: 20 }}>
            <button
              onClick={() => {
                setUser(null);
                setPage("login");
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </>
    );
  }

  return null;
}

export default App;
