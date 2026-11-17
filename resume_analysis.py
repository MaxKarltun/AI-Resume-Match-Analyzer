import re
import unicodedata


SKILLS = [
    "Python", "SQL", "Snowflake", "ETL", "Power BI", "AWS", "Azure",
    "Data Engineering", "Machine Learning", "Analytics", "Airflow", "Spark",
    "Excel", "Tableau", "Pandas", "Docker", "Git",
]

SKILL_ALIASES = {
    "Data Engineering": ("Data Engineering", "Data Engineer", "Data Engineers"),
}


def extract_skills(text: str) -> set[str]:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff\u00ad")))
    text = re.sub(r"\s+", " ", text)
    found = set()

    for skill in SKILLS:
        for alias in SKILL_ALIASES.get(skill, (skill,)):
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.add(skill)
                break

    return found


def get_health_status(score: int) -> tuple[str, str]:
    if score >= 90:
        return "Excellent", "#166534"
    if score >= 75:
        return "Good", "#6524bd"
    if score >= 60:
        return "Fair", "#854d0e"
    return "Needs Improvement", "#9f1239"


def build_suggestions(missing_skills: list[str], resume_text: str) -> list[str]:
    suggestions = [
        f"If you have {skill} experience, add a specific example of how you used "
        "it. Otherwise, consider a project to develop that skill."
        for skill in missing_skills
    ]
    impact_pattern = (
        r"\b\d+(?:[.,]\d+)?\s*(?:%|percent\b|hours?\b|minutes?\b|"
        r"seconds?\b|rows?\b|records?\b|users?\b|GB\b|TB\b)|\$\s*\d"
    )
    if not re.search(impact_pattern, resume_text, flags=re.IGNORECASE):
        suggestions.append(
            "Add measurable business impact where supported by your results, "
            "such as time saved, records processed, or percentage improvement. "
            "Use real numbers, not invented metrics."
        )
    if not missing_skills:
        suggestions.append(
            "All detected job skills are covered. Strengthen your project "
            "descriptions with concrete examples relevant to this role."
        )
    return suggestions
