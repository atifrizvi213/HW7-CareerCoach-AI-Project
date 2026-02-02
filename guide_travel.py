# --------------------------------------------------
# AI Travel Guide Planner
# - Multi-city trips
# - Budget estimation (per person)
# - Age-aware AI itinerary
# --------------------------------------------------

import os
from textwrap import dedent

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from datetime import datetime

# ReportLab imports (REQUIRED for PDF)
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
)

# -------------------------
# ENV
# -------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# STREAMLIT CONFIG
# -------------------------
st.set_page_config(
    page_title="Travel Guide Planner",
    page_icon="🌍",
    layout="centered",
)

# -------------------------
# SESSION STATE
# -------------------------
def init_state():
    st.session_state.setdefault("cities", "")
    st.session_state.setdefault("days", 3)
    st.session_state.setdefault("interests", [])
    st.session_state.setdefault("guardrails", "")
    st.session_state.setdefault("daily_budget", 300)
    st.session_state.setdefault("num_people", 1)
    st.session_state.setdefault("ages", "")
    st.session_state.setdefault("plan_md", "")

def reset_all():
    st.session_state.clear()
    init_state()

init_state()

# -------------------------
# BUDGET ESTIMATION
# -------------------------
def estimate_budget(days, daily_budget, num_people):
    total_daily = daily_budget * num_people

    breakdown = {
        "Accommodation": total_daily * 0.4 * days,
        "Food": total_daily * 0.25 * days,
        "Transport": total_daily * 0.15 * days,
        "Activities": total_daily * 0.2 * days,
    }
    return breakdown, sum(breakdown.values())

# -------------------------
# OPENAI PROMPT
# -------------------------
SYSTEM_PROMPT = dedent("""
You are a professional travel planner.
Create a realistic, day-by-day itinerary.
Adapt activities based on ages (kids, adults, seniors).
Respect guardrails strictly.

Format:

## City Name
### Day 1
- Morning:
- Afternoon:
- Evening:
""")

def build_prompt(cities, days, interests, guardrails, num_people, ages):
    return dedent(f"""
Cities: {", ".join(cities)}
Days per city: {days}

Travel Group:
- Number of people: {num_people}
- Ages: {ages or "Not specified"}

Interests: {", ".join(interests) or "General sightseeing"}
Guardrails: {guardrails or "None"}

Guidelines:
- Include kid-friendly or senior-friendly activities if applicable
- Avoid physically demanding activities when younger kids or seniors are present
- Balance rest and exploration

Generate a practical itinerary.
""")

def generate_itinerary(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=1800,
    )
    return response.choices[0].message.content

 #-------------------------
# PDF HELPERS (ReportLab)
# -------------------------
def markdown_to_flowables(md_text, styles):
    flow = []
    body = styles["BodyText"]
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6)

    for line in md_text.splitlines():
        if line.startswith("## "):
            flow.append(Paragraph(line[3:], h2))
        elif line.startswith("- "):
            flow.append(ListFlowable(
                [ListItem(Paragraph(line[2:], body))],
                bulletType="bullet"
            ))
        else:
            flow.append(Paragraph(line or " ", body))
        flow.append(Spacer(1, 4))
    return flow

def write_pdf(markdown_text, filename="travel_plan.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=LETTER,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    styles = getSampleStyleSheet()
    story = []

    title = Paragraph("AI Travel Guide Plan", styles["Title"])
    meta = Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles["Normal"],
    )

    story.extend([title, Spacer(1, 10), meta, Spacer(1, 12)])
    story.extend(markdown_to_flowables(markdown_text, styles))

    doc.build(story)
    return filename

# -------------------------
# UI
# -------------------------
st.title("🌍 Travel Guide Planner")
st.caption("Multi-city • Budget-aware • Age-aware itinerary")

with st.form("travel_form"):
    st.text_area(
        "Destinations (CITY level – one per line)",
        placeholder="Rome, Italy\nParis, France",
        key="cities",
    )

    st.number_input(
        "Number of Days (per city)",
        min_value=1,
        max_value=14,
        key="days",
    )

    st.number_input(
        "Number of People",
        min_value=1,
        max_value=20,
        key="num_people",
    )

    st.text_input(
        "Age(s) of Travelers (comma-separated)",
        placeholder="5, 12, 34, 60",
        key="ages",
    )

    st.multiselect(
        "Special Interests",
        ["Museums", "Food & Cuisine", "Historic Sites", "Nature", "Shopping"],
        key="interests",
    )

    st.text_area(
        "Guardrails / Constraints",
        placeholder="No walking tours, kid-friendly only",
        key="guardrails",
    )

    st.number_input(
        "Estimated Daily Budget (USD per person)",
        min_value=50,
        max_value=1000,
        step=10,
        key="daily_budget",
    )

    submitted = st.form_submit_button("✨ Generate Travel Plan")

# -------------------------
# MAIN ACTION
# -------------------------
if submitted:
    cities = [c.strip() for c in st.session_state["cities"].splitlines() if c.strip()]

    if not cities:
        st.warning("Please enter at least one city.")
    else:
        with st.spinner("Generating your personalized travel itinerary..."):
            prompt = build_prompt(
                cities,
                st.session_state["days"],
                st.session_state["interests"],
                st.session_state["guardrails"],
                st.session_state["num_people"],
                st.session_state["ages"],
            )
            st.session_state["plan_md"] = generate_itinerary(prompt)

# -------------------------
# OUTPUT
# -------------------------
if st.session_state["plan_md"]:
    st.success("Travel plan generated!")

    st.subheader("🗺️ AI Itinerary")
    st.markdown(st.session_state["plan_md"])

    # Budget
    st.divider()
    st.subheader("💰 Budget Estimate")

    total_days = st.session_state["days"] * len(
        [c for c in st.session_state["cities"].splitlines() if c.strip()]
    )

    breakdown, total = estimate_budget(
        total_days,
        st.session_state["daily_budget"],
        st.session_state["num_people"],
    )

    for k, v in breakdown.items():
        st.write(f"{k}: ${v:,.2f}")

    st.write(f"### Total Estimated Cost: ${total:,.2f}")
# PDF Download
    try:
        pdf_path = write_pdf(st.session_state["plan_md"])
        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇️ Download PDF",
                data=f.read(),
                file_name="travel_plan.pdf",
                mime="application/pdf",
            )
    except Exception as e:
        st.error(f"PDF generation failed: {e}")

# -------------------------
# RESET
# -------------------------
st.divider()
st.button("🔁 Reset Form", on_click=reset_all, type="secondary")
