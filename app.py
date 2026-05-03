import os
from datetime import date

import streamlit as st
from google import genai
from milestones import format_milestones_for_prompt, get_relevant_cdc_milestones


# --- 1. BRANDING & PAGE CONFIG ---
st.set_page_config(page_title="Nurture", page_icon="🧩", layout="centered")


# --- 2. SECURE KEY & ID FETCH ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
AMAZON_ID = os.environ.get("AMAZON_ID")

if not GEMINI_API_KEY:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        GEMINI_API_KEY = None

if not AMAZON_ID:
    try:
        AMAZON_ID = st.secrets["AMAZON_ID"]
    except Exception:
        AMAZON_ID = "steppingstone-20"


# --- 3. INITIALIZE THE AI AGENT ---
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as init_e:
        st.error(f"Failed to initialize AI Client: {init_e}")
else:
    st.error(
        "🔑 Error: GEMINI_API_KEY not found. Add it to your Railway environment variables "
        "or use `.streamlit/secrets.toml` for local testing."
    )


NURTURE_WEEKLY_MILESTONES = {
    "Communication": [
        'Tries to say three or more words besides "mama" or "dada"',
        'Follows one-step directions without gestures, like "Give it to me"',
    ],
    "Motor": [
        "Walks without holding on to anyone or anything",
        "Scribbles",
        "Tries to use a spoon",
    ],
    "Social": [
        "Moves away from you, but looks to make sure you are close by",
        "Points to show you something interesting",
        "Looks at a few pages in a book with you",
    ],
    "Self-care": [
        "Drinks from a cup without a lid and may spill sometimes",
        "Feeds themself with fingers",
        "Helps you dress them by pushing an arm through a sleeve or lifting a foot",
    ],
}


def calculate_months(birth_date):
    today = date.today()
    return (today.year - birth_date.year) * 12 + today.month - birth_date.month


def build_required_milestone_context(age_months):
    milestone_match = get_relevant_cdc_milestones(age_months)
    if not milestone_match:
        return ""

    _, milestones = milestone_match
    ordered_milestones = (
        milestones["social_emotional"]
        + milestones["language_communication"]
        + milestones["cognitive"]
        + milestones["movement_physical"]
    )
    required_phrases = ordered_milestones[:2]

    for milestone in ordered_milestones:
        if "spoon" in milestone.lower() and milestone not in required_phrases:
            required_phrases.append(milestone)

    return "\n".join(f"- {milestone}" for milestone in required_phrases)


def get_nurture_progress():
    checked_count = 0
    total_count = sum(len(milestones) for milestones in NURTURE_WEEKLY_MILESTONES.values())

    for category, milestones in NURTURE_WEEKLY_MILESTONES.items():
        for milestone in milestones:
            key = f"nurture_{category}_{milestone}"
            if st.session_state.get(key):
                checked_count += 1

    return checked_count, total_count


def render_nurture_milestones(age_months, container):
    container.header("Nurture Milestones")
    container.caption(f"Weekly growth tracker for {age_months} months")

    for category, milestones in NURTURE_WEEKLY_MILESTONES.items():
        container.subheader(category)
        for milestone in milestones:
            key = f"nurture_{category}_{milestone}"
            container.checkbox(milestone, key=key)


def render_safe_materials_guide():
    st.sidebar.header("Safe Materials Guide")
    st.sidebar.markdown(
        """
        We prioritize toys made with **wood, organic cotton, food-grade silicone, and water-based finishes** because toddlers explore with their hands and mouths.

        Wooden and organic materials are easier to evaluate, tend to last longer, and support open-ended play without noisy electronics or brittle plastic parts.

        Every recommendation should favor:
        - Non-toxic finishes
        - Durable, repairable construction
        - Simple sensory feedback
        - Brands with clear material transparency
        """
    )


NURTURE_THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Quicksand:wght@600;700&display=swap');

    #MainMenu,
    footer,
    [data-testid="stToolbar"],
    .stDeployButton {
        visibility: hidden;
        height: 0;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(135, 206, 235, 0.24), transparent 34rem),
            radial-gradient(circle at bottom right, rgba(244, 151, 173, 0.2), transparent 32rem),
            linear-gradient(135deg, #f8fbfa 0%, #eef8fb 45%, #fff6f8 100%);
    }

    .stApp,
    .stMarkdown,
    [data-testid="stWidgetLabel"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
    }

    h1,
    h2,
    h3,
    .nurture-title {
        font-family: 'Quicksand', sans-serif !important;
        color: #87CEEB !important;
        letter-spacing: 0;
    }

    .nurture-title {
        margin: 0 0 0.2rem;
        font-size: 3rem;
        line-height: 1.05;
        font-weight: 700;
    }

    .section-kicker {
        margin-bottom: 1.5rem;
        color: #4b6268;
        font-size: 1.02rem;
    }

    .stButton > button {
        width: 100%;
        border: 0;
        border-radius: 8px;
        background: #F497AD;
        color: #ffffff;
        font-family: 'Quicksand', sans-serif;
        font-weight: 700;
        box-shadow: 0 12px 28px rgba(244, 151, 173, 0.28);
        transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }

    .stButton > button:hover {
        background: #ef819d;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 16px 34px rgba(244, 151, 173, 0.34);
    }

    .stProgress > div > div > div > div {
        background-color: #F497AD;
    }

    .product-recommendation-card {
        margin: 1rem 0;
        padding: 1.15rem 1.25rem;
        background: rgba(255, 255, 255, 0.62);
        border: 2px solid #87CEEB;
        border-radius: 8px;
        box-shadow: 0 18px 42px rgba(70, 97, 88, 0.14);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }

    .product-recommendation-card:hover {
        transform: translateY(-4px);
        border-color: #64bfdf;
        box-shadow: 0 24px 54px rgba(70, 97, 88, 0.2);
    }

    .product-recommendation-card h3 {
        margin-top: 0;
        color: #87CEEB;
    }

    .product-recommendation-card a {
        color: #F497AD;
        font-weight: 700;
    }
</style>
"""


# --- 4. USER INTERFACE (UI) ---
st.markdown(NURTURE_THEME_CSS, unsafe_allow_html=True)
st.markdown('<h1 class="nurture-title"><strong>🧩 Nurture</strong></h1>', unsafe_allow_html=True)
st.markdown('<p class="section-kicker">Your personal developmental gift scout.</p>', unsafe_allow_html=True)

with st.sidebar:
    render_safe_materials_guide()

if "child_birth_date" not in st.session_state:
    st.session_state.child_birth_date = date(2024, 11, 1)

months = calculate_months(st.session_state.child_birth_date)


# --- 5. AMAZON GIFT RECOMMENDATIONS ---
st.header("Amazon Gift Recommendations")
st.caption("CDC-informed gift ideas for the next developmental step.")

if st.button("Analyze Milestones & Find Gifts"):
    if not client:
        st.warning(
            "Agent brain is offline. Set GEMINI_API_KEY in Railway environment variables "
            "or `.streamlit/secrets.toml` for local testing."
        )
    else:
        milestone_context = format_milestones_for_prompt(months)
        required_milestones = build_required_milestone_context(months)
        prompt_text = f"""
        You are Nurture, an expert in child development and clean-swap toy curation.
        The child is {months} months old.

        Use this CDC milestone context as the source of truth. Mention the relevant CDC
        milestone(s) explicitly before recommending gifts, and do not replace them with invented
        milestones.

        {milestone_context}

        Required CDC milestone phrases: In your first section, mention each of these exact phrases:
        {required_milestones}

        1. List 2-3 specific developmental milestones relevant for a {months}-month-old, using the CDC context above.
        2. Suggest 3 'Stepping Stone' gifts that help them reach the NEXT CDC milestone.
        3. Focus on high-quality, non-toxic, or wooden brands.
        4. Provide Amazon search links with tag={AMAZON_ID}.
        5. Format each of the 3 product recommendations as its own HTML card:
           <div class="product-recommendation-card">...</div>
        6. Inside each product card, include a "Why it Matters" section that explicitly names one
           CDC milestone from the context above and explains how the toy supports that milestone.
        """

        with st.spinner("Nurture is analyzing developmental data..."):
            last_error = None
            for model in ("gemini-2.5-flash", "gemini-2.0-flash"):
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=prompt_text,
                    )
                    st.markdown(response.text, unsafe_allow_html=True)
                    break
                except Exception as model_error:
                    last_error = model_error
            else:
                st.error(f"Agent Error: {last_error}")

st.divider()


# --- 6. CHILD PROFILE & MILESTONES ---
st.header("Child's Profile")
profile_columns = st.columns([2, 1])
with profile_columns[0]:
    st.date_input("Birth Date", key="child_birth_date")
months = calculate_months(st.session_state.child_birth_date)
with profile_columns[1]:
    st.metric(label="Age in Months", value=f"{months}m")

with st.expander("Nurture Milestones", expanded=False):
    render_nurture_milestones(months, st)

st.divider()


# --- 7. DEVELOPMENTAL PROGRESS ---
st.header("Developmental Progress")
checked_count, total_count = get_nurture_progress()
st.progress(checked_count / total_count if total_count else 0)
st.caption(f"{checked_count} of {total_count} milestones seen today")
st.caption("Nurture | Building foundations through play.")
