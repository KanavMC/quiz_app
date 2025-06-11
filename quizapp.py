import streamlit as st
import google.generativeai as genai
import re

# --- CONFIGURE GEMINI ---
genai.configure(api_key="AIzaSyCbqHFzGCQPx9VApkkNinSEqhHQsp-ofFk")
model = genai.GenerativeModel("models/gemini-2.0-flash")

st.set_page_config(page_title="Kanav Inc. Quiz", layout="centered")

st.markdown("<h1 style='text-align: center; color: white; background-color:#1976D2; padding: 1rem; border-radius: 10px;'>Kanav Inc. 🎓 AI Quiz Generator</h1>", unsafe_allow_html=True)

# --- INIT SESSION STATE ---
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- PARSE QUESTIONS FROM TEXT ---
def parse_questions(text):
    questions = []
    blocks = text.strip().split("\n\n")
    for block in blocks:
        try:
            lines = block.strip().split("\n")
            q_text = lines[0].strip()
            options = [line.strip().split(". ", 1)[1] for line in lines[1:5]]
            answer_line = next((l for l in lines if "Answer" in l), None)
            answer_letter = re.search(r"Answer: ([A-D])", answer_line).group(1)
            questions.append({
                "question": q_text,
                "options": options,
                "answer": options[ord(answer_letter) - ord("A")]
            })
        except:
            continue
    return questions

# --- GENERATE QUESTIONS ---
def generate_questions(topic, grade_level):
    topic_lower = topic.lower()

    if "brain rot" in topic_lower:
        return [
            {"question": "What is the cure for brain rot?", "options": ["Sleep", "Memes", "Pizza", "Nothing"], "answer": "Memes"},
            {"question": "Which platform causes the most brain rot?", "options": ["TikTok", "YouTube", "Duolingo", "Wikipedia"], "answer": "TikTok"},
            {"question": "What is Italian brain rot often accompanied by?", "options": ["Hand gestures", "Opera", "Pizza", "All of the above"], "answer": "All of the above"},
            {"question": "Best way to treat Italian brain rot?", "options": ["Spaghetti", "Talking with hands", "Watching soccer", "Ignoring it"], "answer": "Spaghetti"},
            {"question": "Who is most at risk of brain rot?", "options": ["People with siblings", "Gen Z", "Programmers", "Everyone"], "answer": "Everyone"},
            {"question": "What sound does brain rot make?", "options": ["Crunch", "Huh?", "Bing Bong", "Silence"], "answer": "Bing Bong"},
            {"question": "A meme a day keeps the...", "options": ["Brain rot away", "Doctor away", "Sanity away", "Cringe at bay"], "answer": "Brain rot away"},
            {"question": "Brain rot can be reversed with...", "options": ["French lessons", "Therapy", "More memes", "Mozart"], "answer": "Therapy"},
            {"question": "Italian brain rot is best experienced with...", "options": ["Risotto", "Vine compilations", "Mario impressions", "All of the above"], "answer": "All of the above"},
            {"question": "Final cure?", "options": ["Unplug", "Brain transplant", "Gelato", "Accept it"], "answer": "Accept it"}
        ]

    prompt = f"""Make 10 multiple-choice quiz questions about {topic}, suitable for a student in {grade_level}.
Each question should have 4 labeled options (A–D), and end with the correct answer like this:

Question: What is the capital of France?
A. Berlin
B. London
C. Madrid
D. Paris
Answer: D

Do this 10 times. No extra info, just questions."""
    try:
        response = model.generate_content(prompt)
        return parse_questions(response.text)
    except Exception as e:
        st.error(f"❌ Failed to generate questions: {e}")
        return []

# --- DISPLAY QUIZ ---
def show_quiz():
    st.subheader("🧠 Answer the Questions:")
    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        st.session_state.answers[i] = st.radio(
            f"Your answer:",
            q["options"],
            key=f"answer_{i}"
        )
    if st.button("📩 Submit Answers"):
        st.session_state.submitted = True

# --- SHOW RESULTS ---
def show_results():
    st.subheader("✅ Results")
    correct = 0
    for i, q in enumerate(st.session_state.questions):
        u = st.session_state.answers[i]
        a = q["answer"]
        if u == a:
            st.success(f"Q{i+1}: ✅ Correct ({u})")
            correct += 1
        else:
            st.error(f"Q{i+1}: ❌ You chose {u}, correct was {a}")
    st.info(f"Final Score: {correct}/10")
    if st.button("🔁 New Quiz"):
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.submitted = False

# --- APP FLOW ---
if not st.session_state.questions:
    st.markdown("### 💬 Choose a grade and topic to generate your quiz!")
    grade = st.selectbox("🎓 Select Grade Level", ["No specific grade"] + [f"Grade {i}" for i in range(1, 13)] + ["College"])
    topic = st.text_input("🧠 I want to be quizzed on...", "")
    if st.button("🚀 Start Quiz") and topic:
        st.session_state.questions = generate_questions(topic, grade)
        st.session_state.answers = [""] * 10

if st.session_state.questions and not st.session_state.submitted:
    show_quiz()

if st.session_state.submitted:
    show_results()
