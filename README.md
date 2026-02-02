# HW7-CareerCoach-AI-Project
## Project
Consultant Systems Engineer 
ATIF ALI RIZVI

## Purpose
To use AI-powered Travel Guide Planner web app to plan the new vacation
This is classic AI-assisted workflow with four stages:
  1. Human input
  2. Prompt engineering
  3. AI reasoning & generation
  4. Post-processing & delivery

## What the Code Does
- Collects structured travel preferences from a user
- Uses an AI model to reason and generate a custom itinerary
- Combines AI output with deterministic logic (budget math)
- Produces a human-readable plan and a downloadable PDF
The key idea:
👉 AI is used for planning and creativity; traditional code handles rules, math, and presentation

This code demonstrates human-in-the-loop AI:
  1. Human defines goals and constraints
  2. AI generates a plan within those constraints
  3. Software validates, formats, and distributes the result
The AI augments human planning, rather than replacing logic or control.

## How to RUN
  1. Install requirements :
    python -m venv venv
    source venv/bin/activate   # Mac/Linux
    venv\Scripts\activate      # Windows
  2. Set your OpenAI API key
     OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
  3. Run the app
     streamlit run app.py
     http://localhost:8501


