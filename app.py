import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from resume_analysis import build_suggestions, extract_skills, get_health_status
from resume_parser import ResumeReadError, extract_resume_text

st.set_page_config(
    page_title="AI Resume Match Analyzer",
    page_icon="📄",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        color: #17121e;
        background:
            radial-gradient(ellipse at 90% 0%, #e6d6ff 0%, transparent 52%),
            linear-gradient(145deg, #ffffff 0%, #f2f1f5 55%, #dedde5 100%);
        font-family: "Segoe UI", Arial, sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1440px;
        padding: 3.5rem 2.5rem;
    }

    .workspace-badge {
        display: inline-block;
        padding: 0.6rem 1rem;
        border: 1px solid #21152f;
        border-radius: 999px;
        background: #ede3ff;
        color: #5420a3;
        font-size: 15px;
        font-weight: 750;
        letter-spacing: 0.1em;
        margin-bottom: 0.6rem;
    }

    [data-testid="stHeading"] h1 {
        color: #17121e;
        font-size: clamp(2.6rem, 5vw, 4.5rem);
        font-weight: 800;
        letter-spacing: -0.045em;
        line-height: 1.12;
        padding-bottom: 1rem;
    }

    [data-testid="stHeading"] h2,
    [data-testid="stHeading"] h3 {
        color: #241239;
        font-size: clamp(1.5rem, 2.5vw, 2rem);
        font-weight: 750;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: #292330;
        font-size: 20px;
        line-height: 1.65;
    }

    div[data-testid="stTextArea"] {
        padding: 1.4rem;
        border: 1.5px solid #21152f;
        border-radius: 22px;
        background: linear-gradient(155deg, #ffffff, #f8f6fc);
        box-shadow: 5px 5px 0 #ddd4eb;
        margin: 0.8rem 0 1rem;
        transition: box-shadow 180ms ease;
    }

    div[data-testid="stTextArea"]:focus-within {
        box-shadow: 0 0 0 3px #c4a4ef, 5px 5px 0 #ddd4eb;
    }

    div[data-testid="stTextArea"] label p {
        color: #17121e;
        font-size: 23px;
        font-weight: 700;
    }

    div[data-testid="stTextArea"] textarea {
        color: #17121e !important;
        background: #ffffff !important;
        -webkit-text-fill-color: #17121e !important;
        caret-color: #702bce;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 22px !important;
        line-height: 1.6 !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder {
        color: #655b73 !important;
        -webkit-text-fill-color: #655b73 !important;
        opacity: 1;
    }

    .stButton > button[kind="primary"] {
        min-height: 60px;
        padding: 0.8rem 2.2rem;
        border: 2px solid #21152f;
        border-radius: 14px;
        background: linear-gradient(115deg, #6524bd, #823ddd);
        color: #ffffff;
        box-shadow: 4px 4px 0 #21152f;
        transition: transform 180ms ease, box-shadow 180ms ease;
    }

    .stButton > button[kind="primary"] p {
        color: #ffffff;
        font-size: 21px;
        font-weight: 700;
    }

    .stButton > button[kind="primary"]:hover {
        color: #ffffff;
        border-color: #21152f;
        transform: translateY(-2px);
        box-shadow: 4px 6px 0 #21152f;
    }

    .stButton > button[kind="primary"]:focus-visible {
        outline: 3px solid #702bce;
        outline-offset: 5px;
    }

    [data-testid="stMetric"] {
        padding: 1.4rem;
        background: linear-gradient(135deg, #ffffff, #eee6fa);
        border: 1.5px solid #21152f;
        border-radius: 20px;
        box-shadow: 4px 4px 0 #ddd4eb;
        animation: card-enter 350ms ease-out;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricValue"] p {
        color: #6524bd;
        font-size: clamp(2.4rem, 4vw, 3.6rem);
        font-weight: 800;
    }

    [data-testid="stMetricLabel"] p {
        color: #292330;
        font-size: 19px;
        font-weight: 650;
    }

    [data-testid="stCaptionContainer"] p {
        color: #544a61;
        font-size: 17px;
    }

    .health-card {
        padding: 1.3rem 1.5rem;
        margin-top: 1rem;
        border: 1.5px solid #21152f;
        border-left: 7px solid;
        border-radius: 18px;
        background: linear-gradient(120deg, #ffffff, #f1ecf8);
    }

    .health-card h3 {
        font-size: 25px;
        margin: 0 0 0.4rem;
    }

    @keyframes card-enter {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] {
            padding: 2rem 1rem;
        }

        div[data-testid="stTextArea"] {
            padding: 1rem;
        }

        .stButton > button[kind="primary"] {
            width: 100%;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        div[data-testid="stTextArea"],
        .stButton > button[kind="primary"] {
            transition: none;
        }

        [data-testid="stMetric"] {
            animation: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="workspace-badge">RESUME INTELLIGENCE / MATCH WORKSPACE</div>',
    unsafe_allow_html=True,
)
st.title("AI Resume Match Analyzer")
st.write("Discover how well your resume matches your next opportunity.")


def load_resume_upload():
    uploaded_file = st.session_state["resume_upload"]
    st.session_state.pop("resume_upload_error", None)
    if uploaded_file is None:
        return

    try:
        text = extract_resume_text(uploaded_file.getvalue(), uploaded_file.name)
    except ResumeReadError as error:
        st.session_state["resume_upload_error"] = str(error)
    else:
        st.session_state["resume_editor"] = text


resume_column, job_column = st.columns(2)

with resume_column:
    uploaded_resume = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        max_upload_size=5,
        key="resume_upload",
        on_change=load_resume_upload,
        help="Drag a file here or browse. Text-based PDF, Word, or UTF-8 text; max 5 MB.",
    )
    upload_error = st.session_state.get("resume_upload_error")
    if upload_error:
        st.error(f"{upload_error} The text box has not been changed.")
    elif uploaded_resume is not None:
        st.success("Resume loaded. Review or edit the extracted text below.")

    resume_text = st.text_area(
        "Your resume",
        height=300,
        placeholder="Paste your resume here, or upload a file above...",
        key="resume_editor",
    )
    st.caption(
        "Uploaded text is copied here for review. Removing the file keeps "
        "the text so you can continue editing. If you change the original "
        "file, save and upload the updated copy again."
    )

with job_column:
    job_text = st.text_area(
        "Job description",
        height=300,
        placeholder="Paste the job description here...",
    )


if st.button("Analyze Match", type="primary"):
    if upload_error:
        st.error("Remove the unreadable file or upload another before analyzing.")
    elif not resume_text.strip() or not job_text.strip():
        st.warning("Please paste both your resume and the job description.")
    else:
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_text)

        if not job_skills:
            st.warning(
                "No supported skills were detected in the job description. "
                "Try including skills such as Python, SQL, AWS, or Excel."
            )
        else:
            matched_skills = sorted(resume_skills & job_skills)
            missing_skills = sorted(job_skills - resume_skills)
            match_score = round(
                len(matched_skills) / len(job_skills) * 100
            )

            st.divider()
            st.subheader("Your Match Results")
            st.caption(
                "Based on coverage of supported skills detected in the "
                "job description—not a prediction of hiring success."
            )

            with st.expander("See detected resume and job skills"):
                st.write(
                    "**Detected in your resume:** "
                    + (", ".join(sorted(resume_skills)) or "None detected")
                )
                st.write(
                    "**Detected in the job description:** "
                    + ", ".join(sorted(job_skills))
                )
                st.caption(
                    "A skill counts as matched only when detected in both texts. "
                    "Data Engineer and Data Engineering count as the same skill."
                )

            score_col, matched_col, missing_col = st.columns(3)

            score_col.metric("Match Score", f"{match_score}%")
            matched_col.metric("Matched Skills", len(matched_skills))
            missing_col.metric("Missing Skills", len(missing_skills))

            gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=match_score,
                    number={"suffix": "%", "font": {"color": "#6524bd"}},
                    title={"text": "Resume Match"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#702bce"},
                        "bgcolor": "#ffffff",
                        "bordercolor": "#21152f",
                        "borderwidth": 2,
                        "steps": [
                            {"range": [0, 60], "color": "#eeedf2"},
                            {"range": [60, 90], "color": "#e6d6ff"},
                            {"range": [90, 100], "color": "#c4a4ef"},
                        ],
                    },
                )
            )

            gauge.update_layout(
                height=320,
                margin={"t": 70, "b": 25, "l": 40, "r": 40},
                paper_bgcolor="rgba(0,0,0,0)",
                font={"family": "Segoe UI", "color": "#17121e", "size": 20},
            )

            comparison = pd.DataFrame({
                "Status": ["Matched Skills", "Missing Skills"],
                "Count": [len(matched_skills), len(missing_skills)],
            })
            skills_chart = go.Figure(
                go.Bar(
                    x=comparison["Status"].tolist(),
                    y=comparison["Count"].tolist(),
                    marker_color=["#702bce", "#c5b7d7"],
                    marker_line={"color": "#21152f", "width": 1.5},
                    text=comparison["Count"].tolist(),
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="%{x}: %{y}<extra></extra>",
                )
            )
            skills_chart.update_layout(
                title={"text": "Skills Comparison", "x": 0.5},
                height=320,
                margin={"t": 70, "b": 45, "l": 40, "r": 30},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"family": "Segoe UI", "color": "#17121e", "size": 18},
                yaxis={
                    "title": "Number of skills",
                    "dtick": 1,
                    "range": [0, max(comparison["Count"]) + 1],
                    "gridcolor": "#ded8e7",
                },
                xaxis={"fixedrange": True},
                showlegend=False,
            )

            gauge_column, chart_column = st.columns(2)
            with gauge_column:
                st.plotly_chart(gauge, width="stretch")
            with chart_column:
                st.plotly_chart(skills_chart, width="stretch")

            health_label, health_color = get_health_status(match_score)
            st.markdown(
                f'<section class="health-card" style="border-left-color: {health_color}">'
                f'<h3>Resume Health: <span style="color: {health_color}">'
                f'{health_label} &middot; {match_score}%</span></h3>'
                '<p>Alignment-based: uses your match score, not a full resume '
                'or ATS assessment.</p></section>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Excellent: 90–100 · Good: 75–89 · Fair: 60–74 · "
                "Needs Improvement: below 60"
            )

            found_col, gaps_col = st.columns(2)

            with found_col:
                st.subheader("Top Skills Found")
                if matched_skills:
                    for skill in matched_skills:
                        st.write(f"✅ {skill}")
                else:
                    st.info("No matching skills found yet.")

            with gaps_col:
                st.subheader("Missing Keywords")
                if missing_skills:
                    for skill in missing_skills:
                        st.write(f"❌ {skill}")
                else:
                    st.success("All detected job skills appear in your resume.")

            st.subheader("Your Improvement Plan")
            st.caption(
                "Rule-based guidance. Only include skills and achievements "
                "you can demonstrate; never add experience you do not have."
            )
            for suggestion in build_suggestions(missing_skills, resume_text):
                st.write(f"- {suggestion}")