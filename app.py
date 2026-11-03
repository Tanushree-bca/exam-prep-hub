from datetime import datetime, timedelta
import io
from urllib.parse import quote_plus
import streamlit as st
import chatbot
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Page configuration
st.set_page_config(
    page_title="Exam Prep Hub",
    page_icon="📚",
    layout="wide",
)


def search_link(query):
  """Builds a working Google search link for a given query."""
  return f"https://www.google.com/search?q={quote_plus(query)}"


# ---------- Exam Data ----------
EXAMS = {
    "upsc": {
        "name": "UPSC Civil Services Examination",
        "category": "UPSC",
        "date": "Check UPSC official calendar",
        "syllabus_link": "https://upsc.gov.in/examinations/syllabus",
        "papers_link": (
            "https://upsc.gov.in/examinations/previous-question-papers"
        ),
        "notes_link": search_link("UPSC Civil Services preparation notes"),
        "books": [
            "NCERT History, Geography, Polity (Class 6-12)",
            "Indian Polity - M. Laxmikanth",
            "Economic Survey (latest edition)",
        ],
        "official_link": "https://upsc.gov.in",
        "subjects": [
            "History",
            "Geography",
            "Polity",
            "Economy",
            "Current Affairs",
            "Science & Tech",
            "Ethics",
        ],
    },
    "ssc": {
        "name": "SSC CGL (Combined Graduate Level)",
        "category": "SSC",
        "date": "Check SSC official calendar",
        "syllabus_link": "https://ssc.nic.in/Portal/Syllabus",
        "papers_link": "https://ssc.nic.in/Portal/PreviousQuestionPapers",
        "notes_link": search_link("SSC CGL preparation notes"),
        "books": [
            "Quantitative Aptitude - R.S. Aggarwal",
            "General English - S.P. Bakshi",
            "Lucent's General Knowledge",
        ],
        "official_link": "https://ssc.nic.in",
        "subjects": [
            "Quantitative Aptitude",
            "Reasoning",
            "English",
            "General Awareness",
        ],
        "site_note": True,
    },
    "banking": {
        "name": "IBPS PO (Probationary Officer)",
        "category": "Banking / IBPS",
        "date": "Check IBPS official calendar",
        "syllabus_link": "https://www.ibps.in/",
        "papers_link": search_link("IBPS PO previous year question papers"),
        "notes_link": search_link("IBPS PO preparation notes"),
        "books": [
            "Quantitative Aptitude for Competitive Examinations",
            "Banking Awareness Handbook",
            "Reasoning - R.S. Aggarwal",
        ],
        "official_link": "https://www.ibps.in",
        "subjects": [
            "Quantitative Aptitude",
            "Reasoning",
            "English",
            "Banking Awareness",
            "Computer Knowledge",
        ],
    },
    "railway": {
        "name": "RRB NTPC (Non-Technical Popular Categories)",
        "category": "Railway",
        "date": "Check RRB official calendar",
        "syllabus_link": search_link("RRB NTPC official syllabus"),
        "papers_link": search_link("RRB NTPC previous year question papers"),
        "notes_link": search_link("RRB NTPC preparation notes"),
        "books": [
            "RRB NTPC Guide",
            "General Science for Railway Exams",
            "Previous Year Solved Papers",
        ],
        "official_link": "https://indianrailways.gov.in",
        "subjects": [
            "Mathematics",
            "General Intelligence",
            "General Science",
            "General Awareness",
        ],
        "site_note": True,
    },
    "state": {
        "name": "State PSC (Public Service Commission)",
        "category": "State Government",
        "date": "Varies by state",
        "syllabus_link": search_link("State PSC exam syllabus"),
        "papers_link": search_link("State PSC previous year question papers"),
        "notes_link": search_link("State PSC preparation notes"),
        "books": [
            "State-specific GK Handbook",
            "NCERT Books (Class 6-12)",
            "Previous Year State PSC Papers",
        ],
        "official_link": search_link("State PSC official website"),
        "subjects": [
            "State History & Geography",
            "Polity",
            "Economy",
            "Current Affairs",
            "General Science",
        ],
        "varies_note": True,
    },
    "defence": {
        "name": "NDA (National Defence Academy)",
        "category": "Defence",
        "date": "Check UPSC/NDA official calendar",
        "syllabus_link": "https://upsc.gov.in/examinations/syllabus",
        "papers_link": (
            "https://upsc.gov.in/examinations/previous-question-papers"
        ),
        "notes_link": search_link("NDA exam preparation notes"),
        "books": [
            "NDA Mathematics - R.S. Aggarwal",
            "General Ability Test Guide",
            "NCERT Science & Social Studies",
        ],
        "official_link": "https://upsc.gov.in",
        "subjects": [
            "Mathematics",
            "General Ability",
            "English",
            "Science",
            "Current Affairs",
        ],
    },
}

QUIZZES = {
    "upsc": [
        {
            "q": "Who is known as the Father of the Indian Constitution?",
            "options": [
                "Mahatma Gandhi",
                "B.R. Ambedkar",
                "Jawaharlal Nehru",
                "Sardar Patel",
            ],
            "answer": 1,
        },
        {
            "q": (
                "The Fundamental Rights are enshrined in which part of the"
                " Indian Constitution?"
            ),
            "options": ["Part II", "Part III", "Part IV", "Part V"],
            "answer": 1,
        },
        {
            "q": "Which river is known as the 'Sorrow of Bihar'?",
            "options": ["Ganga", "Yamuna", "Kosi", "Son"],
            "answer": 2,
        },
    ],
    "ssc": [
        {
            "q": "Find the next number: 2, 6, 12, 20, 30, ?",
            "options": ["36", "40", "42", "44"],
            "answer": 2,
        },
        {
            "q": "What is the synonym of 'Abundant'?",
            "options": ["Scarce", "Plentiful", "Limited", "Rare"],
            "answer": 1,
        },
        {
            "q": "What is 15% of 200?",
            "options": ["20", "25", "30", "35"],
            "answer": 2,
        },
    ],
    "banking": [
        {
            "q": "RBI was established in which year?",
            "options": ["1935", "1947", "1950", "1969"],
            "answer": 0,
        },
        {
            "q": "What does NEFT stand for?",
            "options": [
                "National Electronic Funds Transfer",
                "New Electronic Fast Transfer",
                "National Economic Fund Transfer",
                "None of these",
            ],
            "answer": 0,
        },
        {
            "q": (
                "A, B, C are siblings. A is B's brother. C is A's sister. What"
                " is C to B?"
            ),
            "options": ["Brother", "Sister", "Cannot be determined", "Mother"],
            "answer": 1,
        },
    ],
    "railway": [
        {
            "q": "Who is known as the father of Indian Railways?",
            "options": [
                "Lord Dalhousie",
                "Lord Curzon",
                "Lord Mountbatten",
                "Lord Wellesley",
            ],
            "answer": 0,
        },
        {
            "q": "Which is the longest railway platform in India?",
            "options": ["Gorakhpur", "Kharagpur", "Kollam", "Bilaspur"],
            "answer": 0,
        },
        {
            "q": (
                "If a train travels 60 km in 45 minutes, what is its speed in"
                " km/h?"
            ),
            "options": ["75", "80", "85", "90"],
            "answer": 1,
        },
    ],
    "state": [
        {
            "q": "Which is the largest state in India by area?",
            "options": [
                "Madhya Pradesh",
                "Maharashtra",
                "Rajasthan",
                "Uttar Pradesh",
            ],
            "answer": 2,
        },
        {
            "q": "The Governor of a state is appointed by whom?",
            "options": [
                "Prime Minister",
                "Chief Minister",
                "President",
                "Parliament",
            ],
            "answer": 2,
        },
        {
            "q": (
                "Panchayati Raj system was given constitutional status by which"
                " amendment?"
            ),
            "options": ["42nd", "61st", "73rd", "86th"],
            "answer": 2,
        },
    ],
    "defence": [
        {
            "q": (
                "The National Defence Academy (NDA) is located in which state?"
            ),
            "options": ["Maharashtra", "Uttar Pradesh", "Rajasthan", "Punjab"],
            "answer": 0,
        },
        {
            "q": "Who is the Supreme Commander of the Indian Armed Forces?",
            "options": [
                "Prime Minister",
                "President",
                "Defence Minister",
                "Chief of Army Staff",
            ],
            "answer": 1,
        },
        {
            "q": (
                "What does INS (used before Indian naval ship names) stand"
                " for?"
            ),
            "options": [
                "Indian National Ship",
                "Indian Naval Ship",
                "International Naval Ship",
                "Indian Navy Station",
            ],
            "answer": 1,
        },
    ],
}


def generate_weighted_plan(subjects, confidence, days_left, daily_hours):
  weights = {subj: (6 - confidence.get(subj, 3)) for subj in subjects}
  total_weight = sum(weights.values()) or 1

  allocation = []
  for subj in subjects:
    daily = round(daily_hours * weights[subj] / total_weight, 2)
    total_until_exam = round(daily * days_left, 1)
    allocation.append({
        "subject": subj,
        "confidence": confidence.get(subj, 3),
        "daily_hours": daily,
        "total_hours": total_until_exam,
    })

  allocation.sort(key=lambda x: x["confidence"])
  weakest = allocation[0]
  strongest = allocation[-1]
  insight = (
      f"Your weakest area is {weakest['subject']} (confidence"
      f" {weakest['confidence']}/5) — we've allocated"
      f" {weakest['daily_hours']} hrs/day to it. {strongest['subject']} is your"
      " strongest area, so it gets less daily time."
  )
  return allocation, insight


def build_plan_pdf(exam, allocation, insight, days_left, daily_hours):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(buffer, pagesize=A4, title="Study Plan")
  styles = getSampleStyleSheet()
  elements = []

  elements.append(Paragraph(f"AI Study Plan - {exam['name']}", styles["Title"]))
  elements.append(Spacer(1, 10))
  elements.append(
      Paragraph(f"Days until exam: {days_left}", styles["Normal"])
  )
  elements.append(
      Paragraph(
          f"Daily study hours available: {daily_hours}", styles["Normal"]
      )
  )
  elements.append(Spacer(1, 14))
  elements.append(Paragraph(insight, styles["Normal"]))
  elements.append(Spacer(1, 16))

  table_data = [["Subject", "Confidence", "Daily Hours", "Total Hours"]]
  for item in allocation:
    table_data.append([
        item["subject"],
        f"{item['confidence']} / 5",
        f"{item['daily_hours']} hrs",
        f"{item['total_hours']} hrs",
    ])

  table = Table(table_data, colWidths=[150, 90, 100, 110])
  table.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("ALIGN", (1, 0), (-1, -1), "CENTER"),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
          (
              "ROWBACKGROUNDS",
              (0, 1),
              (-1, -1),
              [colors.white, colors.HexColor("#f9fafb")],
          ),
          ("FONTSIZE", (0, 0), (-1, -1), 10),
          ("TOPPADDING", (0, 0), (-1, -1), 8),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
      ])
  )
  elements.append(table)
  doc.build(elements)
  buffer.seek(0)
  return buffer


# ---------- Streamlit Navigation & UI ----------
st.sidebar.title("📚 Exam Prep Hub")
page = st.sidebar.radio(
    "Navigation",
    [
        "Home / Exams",
        "AI Study Plan",
        "AI Chatbot",
        "Practice Quiz",
        "Exam Countdown",
    ],
)

if page == "Home / Exams":
  st.title("Welcome to Exam Prep Hub")
  st.write(
      "Select an exam below to view details, syllabus, books, and resources."
  )

  exam_keys = list(EXAMS.keys())
  selected_exam_key = st.selectbox(
      "Choose an Exam", exam_keys, format_func=lambda x: EXAMS[x]["name"]
  )
  exam = EXAMS[selected_exam_key]

  st.markdown(f"### {exam['name']}")
  st.write(f"**Category:** {exam['category']}")
  st.write(f"**Exam Date:** {exam['date']}")

  col1, col2, col3 = st.columns(3)
  with col1:
    st.markdown(f"[Official Website]({exam['official_link']})")
  with col2:
    st.markdown(f"[Syllabus]({exam['syllabus_link']})")
  with col3:
    st.markdown(f"[Previous Papers]({exam['papers_link']})")

  st.markdown("#### Recommended Books")
  for book in exam["books"]:
    st.markdown(f"- {book}")

  st.markdown("#### Core Subjects")
  st.write(", ".join(exam["subjects"]))

elif page == "AI Study Plan":
  st.title("🧠 AI Personalized Study Plan")
  st.write(
      "Rate your confidence in each subject, and our system will generate a"
      " tailored schedule."
  )

  exam_keys = list(EXAMS.keys())
  selected_exam_key = st.selectbox(
      "Select Exam", exam_keys, format_func=lambda x: EXAMS[x]["name"]
  )
  exam = EXAMS[selected_exam_key]

  with st.form("study_plan_form"):
    exam_date = st.date_input(
        "Target Exam Date", min_value=datetime.now().date() + timedelta(days=1)
    )
    daily_hours = st.number_input(
        "Daily Study Hours Available", min_value=0.5, max_value=16.0, value=4.0
    )

    st.markdown("### Rate Your Confidence (1 = Weak, 5 = Strong)")
    confidence = {}
    for subj in exam["subjects"]:
      confidence[subj] = st.slider(subj, 1, 5, 3)

    submitted = st.form_submit_button("Generate Study Plan")

  if submitted:
    today = datetime.now().date()
    days_left = (exam_date - today).days

    if days_left <= 0:
      st.error("Please choose an exam date in the future.")
    else:
      allocation, insight = generate_weighted_plan(
          exam["subjects"], confidence, days_left, daily_hours
      )

      st.success("Study Plan Generated Successfully!")
      st.info(insight)

      table_data = []
      for item in allocation:
        table_data.append({
            "Subject": item["subject"],
            "Confidence": f"{item['confidence']} / 5",
            "Daily Hours": f"{item['daily_hours']} hrs",
            "Total Hours": f"{item['total_hours']} hrs",
        })
      st.table(table_data)

      pdf_buffer = build_plan_pdf(
          exam, allocation, insight, days_left, daily_hours
      )
      filename = f"{exam['category'].replace(' ', '_')}_study_plan.pdf"
      st.download_button(
          label="📥 Download Study Plan PDF",
          data=pdf_buffer,
          file_name=filename,
          mime="application/pdf",
      )

elif page == "AI Chatbot":
  st.title("🤖 AI Exam Assistant")
  st.write(
      "Ask any question regarding exam prep, study tips, or syllabus topics!"
  )

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input("Ask your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      result = chatbot.get_answer(prompt.strip()[:300])
      answer_text = result.get(
          "answer", "Sorry, I couldn't process that question."
      )
      st.markdown(answer_text)
      st.session_state.messages.append(
          {"role": "assistant", "content": answer_text}
      )

elif page == "Practice Quiz":
  st.title("📝 Practice Quiz")
  exam_keys = list(EXAMS.keys())
  selected_exam_key = st.selectbox(
      "Select Exam for Quiz",
      exam_keys,
      format_func=lambda x: EXAMS[x]["name"],
  )
  exam = EXAMS[selected_exam_key]
  questions = QUIZZES.get(selected_exam_key)

  if not questions:
    st.warning("No quiz available for this exam yet.")
  else:
    with st.form(f"quiz_form_{selected_exam_key}"):
      user_answers = {}
      for i, q in enumerate(questions):
        st.markdown(f"**Q{i+1}: {q['q']}**")
        user_answers[i] = st.radio(
            "Choose option:", q["options"], key=f"q_{selected_exam_key}_{i}"
        )
        st.markdown("---")

      submit_quiz = st.form_submit_button("Submit Quiz")

    if submit_quiz:
      score = 0
      for i, q in enumerate(questions):
        selected_option = user_answers[i]
        selected_index = q["options"].index(selected_option)
        if selected_index == q["answer"]:
          score += 1

      st.subheader(
          f"Your Score: {score} / {len(questions)} ({(score/len(questions))*100:.1f}%)"
      )

      for i, q in enumerate(questions):
        selected_option = user_answers[i]
        selected_index = q["options"].index(selected_option)
        correct_option = q["options"][q["answer"]]

        if selected_index == q["answer"]:
          st.success(
              f"Q{i+1}: {q['q']} — Your answer: {selected_option} (Correct!)"
          )
        else:
          st.error(
              f"Q{i+1}: {q['q']} — Your answer: {selected_option} | Correct"
              f" answer: {correct_option}"
          )

elif page == "Exam Countdown":
  st.title("⏳ Exam Countdown Timer")
  exam_keys = list(EXAMS.keys())
  selected_exam_key = st.selectbox(
      "Select Exam", exam_keys, format_func=lambda x: EXAMS[x]["name"]
  )
  exam = EXAMS[selected_exam_key]

  target_date = st.date_input(
      "Target Exam Date", min_value=datetime.now().date()
  )

  if st.button("Calculate Countdown"):
    today = datetime.now().date()
    days_left = (target_date - today).days
    if days_left < 0:
      st.error("The selected date has already passed!")
    else:
      st.success(
          f"Countdown for {exam['name']}: **{days_left} days** remaining until"
          f" {target_date.strftime('%B %d, %Y')}!"
      )