# 📚 Government Exam Preparation Hub

A Flask web application that helps students prepare for government exams — with an exam information hub, an AI study planner, an NLP chatbot, a practice quiz and more.

**Domain:** Artificial Intelligence & Cloud Computing (internship project)

🔗 **Live App:** _add your Render link here after deployment_

---

## ✨ Features

| Feature | What it does |
|---|---|
| **Exam Info Hub** | Pick UPSC, SSC CGL, IBPS PO, RRB NTPC, State PSC or NDA and see the exam date source, syllabus, previous papers, notes, recommended books and official website. |
| **AI Study Plan Generator** | Rate your confidence (1–5) in each subject, enter your exam date and daily study hours — weaker subjects automatically get more time (weighted allocation). |
| **Download Plan as PDF** | Export the generated study plan as a PDF. |
| **Exam Countdown Timer** | A live countdown (days, hours, minutes, seconds) to your exam date. |
| **Practice Quiz** | Sample questions for each exam with instant scoring and correct answers. |
| **AI Chatbot** | Ask about eligibility, exam pattern, study tips or how to use the site. |

## 🧠 How the AI parts work

- **Study planner:** each subject gets weight `6 − confidence`; your daily hours are split in proportion to these weights, so the subjects you are weakest in get the most time.
- **Chatbot:** a retrieval-based NLP bot using **TF-IDF + cosine similarity** (scikit-learn). It first detects which exam you mention and what you want to know (eligibility, pattern, books…), then falls back to similarity search over a knowledge base. If it is not confident it says so instead of guessing. No external AI API or key is used.

## 🛠️ Tech Stack

Python · Flask · HTML/CSS/JavaScript · scikit-learn · ReportLab · Gunicorn · Git/GitHub · Render (cloud hosting)

## 📁 Project Structure

```
exam_prep_hub/
├── app.py               # Flask routes, exam data, study-plan + quiz + PDF logic
├── chatbot.py           # NLP chatbot (knowledge base + TF-IDF matching)
├── requirements.txt     # Python dependencies
├── templates/           # HTML pages
└── static/
    └── style.css        # Styling
```

## ▶️ Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

## ⚠️ Notes

- Exam details (age limits, patterns) are general guidance. Always confirm in the latest official notification.
- Quiz questions are sample practice questions, not official past papers.
- Some government websites may show a browser security warning because of their own certificate settings.

## 👩‍💻 Author

Tanushree — BCA, Internship at Trishna Technology