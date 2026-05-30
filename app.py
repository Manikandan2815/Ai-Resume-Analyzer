from flask import Flask, render_template, request
import pdfplumber
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

SKILLS_DATABASE = [
    "Python", "Java", "C", "C++", "C#", "JavaScript",
    "HTML", "CSS", "React", "Angular", "Vue",
    "Node.js", "Express", "Flask", "Django",
    "SQL", "MySQL", "PostgreSQL", "MongoDB",
    "Git", "GitHub",
    "Machine Learning", "Deep Learning",
    "Artificial Intelligence", "Data Science",
    "Pandas", "NumPy", "TensorFlow", "PyTorch",
    "Power BI", "Excel",
    "AWS", "Azure", "Docker",
    "Linux"
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "resume" not in request.files:
        return "No file selected"

    file = request.files["resume"]

    if file.filename == "":
        return "No file selected"

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    resume_text = ""

    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if text:
                    resume_text += text + "\n"

    except Exception as e:
        return f"PDF Error: {e}"

    resume_lower = resume_text.lower()

    detected_skills = []

    for skill in SKILLS_DATABASE:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, resume_lower):
            detected_skills.append(skill)

    detected_skills = sorted(list(set(detected_skills)))

    # Resume Score
    score = min(100, len(detected_skills) * 8)

    # Missing Skills
    important_skills = ["Python", "HTML", "CSS", "Git", "SQL", "Flask"]

    missing_skills = [
        skill for skill in important_skills
        if skill not in detected_skills
    ]

    # Suggestions
    suggestions = []

    if "Git" not in detected_skills:
        suggestions.append("Learn Git and GitHub")

    if "GitHub" not in detected_skills:
        suggestions.append("Create a GitHub portfolio")

    if "SQL" not in detected_skills:
        suggestions.append("Add SQL knowledge")

    if "Flask" not in detected_skills:
        suggestions.append("Build Flask projects and deploy them")

    if "Machine Learning" not in detected_skills:
        suggestions.append("Explore Machine Learning fundamentals")

    if len(detected_skills) < 5:
        suggestions.append("Add more technical skills to improve ATS score")

    if len(suggestions) == 0:
        suggestions.append("Strong technical profile. Keep building projects.")

    # ATS Analysis
    ats_score = 0
    ats_checks = []

    if "@" in resume_text:
        ats_score += 20
        ats_checks.append("✅ Email Found")
    else:
        ats_checks.append("❌ Email Missing")

    if "education" in resume_lower:
        ats_score += 20
        ats_checks.append("✅ Education Section Found")
    else:
        ats_checks.append("❌ Education Section Missing")

    if "project" in resume_lower:
        ats_score += 20
        ats_checks.append("✅ Projects Section Found")
    else:
        ats_checks.append("❌ Projects Section Missing")

    if len(detected_skills) >= 5:
        ats_score += 20
        ats_checks.append("✅ Skills Section Strong")
    elif len(detected_skills) >= 3:
        ats_score += 10
        ats_checks.append("⚠️ Skills Section Average")
    else:
        ats_checks.append("❌ Skills Section Weak")

    if "github" in resume_lower:
        ats_score += 20
        ats_checks.append("✅ GitHub Profile Found")
    else:
        ats_checks.append("❌ GitHub Profile Missing")

    # Career Role
    career_role = "General"

    if (
        "Machine Learning" in detected_skills
        or "Artificial Intelligence" in detected_skills
        or "Data Science" in detected_skills
    ):
        career_role = "Machine Learning Engineer"

    elif (
        "HTML" in detected_skills
        or "CSS" in detected_skills
        or "JavaScript" in detected_skills
    ):
        career_role = "Web Developer"

    elif "Python" in detected_skills:
        career_role = "Python Developer"

    return render_template(
        "result.html",
        score=score,
        ats_score=ats_score,
        career_role=career_role,
        detected_skills=detected_skills,
        missing_skills=missing_skills,
        suggestions=suggestions,
        ats_checks=ats_checks,
        resume_text=resume_text
    )


if __name__ == "__main__":
    app.run(debug=True)