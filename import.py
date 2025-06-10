import streamlit as st
import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta

# ========== SETUP ==========
GENAI_API_KEY = "AIzaSyC3Cbb1kPNDDgI_OW1XKRnEA6vZUis1Xoo"  # Replace with actual key
genai.configure(api_key=GENAI_API_KEY)

def generate_schedule(tasks, style):
    prompt = (
        f"Create a daily schedule with time-blocking and productivity tips.\n\n"
        f"Tasks: {tasks}\n"
        f"Preferred Productivity Style: {style}\n"
        f"Include: start/end times, task descriptions, productivity insights.\n"
    )
    model = genai.GenerativeModel('gemini-2.0 flash')
    response = model.generate_content(prompt)
    return response.text.strip()

def parse_schedule_to_table(generated_text):
    # This function assumes that the generated schedule has lines like:
    # "9:00 AM - 10:00 AM: Task Name"
    rows = []
    for line in generated_text.split('\n'):
        if " - " in line and ":" in line:
            try:
                time_part, task = line.split(":", 1)
                start_end = time_part.strip().split(" - ")
                if len(start_end) == 2:
                    rows.append({
                        "Start Time": start_end[0].strip(),
                        "End Time": start_end[1].strip(),
                        "Task": task.strip()
                    })
            except:
                continue
    return pd.DataFrame(rows)

def save_pdf(schedule_text, filename="schedule.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in schedule_text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    return filename

# ========== STREAMLIT UI ==========
st.set_page_config(page_title="Time Management Coach", layout="centered")
st.title("⏰ Time Management Coach")
st.markdown("Enter your tasks and preferences to get a smart, time-blocked schedule with productivity insights.")

# Task input
tasks_input = st.text_area("📝 Enter Your Tasks (Optional: with priority or duration)", height=200,
                           placeholder="E.g.\n1. Check emails\n2. Project work (2 hrs, High priority)\n3. Team meeting")

# Style selection
style = st.selectbox("💡 Choose Your Productivity Style", ["Pomodoro", "Deep Work", "Balanced", "Time-Boxing", "Focus Sprint"])

# Action buttons
generate = st.button("Generate Schedule")
regenerate = st.button("Regenerate")

# Session state
if "schedule_text" not in st.session_state:
    st.session_state.schedule_text = ""

if (generate or regenerate) and tasks_input:
    with st.spinner("Generating your personalized schedule..."):
        st.session_state.schedule_text = generate_schedule(tasks_input, style)

if st.session_state.schedule_text:
    st.subheader("🗓️ Your Time-Blocked Schedule")
    st.text_area("Generated Schedule", st.session_state.schedule_text, height=300)

    # Visualize in table
    df_schedule = parse_schedule_to_table(st.session_state.schedule_text)
    if not df_schedule.empty:
        st.dataframe(df_schedule)

    # Download as PDF
    if st.button("Download Schedule as PDF"):
        filename = save_pdf(st.session_state.schedule_text)
        with open(filename, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="schedule.pdf", mime="application/pdf")

st.markdown("---")
st.info("Tip: Include durations or priorities in your tasks to get better results!")
