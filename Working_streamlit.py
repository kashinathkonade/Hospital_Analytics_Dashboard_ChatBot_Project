import streamlit as st
import pandas as pd
import os
import base64
import time
import google.generativeai as genai

# Configure your API key for Google Generative AI
genai.configure(api_key="AIzaSyBxCOi6uS0G1UKgq-aFgHE3umgrgCAA6Q8")

# Function to convert a local image to Base64 string
def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# Sidebar with branding
st.sidebar.markdown(
    """
    <div style='position: fixed; bottom: 0; left: 60px; font-size: 17px;'>
        <span style='color: gray;'>Powered by</span> 
        <a href='https://www.aispry.com' target='_blank' style='color: #b8860b; text-decoration: none; font-weight: bold;'>AiSPRY</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Image file path for the sidebar logo
image_path = r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\AiSPRY logo.jpg"
image_base64 = get_image_as_base64(image_path)

# Sidebar logo and project title
st.sidebar.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/jpg;base64,{image_base64}" alt="AiSPRY Logo" width="150">
        <h2 style="color: #4CAF50; font-family: 'Arial Black', sans-serif; font-size: 28px; font-weight: bold;">
            Hospital Analytics Project
        </h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar navigation
st.sidebar.title("Navigation")
navigation = st.sidebar.radio("Go to", ["Welcome", "Dashboard", "Chatbot"])

# Main page content
if navigation == "Welcome":
    st.title("Welcome to HealthCare Analytics")
    st.write("Navigate to the Dashboard or Chatbot using the sidebar.")
elif navigation == "Dashboard":
    st.title("Hospital Analytics Dashboard")
    dashboard_url = "https://app.powerbi.com/view?r=eyJrIjoiYzQyYjEwZTctNGQ3Yi00ZGMxLTgzODMtZDZlYzU4Yzk0Y2IzIiwidCI6IjQyY2VjMjM1LTc4MTUtNDNhYy1iNjdiLTAxNTFkYmZkZmQ4ZiJ9"
    st.markdown(f"""
        <iframe title="Power BI Dashboard" width="100%" height="600px" src="{dashboard_url}" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)
elif navigation == "Chatbot":
    st.title("Hospital Analytics Chatbot")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)
            st.write("CSV File Preview:")
            st.dataframe(df.head())

            # Process CSV file with Google Generative AI
            with st.spinner("Uploading file and initializing chatbot..."):
                # Upload file to Google Generative AI
                files = [genai.upload_file(uploaded_file.name, mime_type="text/csv")]
                for file in files:
                    while file.state.name == "PROCESSING":
                        time.sleep(10)
                        file = genai.get_file(file.name)
                    if file.state.name != "ACTIVE":
                        st.error(f"File {file.name} failed to process.")
                        st.stop()

                st.success("File uploaded and processed successfully!")
                st.session_state.df = df

            # Chat interface
            question = st.text_input("Ask a question about the uploaded data:")
            if question:
                with st.spinner("Processing your question..."):
                    # Send query to Google Generative AI
                    prompt = f"""
                    Analyze the uploaded CSV file and answer the question:
                    {question}
                    """
                    chat_response = genai.GenerativeModel(
                        model_name="gemini-2.0-flash-exp"
                    ).generate(prompt)
                    st.write("Response:")
                    st.write(chat_response)
        except Exception as e:
            st.error(f"Error processing file: {e}")
