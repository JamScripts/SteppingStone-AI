import streamlit as st
import os
from google import genai
from datetime import date
from milestones import format_milestones_for_prompt

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
        # Initializing the modern Gen AI Client
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as init_e:
        st.error(f"Failed to initialize AI Client: {init_e}")
else:
    st.error("🔑 Error: GEMINI_API_KEY not found. Please check your Railway Variables.")

def calculate_months(birth_date):
    today = date.today()
    return (today.year - birth_date.year) * 12 + today.month - birth_date.month

# --- 4. USER INTERFACE (UI) ---
st.title("🧩 SteppingStone AI")
st.subheader("Your Personal Developmental Gift Scout")

with st.sidebar:
    st.header("Child's Profile")
    dob = st.date_input("Birth Date", value=date(2024, 11, 1))
    months = calculate_months(dob)
    st.metric(label="Age in Months", value=f"{months}m")
    st.write("---")
    st.caption(f"Tracking ID: {AMAZON_ID}")

# --- 5. AGENT LOGIC ---
if st.button("Analyze Milestones & Find Gifts"):
    if not client:
        st.warning("Agent brain is offline. Set API Key in Railway.")
    else:
        milestone_context = format_milestones_for_prompt(months)
        prompt_text = f"""
        You are SteppingStone AI, an expert in child development and clean-swap toy curation.
        The child is {months} months old. 
        
        Use this CDC milestone context when tailoring the response:
        {milestone_context}
        
        1. List 2-3 specific developmental milestones for a {months}-month-old using the CDC context above.
        2. Suggest 3 'Stepping Stone' gifts that help them reach the NEXT milestone.
        3. Focus on high-quality, non-toxic, or wooden brands.
        4. Provide Amazon search links with tag={AMAZON_ID}.
        """
        
        with st.spinner("SteppingStone AI is analyzing developmental data..."):
            try:
                # Primary Attempt: Gemini 3.1 Flash (The state-of-the-art in 2026)
                response = client.models.generate_content(
                    model="gemini-3.1-flash", 
                    contents=prompt_text
                )
                st.markdown(response.text)
            except Exception as e:
                # Secondary Attempt: Gemini 2.5 Flash (The high-reliability stable model)
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt_text
                    )
                    st.markdown(response.text)
                except Exception as final_e:
                    st.error(f"Agent Error: {final_e}")

st.divider()
st.caption("SteppingStone AI | Building foundations through play.")
