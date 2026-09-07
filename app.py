"""AI Study Pack Generator - Streamlit application."""

import os
import streamlit as st

from workflow import WorkflowError, run_workflow


st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide",
)

st.title("📚 AI Study Pack Generator")
st.markdown("### Plan → Generate → Assess → Review → Refine")
st.caption(
    "A personalized multi-stage AI workflow for creating high-quality study packs."
)

# Load API key from Streamlit Secrets or environment variable
try:
    secret_key = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    secret_key = ""

with st.sidebar:
    st.header("⚙️ AI Settings")

    api_key = st.text_input(
        "Groq API Key",
        value=secret_key or os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="For deployment, store GROQ_API_KEY in Streamlit Secrets.",
    )

    model = st.selectbox(
    "Groq Model",
    [
        "llama-3.1-8b-instant",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
    ],
    index=0,
    )

    st.divider()

    st.info(
        "Never commit your API key to GitHub. "
        "Use Streamlit Secrets for deployment."
    )


# ---------------------------------------------------------
# LEARNER PROFILE
# ---------------------------------------------------------

st.subheader("👤 Learner Profile")

left, right = st.columns(2)

with left:
    subject = st.text_input(
        "📖 Subject",
        placeholder="e.g. Biology",
    )

    topic = st.text_input(
        "🎯 Topic",
        placeholder="e.g. Photosynthesis",
    )

    level = st.selectbox(
        "🎓 Student Level",
        [
            "Class 6",
            "Class 7",
            "Class 8",
            "Class 9",
            "Class 10",
            "Class 11",
            "Class 12",
            "College",
            "Beginner",
            "Intermediate",
            "Advanced",
        ],
    )

    prior_knowledge = st.text_area(
        "🧠 Prior Knowledge",
        placeholder="What does the student already know about this topic?",
    )


with right:
    pack_type = st.selectbox(
        "🧰 Study Pack Type",
        [
            "Complete Study Pack",
            "Revision Notes",
            "Quiz + Answer Key",
            "Flashcards",
            "Exam Preparation Pack",
            "Concept Explainer + Practice",
        ],
    )

    difficulty = st.select_slider(
        "🔥 Difficulty",
        options=["Easy", "Medium", "Hard"],
        value="Medium",
    )

    study_time = st.selectbox(
        "⏱️ Available Study Time",
        [
            "15 minutes",
            "30 minutes",
            "1 hour",
            "2 hours",
            "3+ hours",
        ],
    )

    language = st.selectbox(
        "🌐 Language",
        [
            "English",
            "Urdu",
            "Roman Urdu",
            "English + Urdu",
        ],
    )


extra = st.text_area(
    "📝 Additional Instructions",
    placeholder=(
        "e.g. Focus on board-exam questions, "
        "use simple explanations, include formulas and examples."
    ),
)


st.divider()

generate = st.button(
    "🚀 Generate Personalized Study Pack",
    type="primary",
    use_container_width=True,
)


# ---------------------------------------------------------
# RUN WORKFLOW
# ---------------------------------------------------------

if generate:

    if not api_key.strip():
        st.error("❌ Please provide your Groq API key.")
        st.stop()

    if not subject.strip() or not topic.strip():
        st.warning("⚠️ Please enter both a subject and topic.")
        st.stop()

    learner_profile = {
        "subject": subject.strip(),
        "topic": topic.strip(),
        "level": level,
        "pack_type": pack_type,
        "difficulty": difficulty,
        "study_time": study_time,
        "language": language,
        "prior_knowledge": prior_knowledge.strip(),
        "additional_instructions": extra.strip(),
    }

    progress_bar = st.progress(0)
    status = st.empty()

    def update_progress(stage: str, value: int) -> None:
        status.info(f"🔄 Running stage: **{stage}**")
        progress_bar.progress(value)

    try:

        with st.spinner("AI workflow is running..."):

            result = run_workflow(
                learner_profile=learner_profile,
                api_key=api_key.strip(),
                model=model,
                progress_callback=update_progress,
            )

        st.session_state["workflow_result"] = result

        progress_bar.progress(100)

        status.success(
            "✅ All 5 AI workflow stages completed!"
        )

    except WorkflowError as exc:

        status.empty()
        progress_bar.empty()

        st.error(
            f"❌ Workflow error: {exc}"
        )

        st.stop()

    except Exception as exc:

        status.empty()
        progress_bar.empty()

        st.error(
            "❌ An unexpected error occurred. "
            "Please check your inputs and deployment logs."
        )

        st.caption(
            f"Technical detail: {exc}"
        )

        st.stop()


# ---------------------------------------------------------
# DISPLAY RESULT
# ---------------------------------------------------------

if "workflow_result" in st.session_state:

    result = st.session_state["workflow_result"]

    st.divider()

    st.header("📘 Final Study Pack")

    st.markdown(
        result["final_pack"]
    )

    st.download_button(
        label="⬇️ Download Study Pack",
        data=result["final_pack"],
        file_name="study_pack.md",
        mime="text/markdown",
        use_container_width=True,
    )

    st.divider()

    st.header("🔍 Workflow Details")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🗺️ Planning",
            "✍️ Draft",
            "📊 Assessment",
            "🔎 Review",
            "🔗 Context Flow",
        ]
    )

    # Planning
    with tab1:
        st.json(result["plan"])

    # Draft
    with tab2:
        st.markdown(result["draft"])

    # Assessment
    with tab3:

        assessment = result["assessment"]

        scores = [
            assessment.get("accuracy_score", 0),
            assessment.get("coverage_score", 0),
            assessment.get("level_fit_score", 0),
            assessment.get("clarity_score", 0),
            assessment.get("personalization_score", 0),
        ]

        overall_score = sum(scores) / len(scores)

        st.metric(
            "Overall Quality Score",
            f"{overall_score:.1f}/100",
        )

        st.json(assessment)

    # Review
    with tab4:
        st.json(result["review"])

    # Context flow
    with tab5:

        st.markdown(
            "**Context passing used by this application:**\n\n"
            "`Learner Profile` → "
            "`Planning` → "
            "`Content Generation` → "
            "`Assessment` → "
            "`Review` → "
            "`Refinement` → "
            "`Final Study Pack`"
        )

        st.write(
            "The refinement stage receives:"
        )

        st.code(
            "learner_profile + plan + draft + assessment + review"
        )

    # Clear result
    if st.button("🗑️ Clear Current Results"):

        del st.session_state["workflow_result"]

        st.rerun()


st.divider()

st.caption(
    "AI Study Pack Generator • Python + Streamlit + Groq"
)
