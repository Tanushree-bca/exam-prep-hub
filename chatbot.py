"""
chatbot.py - a small retrieval-based AI chatbot for exam questions.

How it works (NLP, no external API needed):
1. We keep a knowledge base of questions and answers (KB below).
2. Every example question is converted into numbers using TF-IDF
   (a standard NLP technique that gives rare, meaningful words more weight).
3. When a student asks something, we convert it the same way and use
   cosine similarity to find the closest question in the knowledge base.
4. If the match is strong enough we reply with its answer; otherwise we
   say we are not sure and suggest questions the bot can answer.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

CONFIDENCE_THRESHOLD = 0.30
NOTE = "\n\nℹ️ Please confirm details in the latest official notification."

KB = [
    # ---------- small talk ----------
    {"tag": "greeting",
     "questions": ["hi", "hello", "hey", "hii", "good morning", "good evening", "hello there"],
     "answer": "Hello! 👋 I'm the Exam Prep Assistant. Ask me about UPSC, SSC, Banking, Railway, State PSC or Defence exams — eligibility, exam pattern, study tips, or how to use this app."},
    {"tag": "thanks",
     "questions": ["thanks", "thank you", "thanks a lot", "thank you so much", "ok thanks"],
     "answer": "You're welcome! Good luck with your preparation 🙌"},
    {"tag": "about_bot",
     "questions": ["who are you", "what can you do", "what is this chatbot", "help me", "what can i ask you"],
     "answer": "I'm an AI chatbot built into the Exam Prep Hub. I can answer questions about eligibility and exam pattern for UPSC, SSC CGL, IBPS PO, RRB NTPC, State PSC and NDA, give study tips, and explain how to use this website.",
     "suggest": "What can you help me with?"},

    # ---------- generic (exam not named) ----------
    {"tag": "generic_eligibility",
     "questions": ["what is the eligibility", "eligibility criteria", "what is the age limit", "who can apply", "qualification required"],
     "answer": "Eligibility depends on the exam. Which one do you mean — UPSC, SSC CGL, IBPS PO, RRB NTPC, State PSC or NDA? Try asking, for example: \"UPSC eligibility\" or \"NDA age limit\".",
     "suggest": "What is the eligibility for UPSC?"},
    {"tag": "generic_pattern",
     "questions": ["what is the exam pattern", "how many marks is the exam", "how many questions are asked", "is there negative marking", "what is the syllabus pattern"],
     "answer": "The pattern is different for every exam. Which one do you mean — UPSC, SSC CGL, IBPS PO, RRB NTPC, State PSC or NDA? Try asking, for example: \"SSC CGL exam pattern\".",
     "suggest": "What is the SSC CGL exam pattern?"},

    # ---------- UPSC ----------
    {"tag": "upsc_about",
     "questions": ["what is upsc", "what is the upsc civil services exam", "tell me about the ias exam", "what is ias ips exam", "what is civil services examination"],
     "answer": "UPSC (Union Public Service Commission) conducts the Civil Services Examination for top central services such as IAS, IPS and IFS. It is one of the most competitive exams in India.",
     "suggest": "What is the UPSC Civil Services exam?"},
    {"tag": "upsc_stages",
     "questions": ["what are the stages of upsc", "upsc exam pattern", "how many stages in the civil services exam", "prelims mains interview upsc", "structure of civil services examination"],
     "answer": "The UPSC Civil Services Exam has three stages:\n• Preliminary (objective, screening)\n• Main (written, descriptive papers)\n• Personality Test / Interview\nYour final rank is decided by the Main exam and Interview marks." + NOTE,
     "suggest": "What are the stages of the UPSC exam?"},
    {"tag": "upsc_eligibility",
     "questions": ["upsc eligibility", "who can apply for upsc", "educational qualification for ias", "qualification for upsc", "eligibility criteria for civil services"],
     "answer": "For UPSC Civil Services you need a bachelor's degree from a recognised university (final-year students can apply but must show the degree later). Check the notification for the exact rules." + NOTE,
     "suggest": "What is the eligibility for UPSC?"},
    {"tag": "upsc_age_attempts",
     "questions": ["what is the age limit for upsc", "upsc age limit", "how many attempts for upsc", "how many chances do i get in upsc", "how many times can i write civil services", "maximum age for ias exam", "number of attempts civil services"],
     "answer": "Roughly: general category candidates can apply from age 21 up to 32 with 6 attempts. OBC candidates get 3 extra years (9 attempts) and SC/ST candidates get 5 extra years (no limit on attempts within the age limit)." + NOTE,
     "suggest": "What is the age limit and attempts for UPSC?"},
    {"tag": "upsc_prelims",
     "questions": ["upsc prelims pattern", "how many papers in upsc prelims", "what is csat", "negative marking in upsc prelims", "civil services preliminary exam marks"],
     "answer": "UPSC Prelims has two objective (MCQ) papers of 200 marks each: General Studies Paper I and CSAT (Paper II). CSAT is only qualifying (33% needed). There is negative marking of one-third for wrong answers. Prelims marks are not counted in the final ranking." + NOTE,
     "suggest": "What is the UPSC Prelims pattern?"},
    {"tag": "upsc_mains",
     "questions": ["upsc mains pattern", "how many papers in upsc mains", "total marks in upsc", "upsc interview marks", "personality test marks civil services"],
     "answer": "UPSC Mains has 9 papers, of which 7 are counted for 1750 marks (Essay, four General Studies papers and two Optional subject papers). The two language papers are qualifying only. The Interview is 275 marks, so the total for ranking is 2025." + NOTE,
     "suggest": "What is the UPSC Mains pattern and interview marks?"},
    {"tag": "upsc_books",
     "questions": ["best books for upsc", "upsc books", "which books to read for ias", "ncert for upsc", "books for civil services preparation"],
     "answer": "Popular starting points for UPSC: NCERT textbooks (Class 6–12) for basics, Indian Polity by M. Laxmikanth, the Economic Survey, and a daily newspaper for current affairs. Also see the 'Recommended Books' section on the UPSC page of this site.",
     "suggest": "Which books should I read for UPSC?"},

    # ---------- SSC CGL ----------
    {"tag": "ssc_about",
     "questions": ["what is ssc cgl", "ssc cgl full form", "tell me about ssc cgl", "what does cgl stand for", "combined graduate level exam"],
     "answer": "SSC CGL (Combined Graduate Level) is conducted by the Staff Selection Commission to recruit graduates for Group B and Group C posts in central government ministries and departments.",
     "suggest": "What is SSC CGL?"},
    {"tag": "ssc_pattern",
     "questions": ["ssc cgl exam pattern", "ssc cgl tiers", "how many tiers in ssc cgl", "ssc cgl tier 1 syllabus", "ssc cgl negative marking"],
     "answer": "SSC CGL has Tier-I and Tier-II. Tier-I is 100 questions for 200 marks in 60 minutes, with four sections of 25 questions each: Reasoning, General Awareness, Quantitative Aptitude and English. Wrong answers carry 0.50 negative marking. Tier-II has further papers depending on the post." + NOTE,
     "suggest": "What is the SSC CGL exam pattern?"},
    {"tag": "ssc_eligibility",
     "questions": ["ssc cgl eligibility", "who can apply for ssc cgl", "ssc cgl age limit", "ssc cgl qualification", "age criteria for combined graduate level exam"],
     "answer": "For most SSC CGL posts you need a bachelor's degree from a recognised university. The age limit depends on the post (commonly between 18 and 32 years) with relaxations for reserved categories." + NOTE,
     "suggest": "What is the eligibility for SSC CGL?"},

    # ---------- Banking ----------
    {"tag": "banking_about",
     "questions": ["what is ibps po", "tell me about ibps", "what is ibps", "bank po exam", "institute of banking personnel selection"],
     "answer": "IBPS (Institute of Banking Personnel Selection) conducts recruitment exams for public sector banks. PO stands for Probationary Officer, an entry-level officer post in a bank.",
     "suggest": "What is IBPS PO?"},
    {"tag": "banking_pattern",
     "questions": ["ibps po exam pattern", "ibps po prelims", "ibps po mains", "ibps po stages", "rounds in bank po recruitment", "negative marking in ibps po"],
     "answer": "IBPS PO has three stages: Prelims, Mains and Interview. Prelims is 100 questions for 100 marks in 60 minutes (English, Quantitative Aptitude, Reasoning) with 0.25 negative marking, and is qualifying in nature. Mains has an objective test plus a descriptive paper." + NOTE,
     "suggest": "What is the IBPS PO exam pattern?"},
    {"tag": "banking_eligibility",
     "questions": ["ibps po eligibility", "ibps po age limit", "qualification for bank po", "who can apply for ibps po", "minimum qualification for probationary officer"],
     "answer": "For IBPS PO you need a bachelor's degree in any discipline from a recognised university. The usual age range is 20 to 30 years, with relaxations for reserved categories." + NOTE,
     "suggest": "What is the eligibility for IBPS PO?"},

    # ---------- Railway ----------
    {"tag": "railway_about",
     "questions": ["what is rrb ntpc", "ntpc full form", "tell me about railway ntpc", "railway exam", "what posts can i get through ntpc", "which jobs does ntpc fill", "what jobs does ntpc give"],
     "answer": "RRB NTPC stands for Railway Recruitment Board Non-Technical Popular Categories. It fills non-technical railway posts such as Station Master, Goods Guard, Clerk and Typist.",
     "suggest": "What is RRB NTPC?"},
    {"tag": "railway_pattern",
     "questions": ["rrb ntpc exam pattern", "ntpc stages", "ntpc cbt 1", "ntpc negative marking", "how many questions in ntpc"],
     "answer": "RRB NTPC has a first-stage CBT (100 questions, 90 minutes: General Awareness 40, Mathematics 30, Reasoning 30) with one-third negative marking, followed by a second-stage CBT, then a typing/skill or aptitude test and document verification depending on the post." + NOTE,
     "suggest": "What is the RRB NTPC exam pattern?"},
    {"tag": "railway_eligibility",
     "questions": ["rrb ntpc eligibility", "ntpc qualification", "ntpc age limit", "can a 12th pass student apply for ntpc", "who can apply for railway ntpc"],
     "answer": "Graduate-level NTPC posts need a bachelor's degree; undergraduate-level posts need 12th pass. The age range is roughly 18 to 33 for graduate posts and 18 to 30 for undergraduate posts, with relaxations." + NOTE,
     "suggest": "What is the eligibility for RRB NTPC?"},

    # ---------- State PSC ----------
    {"tag": "state_about",
     "questions": ["what is state psc", "what is psc exam", "state civil services exam", "what is kpsc", "tnpsc uppsc kpsc difference"],
     "answer": "Every state has its own Public Service Commission (PSC) that conducts the state civil services exam — for example KPSC in Karnataka, TNPSC in Tamil Nadu and UPPSC in Uttar Pradesh.",
     "suggest": "What is a State PSC exam?"},
    {"tag": "state_pattern",
     "questions": ["state psc exam pattern", "state psc syllabus", "state psc stages", "how is the state civil services exam structured", "state psc preliminary mains interview"],
     "answer": "Most State PSC exams follow Prelims, Mains and Interview, but the exact pattern and syllabus differ by state. They usually combine general studies with state-specific topics such as local history, geography and culture. Check your own state PSC website." + NOTE,
     "suggest": "What is the State PSC exam pattern?"},

    # ---------- Defence ----------
    {"tag": "defence_about",
     "questions": ["what is nda", "nda full form", "tell me about the nda exam", "national defence academy exam", "where is the national defence academy located"],
     "answer": "The NDA exam is conducted by UPSC (twice a year) for entry into the Army, Navy and Air Force wings of the National Defence Academy, which is located at Khadakwasla, Pune.",
     "suggest": "What is the NDA exam?"},
    {"tag": "defence_eligibility",
     "questions": ["nda eligibility", "nda age limit", "who can apply for nda", "nda qualification", "can girls apply for nda", "age limit to join nda", "can women apply for nda", "are girls allowed in nda"],
     "answer": "For NDA you need to have passed (or be appearing in) 12th. The Army wing accepts any stream; the Air Force and Navy wings need Physics and Mathematics. Candidates must be unmarried and roughly 16.5 to 19.5 years old at course start. Women candidates are now eligible too." + NOTE,
     "suggest": "What is the eligibility for NDA?"},
    {"tag": "defence_pattern",
     "questions": ["nda exam pattern", "nda written exam", "nda ssb", "nda marks", "how many marks is ssb for nda"],
     "answer": "The NDA written exam has Mathematics (300 marks) and General Ability Test (600 marks), 900 in total, with negative marking. Qualified candidates then go to the SSB interview (900 marks), and the final merit list combines both." + NOTE,
     "suggest": "What is the NDA exam pattern?"},

    # ---------- study tips ----------
    {"tag": "tip_plan",
     "questions": ["how to make a study plan", "how to plan my preparation", "how to start preparing for government exams", "where should i start", "where do i begin my govt exam preparation", "how do i prepare a timetable", "make a timetable for competitive exams", "daily routine for exam preparation"],
     "answer": "A simple way to start:\n1. Read the syllabus and exam pattern first.\n2. Rate yourself honestly in each subject.\n3. Give more time to weak subjects.\n4. Revise every week and take mock tests.\nYou can use the AI Study Plan Generator on this site to do steps 2–3 automatically.",
     "suggest": "How do I make a study plan?"},
    {"tag": "tip_hours",
     "questions": ["how many hours should i study", "how many hours daily for government exams", "study hours per day", "how many hours a day should an aspirant study", "how much time per day should i study", "how much time is enough for preparation"],
     "answer": "There is no fixed rule. Many aspirants study about 6–8 hours a day for UPSC and 3–5 hours for other exams, but consistency and focus matter more than the number. Take short breaks and sleep well.",
     "suggest": "How many hours should I study daily?"},
    {"tag": "tip_revision",
     "questions": ["how to revise", "how to remember what i study", "revision strategy", "how to avoid forgetting", "how to not forget what i studied", "best way to retain what i read"],
     "answer": "Revise a topic within 24 hours, again after a week, and again after a month. Make short notes, test yourself by recalling without looking, and solve practice questions instead of only re-reading.",
     "suggest": "How should I revise?"},
    {"tag": "tip_current_affairs",
     "questions": ["how to prepare current affairs", "current affairs preparation", "what to read daily newspaper", "how should i read newspapers for exams"],
     "answer": "Spend 30–45 minutes daily on a good newspaper, note down government schemes, economy and international news, and revise a monthly compilation. Don't try to memorise everything — focus on topics linked to your syllabus.",
     "suggest": "How do I prepare current affairs?"},
    {"tag": "tip_mock",
     "questions": ["are mock tests important", "how many mock tests should i take", "how to analyse mock test", "how often should i give mock exams"],
     "answer": "Yes, mock tests are very important. Take them in real exam conditions with a timer, then spend as much time analysing your mistakes as you spent attempting. Take them weekly at first and more often in the last month.",
     "suggest": "How important are mock tests?"},
    {"tag": "tip_stress",
     "questions": ["i am stressed", "how to deal with exam stress", "i feel demotivated", "how to stay motivated", "burnout", "i am feeling very anxious about my exam"],
     "answer": "Feeling stressed during preparation is very common. Try setting small daily goals, sleeping properly, taking short breaks and some exercise. If it feels too heavy, please talk to a friend, family member or teacher you trust — you don't have to carry it alone. 💙",
     "suggest": "How do I handle exam stress?"},
    {"tag": "tip_speed",
     "questions": ["how to improve speed in maths", "how to solve faster", "time management in exam", "how to manage time during the exam", "tips for solving aptitude questions quickly"],
     "answer": "Practise tables, squares and basic shortcuts, solve questions with a timer, and in the exam skip very hard questions on the first round and come back to them later.",
     "suggest": "How can I solve questions faster?"},

    # ---------- about this app ----------
    {"tag": "app_study_plan",
     "questions": ["how to use the study plan generator", "what is the study plan generator", "how does the ai study planner work", "how do i use the ai study planner on this site", "what do the sliders mean", "what is confidence rating", "how are study hours allocated"],
     "answer": "In the AI Study Plan Generator you pick your exam, rate your confidence (1–5) in each subject, then enter your exam date and daily study hours. Weaker subjects automatically get more daily time. You can download the result as a PDF.",
     "suggest": "How does the AI Study Plan Generator work?"},
    {"tag": "app_countdown_quiz",
     "questions": ["how to use countdown", "what is the countdown timer", "how does the quiz work", "practice quiz", "what is the practice quiz"],
     "answer": "The Countdown Timer shows a live countdown to your exam date. The Practice Quiz gives a few sample questions for your chosen exam and shows your score with the correct answers straight away.",
     "suggest": "How does the practice quiz work?"},
    {"tag": "app_how",
     "questions": ["how does this chatbot work", "what ai is used", "is this chatgpt", "how do you work", "what technology does this chatbot use", "how do you give answers", "how does the bot answer my questions"],
     "answer": "I'm a retrieval-based NLP chatbot. Your question is converted into numbers using TF-IDF, and I use cosine similarity to find the closest question in my knowledge base. I don't use any external AI service, and if I'm not sure I'll say so instead of guessing.",
     "suggest": "How does this chatbot work?"},

    # ---------- things the bot should not guess ----------
    {"tag": "exam_dates",
     "questions": ["when is the exam", "what is the exam date", "upsc exam date", "ssc cgl exam date", "when is the nda exam", "when will the next upsc notification come out"],
     "answer": "I don't have live exam dates because they change every year. Please check the official calendar on the exam's website — each exam page in the Exam Hub has an 'Official Website' link.",
     "suggest": "When is the next exam?"},
    {"tag": "syllabus_papers",
     "questions": ["where can i get the syllabus", "syllabus pdf", "previous year question papers", "where to download previous papers", "where to download old question papers"],
     "answer": "Open any exam in the Exam Hub — each page has links for the Syllabus, Previous Year Papers and Notes.",
     "suggest": "Where can I find the syllabus and previous papers?"},
    {"tag": "best_exam",
     "questions": ["which exam is best for me", "which government exam should i choose", "easiest government exam", "which exam is easy", "which exam is the easiest"],
     "answer": "There is no single best or easiest exam — it depends on your qualification, age and interests. Graduates can look at UPSC, SSC CGL, IBPS PO and RRB NTPC; 12th-pass students can look at NDA and some RRB posts. Compare their pages in the Exam Hub.",
     "suggest": "Which government exam should I choose?"},
]

# ---------- exam and topic detection ------