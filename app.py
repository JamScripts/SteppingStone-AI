import os
from datetime import date

import streamlit as st
from google import genai
from milestones import format_milestones_for_prompt, get_relevant_cdc_milestones


# --- 1. BRANDING & PAGE CONFIG ---
st.set_page_config(page_title="SteppingStone AI", page_icon="🧩", layout="centered")


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


def render_nurture_milestones(age_months, container):
    container.header("Nurture Milestones")
    container.caption(f"Weekly growth tracker for {age_months} months")

    checked_count = 0
    total_count = sum(len(milestones) for milestones in NURTURE_WEEKLY_MILESTONES.values())

    for category, milestones in NURTURE_WEEKLY_MILESTONES.items():
        container.subheader(category)
        for milestone in milestones:
            key = f"nurture_{category}_{milestone}"
            if container.checkbox(milestone, key=key):
                checked_count += 1

    container.progress(checked_count / total_count if total_count else 0)
    container.caption(f"{checked_count} of {total_count} seen today")


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


GLASSMORPHISM_CSS = """
<style>
    #MainMenu,
    footer,
    [data-testid="stToolbar"],
    .stDeployButton {
        visibility: hidden;
        height: 0;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(132, 204, 197, 0.28), transparent 34rem),
            radial-gradient(circle at bottom right, rgba(245, 158, 123, 0.22), transparent 32rem),
            linear-gradient(135deg, #f8fbfa 0%, #eef7f5 45%, #fff7f0 100%);
    }

    .product-recommendation-card {
        margin: 1rem 0;
        padding: 1.15rem 1.25rem;
        background: rgba(255, 255, 255, 0.62);
        border: 1px solid rgba(255, 255, 255, 0.72);
        border-radius: 8px;
        box-shadow: 0 18px 42px rgba(70, 97, 88, 0.14);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }

    .product-recommendation-card h3 {
        margin-top: 0;
        color: #24433c;
    }

    .product-recommendation-card a {
        color: #1d7f72;
        font-weight: 700;
    }
</style>
"""


# --- 4. USER INTERFACE (UI) ---
st.markdown(GLASSMORPHISM_CSS, unsafe_allow_html=True)
st.title("🧩 SteppingStone AI")
st.subheader("Your Personal Developmental Gift Scout")

with st.sidebar:
    render_safe_materials_guide()

st.header("Child's Profile")
profile_columns = st.columns([2, 1])
with profile_columns[0]:
    dob = st.date_input("Birth Date", value=date(2024, 11, 1))
months = calculate_months(dob)
with profile_columns[1]:
    st.metric(label="Age in Months", value=f"{months}m")

with st.expander("Nurture Milestones", expanded=False):
    render_nurture_milestones(months, st)


# --- 5. AGENT LOGIC ---
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
        You are SteppingStone AI, an expert in child development and clean-swap toy curation.
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
        """

        with st.spinner("SteppingStone AI is analyzing developmental data..."):
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
st.caption("SteppingStone AI | Building foundations through play.")
