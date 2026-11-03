from flask import Flask, render_template, abort, request, send_file, jsonify
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import io
import chatbot
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

app = Flask(__name__)


def search_link(query):
    """Builds a working Google search link for a given query - used whenever
    we don't have one single official link (e.g. State PSC varies by state,
    and curated notes pages don't have one fixed official URL)."""
    return f"https://www.google.com/search?q={quote_plus(query)}"


# ---------- Exam Data ----------
# In a real system this might come from a database.
# For now we keep it simple with a Python dictionary.

EXAMS = {
    "upsc": {
        "name": "UPSC Civil Services Examination",
        "category": "UPSC",
        "date": "Check UPSC official calendar",
        "syllabus_link": "https://upsc.gov.in/examinations/syllabus",
        "papers_link": "https://upsc.gov.in/examinations/previous-question-papers",
        "notes_link": search_link("UPSC Civil Services preparation notes"),
        "books": ["NCERT History, Geography, Polity (Class 6-12)", "Indian Polity - M. Laxmikanth", "Economic Survey (latest edition)"],
        "official_link": "https://upsc.gov.in",
        "subjects": ["History", "Geography", "Polity", "Economy", "Current Affairs", "Science & Tech", "Ethics"],
    },
    "ssc": {
        "name": "SSC CGL (Combined Graduate Level)",
        "category": "SSC",
        "date": "Check SSC official calendar",
        "syllabus_link": "https://ssc.nic.in/Portal/Syllabus",
        "papers_link": "https://ssc.nic.in/Portal/PreviousQuestionPapers",
        "notes_link": search_link("SSC CGL preparation notes"),
        "books": ["Quantitative Aptitude - R.S. Aggarwal", "General English - S.P. Bakshi", "Lucent's General Knowledge"],
        "official_link": "https://ssc.nic.in",
        "subjects": ["Quantitative Aptitude", "Reasoning", "English", "General Awareness"],
        "site_note": True,
    },
    "banking": {
        "name": "IBPS PO (Probationary Officer)",
        "category": "Banking / IBPS",
        "date": "Check IBPS official calendar",
        "syllabus_link": "https://www.ibps.in/",
        "papers_link": search_link("IBPS PO previous year question papers"),
        "notes_link": search_link("IBPS PO preparation notes"),
        "books": ["Quantitative Aptitude for Competitive Examinations", "Banking Awareness Handbook", "Reasoning - R.S. Aggarwal"],
        "official_link": "https://www.ibps.in",
        "subjects": ["Quantitative Aptitude", "Reasoning", "English", "Banking Awareness", "Computer Knowledge"],
    },
    "railway": {
        "name": "RRB NTPC (Non-Technical Popular Categories)",
        "category": "Railway",
        "date": "Check RRB official calendar",
        "syllabus_link": search_link("RRB NTPC official syllabus"),
        "papers_link": search_link("RRB NTPC previous year question papers"),
        "notes_link": search_link("RRB NTPC preparation notes"),
        "books": ["RRB NTPC Guide", "General Science for Railway Exams", "Previous Year Solved Papers"],
        "official_link": "https://indianrailways.gov.in",
        "subjects": ["Mathematics", "General Intelligence", "General Science", "General Awareness"],
        "site_note": True,
    },
    "state": {
        "name": "State PSC (Public Service Commission)",
        "category": "State Government",
        "date": "Varies by state",
        "syllabus_link": search_link("State PSC exam syllabus"),
        "papers_link": search_link("State PSC previous year question papers"),
        "notes_link": search_link("State PSC preparation notes"),
        "books": ["State-specific GK Handbook", "NCERT Books (Class 6-12)", "Previous Year State PSC Papers"],
        "official_link": search_link("State PSC official website"),
        "subjects": ["State History & Geography", "Polity", "Economy", "Current Affairs", "General Science"],
        "varies_note": True,
    },
    "defence": {
        "name": "NDA (National Defence Academy)",
        "category": "Defence",
        "date": "Check UPSC/NDA official calendar",
        "syllabus_link": "https://upsc.gov.in/examinations/syllabus",
        "papers_link": "https://upsc.gov.in/examinations/previous-question-papers",
        "notes_link": search_link("NDA exam preparation notes"),
        "books": ["NDA Mathematics - R.S. Aggarwal", "General Ability Test Guide", "NCERT Science & Social Studies"],
        "official_link": "https://upsc.gov.in",
        "subjects": ["Mathematics", "General Ability", "English", "Science", "Current Affairs"],
    },
}


QUIZZES = {
    "upsc": [
        {"q": "Who is known as the Father of the Indian Constitution?", "options": ["Mahatma Gandhi", "B.R. Ambedkar", "Jawaharlal Nehru", "Sardar Patel"], "answer": 1},
        {"q": "The Fundamental Rights are enshrined in which part of the Indian Constitution?", "options": ["Part II", "Part III", "Part IV", "Part V"], "answer": 1},
        {"q": "Which river is known as the 'Sorrow of Bihar'?", "options": ["Ganga", "Yamuna", "Kosi", "Son"], "answer": 2},
    ],
    "ssc": [
        {"q": "Find the next number: 2, 6, 12, 20, 30, ?", "options": ["36", "40", "42", "44"], "answer": 2},
        {"q": "What is the synonym of 'Abundant'?", "options": ["Scarce", "Plentiful", "Limited", "Rare"], "answer": 1},
        {"q": "What is 15% of 200?", "options": ["20", "25", "30", "35"], "answer": 2},
    ],
    "banking": [
        {"q": "RBI was established in which year?", "options": ["1935", "1947", "1950", "1969"], "answer": 0},
        {"q": "What does NEFT stand for?", "options": ["National Electronic Funds Transfer", "New Electronic Fast Transfer", "National Economic Fund Transfer", "None of these"], "answer": 0},
        {"q": "A, B, C are siblings. A is B's brother. C is A's sister. What is C to B?", "options": ["Brother", "Sister", "Cannot be determined", "Mother"], "answer": 1},
    ],
    "railway": [
        {"q": "Who is known as the father of Indian Railways?", "options": ["Lord Dalhousie", "Lord Curzon", "Lord Mountbatten", "Lord Wellesley"], "answer": 0},
        {"q": "Which is the longest railway platform in India?", "options": ["Gorakhpur", "Kharagpur", "Kollam", "Bilaspur"], "answer": 0},
        {"q": "If a train travels 60 km in 45 minutes, what is its speed in km/h?", "options": ["75", "80", "85", "90"], "answer": 1},
    ],
    "state": [
        {"q": "Which is the largest state in India by area?", "options": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh"], "answer": 2},
        {"q": "The Governor of a state is appointed by whom?", "options": ["Prime Minister", "Chief Minister", "President", "Parliament"], "answer": 2},
        {"q": "Panchayati Raj system was given constitutional status by which amendment?", "options": ["42nd", "61st", "73rd", "86th"], "answer": 2},
    ],
    "defence": [
        {"q": "The National Defence Academy (NDA) is located in which state?", "options": ["Maharashtra", "Uttar Pradesh", "Rajasthan", "Punjab"], "answer": 0},
        {"q": "Who is the Supreme Commander of the Indian Armed Forces?", "options": ["Prime Minister", "President", "Defence Minister", "Chief of Army Staff"], "answer": 1},
        {"q": "What does INS (used before Indian naval ship names) stand for?", "options": ["Indian National Ship", "Indian Naval Ship", "International Naval Ship", "Indian Navy Station"], "answer": 1},
    ],
}


def generate_weighted_plan(subjects, confidence, days_left, daily_hours):
    """
    Confidence-based smart allocation.
    The user rates their confidence in each subject from 1 (weak) to 5 (strong).
    Weaker subjects automatically get more daily study time.
    """
    # Lower confidence -> higher weight -> more time allocated
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

    # Weakest subjects first
    allocation.sort(key=lambda x: x["confidence"])

    weakest = allocation[0]
    strongest = allocation[-1]
    insight = (
        f"Your weakest area is {weakest['subject']} (confidence {weakest['confidence']}/5) — "
        f"we've allocated {weakest['daily_hours']} hrs/day to it. "
        f"{strongest['subject']} is your strongest area, so it gets less daily time."
    )

    return allocation, insight


@app.route("/")
def home():
    return render_template("home.html", exams=EXAMS)


@app.route("/exam/<exam_id>")
def exam_detail(exam_id):
    exam = EXAMS.get(exam_id)
    if not exam:
        abort(404)
    return render_template("exam_detail.html", exam=exam, exam_id=exam_id)


@app.route("/study-plan")
def study_plan_select():
    """Step 1: pick which exam you're preparing for."""
    return render_template("study_plan_select.html", exams=EXAMS)


@app.route("/study-plan/<exam_id>", methods=["GET", "POST"])
def study_plan(exam_id):
    """Step 2: rate confidence per subject, then get a weighted plan."""
    exam = EXAMS.get(exam_id)
    if not exam:
        abort(404)

    allocation = None
    insight = None
    error = None
    exam_date_str = None
    daily_hours = None
    days_left = None

    if request.method == "POST":
        exam_date_str = request.form.get("exam_date")
        daily_hours = request.form.get("daily_hours")
        confidence = {}
        for subj in exam["subjects"]:
            confidence[subj] = int(request.form.get(f"confidence_{subj}", 3))

        try:
            daily_hours = float(daily_hours)
            exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            days_left = (exam_date - today).days

            if days_left <= 0:
                error = "Please choose an exam date in the future."
            elif daily_hours <= 0:
                error = "Daily study hours must be greater than 0."
            else:
                allocation, insight = generate_weighted_plan(
                    exam["subjects"], confidence, days_left, daily_hours
                )
        except (ValueError, TypeError):
            error = "Please fill in all fields correctly."

    return render_template(
        "study_plan.html",
        exam=exam,
        exam_id=exam_id,
        allocation=allocation,
        insight=insight,
        error=error,
        exam_date_str=exam_date_str,
        daily_hours=daily_hours,
        days_left=days_left,
    )


def build_plan_pdf(exam, allocation, insight, days_left, daily_hours):
    """Builds a downloadable PDF of the personalized study plan."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Study Plan")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"AI Study Plan - {exam['name']}", styles["Title"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Days until exam: {days_left}", styles["Normal"]))
    elements.append(Paragraph(f"Daily study hours available: {daily_hours}", styles["Normal"]))
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
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


@app.route("/study-plan/<exam_id>/pdf", methods=["POST"])
def study_plan_pdf(exam_id):
    exam = EXAMS.get(exam_id)
    if not exam:
        abort(404)

    exam_date_str = request.form.get("exam_date")
    daily_hours = request.form.get("daily_hours")
    confidence = {}
    for subj in exam["subjects"]:
        confidence[subj] = int(request.form.get(f"confidence_{subj}", 3))

    try:
        daily_hours = float(daily_hours)
        exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_left = (exam_date - today).days
        if days_left <= 0 or daily_hours <= 0:
            abort(400)
    except (ValueError, TypeError):
        abort(400)

    allocation, insight = generate_weighted_plan(exam["subjects"], confidence, days_left, daily_hours)
    pdf_buffer = build_plan_pdf(exam, allocation, insight, days_left, daily_hours)

    filename = f"{exam['category'].replace(' ', '_')}_study_plan.pdf"
    return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)


@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html", suggestions=chatbot.suggestions_for_start())


@app.route("/chatbot/ask", methods=["POST"])
def chatbot_ask():
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Please type a question."}), 400
    result = chatbot.get_answer(message.strip()[:300])
    return jsonify(result)


@app.route("/quiz")
def quiz_select():
    """Pick which exam's practice quiz you want to try."""
    return render_template("quiz_select.html", exams=EXAMS)


@app.route("/quiz/<exam_id>", methods=["GET", "POST"])
def quiz(exam_id):
    exam = EXAMS.get(exam_id)
    questions = QUIZZES.get(exam_id)
    if not exam or not questions:
        abort(404)

    results = None
    score = None

    if request.method == "POST":
        results = []
        score = 0
        for i, q in enumerate(questions):
            selected = request.form.get(f"q{i}")
            selected_index = int(selected) if selected is not None else None
            is_correct = selected_index == q["answer"]
            if is_correct:
                score += 1
            results.append({
                "question": q["q"],
                "options": q["options"],
                "correct_index": q["answer"],
                "selected_index": selected_index,
                "is_correct": is_correct,
            })

    return render_template(
        "quiz.html",
        exam=exam,
        exam_id=exam_id,
        questions=questions,
        results=results,
        score=score,
        total=len(questions),
    )


@app.route("/countdown")
def countdown_select():
    """Step 1: pick an exam and your target date for the countdown."""
    return render_template("countdown_select.html", exams=EXAMS)


@app.route("/countdown/show")
def countdown_show():
    """Step 2: live countdown display."""
    exam_id = request.args.get("exam_id")
    target_date_str = request.args.get("target_date")

    exam = EXAMS.get(exam_id)
    if not exam or not target_date_str:
        abort(404)

    try:
        datetime.strptime(target_date_str, "%Y-%m-%d")
    except ValueError:
        abort(404)

    return render_template(
        "countdown_show.html",
        exam=exam,
        target_date_str=target_date_str,
    )


if __name__ == "__main__":
    app.run(debug=True)