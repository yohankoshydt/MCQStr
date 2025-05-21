import streamlit as st
from ff import generate_mcqs

st.set_page_config(page_title="MCQ Parse")

st.title("🧠 MCQ Parse")

# Option to upload or enter text

mode = st.radio("Choose mode:", ["parse", "generate"])

user_text = ""
number = None
topic = None

if mode == "parse":
    # Input for parse/generate
    input_method = st.radio("Choose input method:", ["Upload File", "Enter Text"])
    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload a file containing MCQs (.txt only)", type=["txt"])
        if uploaded_file is not None:
            user_text = uploaded_file.read().decode("utf-8")
    elif input_method == "Enter Text":
        user_text = st.text_area("Enter your MCQ content here:", height=300)

# Inputs for generate mode
if mode == "generate":
    number = st.number_input("Number of Questions", min_value=1, max_value=100, value=5)
    topic = st.text_input("Topic")

# Button to trigger either mode
if st.button("Run"):
    if mode == "generate" and (not topic or not number):
        st.warning("Please provide both topic and number of questions.")
    elif user_text.strip() or mode == "generate":
        output = generate_mcqs(mode=mode, content=user_text, number=number, topic=topic)
        
        # Download button
        st.download_button(
            label="📥 Download MCQs as Excel",
            data=output,
            file_name="mcqs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Please provide valid input text.")
