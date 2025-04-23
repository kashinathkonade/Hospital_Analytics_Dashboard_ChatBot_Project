import streamlit as st
import base64
import os
import time
import pandas as pd
import re
import google.generativeai as genai

# Configure your API key for Google Generative AI
genai.configure(api_key="AIzaSyDd4OKiCLlGW716L-ezmgvP4DrnN3nEHc4")

# Set Streamlit page configuration
st.set_page_config(page_title="Hospital Analytics Project", layout="wide")

# Function to convert a local image to Base64 string
def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# Image file path for the sidebar logo
image_path = r"C:\\Users\\kashinath konade\\Downloads\\Hospital Analytics Project\\AiSPRY logo.jpg"
image_base64 = get_image_as_base64(image_path)

# Sidebar navigation
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

# Navigation buttons
selected_page = st.sidebar.radio("Select a Page", ("Dashboard", "Chatbot"))

# If the user selects "Dashboard"
if selected_page == "Dashboard":
    st.title("Hospital Analytics Dashboard")
    
    # Power BI Dashboard Embed
    dashboard_url = "https://app.powerbi.com/view?r=eyJrIjoiYzQyYjEwZTctNGQ3Yi00ZGMxLTgzODMtZDZlYzU4Yzk0Y2IzIiwidCI6IjQyY2VjMjM1LTc4MTUtNDNhYy1iNjdiLTAxNTFkYmZkZmQ4ZiJ9"
    st.markdown(f"""
        <iframe title="Power BI Dashboard" width="100%" height="600px" src="{dashboard_url}" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)

# If the user selects "Chatbot"
elif selected_page == "Chatbot":
    st.title("Hospital Analytics Chatbot")

    # Sidebar file uploader
    with st.sidebar:
        st.header("File Upload")
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    # Initialize session state
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'last_question' not in st.session_state:
        st.session_state.last_question = None
    if 'df' not in st.session_state:
        st.session_state.df = None

    if not st.session_state.chat_open:
        if uploaded_file:
            file_path = os.path.join("uploaded_files", uploaded_file.name)
            os.makedirs("uploaded_files", exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                # Validate and preprocess the file
                try:
                    df = pd.read_csv(file_path, encoding='utf-8', sep=',')
                    if df.empty:
                        st.error("The uploaded CSV file is empty. Please provide a valid file.")
                        st.stop()
                    df = df.drop_duplicates().fillna("Missing")  # Clean data
                    st.session_state.df = df
                    
                except pd.errors.ParserError:
                    st.error("There was an error parsing the CSV file. Please check the file format.")
                    st.stop()
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.stop()

                # Upload file to Gemini
                files = [genai.upload_file(file_path, mime_type="text/csv")]
                for file in files:
                    while file.state.name == "PROCESSING":
                        time.sleep(10)
                        file = genai.get_file(file.name)
                    if file.state.name != "ACTIVE":
                        raise Exception(f"File {file.name} failed to process")

                st.success("File uploaded and processed successfully!")

                # Updated prompt template with strict constraints
                prompt_template = """
                You are a highly accurate data analysis assistant with expertise in processing CSV files. Follow these principles strictly:

                1. *Data Integrity*: Base all calculations and interpretations strictly on the uploaded CSV data. Ensure all numbers match the raw data and flag discrepancies with detailed explanations.
                2. *Step-by-Step Calculations*: Provide precise calculations like sum, average, maximum, minimum, and percentages. Include a breakdown of the steps, showing intermediate results clearly.
                3. *Validation*: Cross-check all calculated results with the raw data to ensure consistency. If discrepancies are found, provide an explanation and resolution.
                4. *Contextual Responses*:
                - Focus only on the data relevant to the user's question.
                - Exclude unrelated columns or rows unless explicitly requested.
                - Ensure summaries and tables are concise and well-organized.
                5. *Error Reporting*:
                - If required data is missing or improperly formatted, clearly state the issue and suggest corrective actions.
                - Do not generate speculative or unsupported content.
                6. *Output Format*:
                - Provide results in tables wherever appropriate.
                - Include detailed calculation steps and clarification notes below the results.

                Context: {context}

                Question: {question}

                Response:
                """
                chat_session = genai.GenerativeModel(
                    model_name="gemini-2.0-flash-exp", 
                    generation_config={"temperature": 0.2, "max_output_tokens": 1000}
                ).start_chat(
                    history=[
                        {
                            "role": "user",
                            "parts": [
                                files[0],
                                prompt_template.format(
                                    context="Uploaded CSV data has been processed.",
                                    question="Analyze and describe the content of the file."
                                ),
                            ],
                        },
                        {
                            "role": "model",
                            "parts": ["File analysis complete. Ask me any question about the file!"]
                        },
                    ]
                )
                

                if st.button("Open Chatbot"):
                    st.session_state.chat_open = True
                    st.session_state.chat_session = chat_session
                    st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

    else:
        # Display chat history
        for chat in st.session_state.chat_history:
            st.chat_message("user").write(chat["question"])
            st.chat_message("assistant").write(chat["answer"])

        # Input box for user question
        user_input = st.chat_input("Your Question:")
        if user_input and user_input != st.session_state.last_question:
            st.chat_message("user").write(user_input)
            st.session_state.last_question = user_input
            st.session_state.chat_history.append({"role": "user", "question": user_input})

            with st.spinner("Generating answer..."):
                try:
                    prompt_template = """
                    You are a highly accurate data analysis assistant with expertise in processing CSV files. Follow these principles strictly:

                    1. *Data Integrity*: Base all calculations and interpretations strictly on the uploaded CSV data. Ensure all numbers match the raw data and flag discrepancies with detailed explanations.
                    2. *Step-by-Step Calculations*: Provide precise calculations like sum, average, maximum, minimum, and percentages. Include a breakdown of the steps, showing intermediate results clearly.
                    3. *Validation*: Cross-check all calculated results with the raw data to ensure consistency. If discrepancies are found, provide an explanation and resolution.
                    4. *Contextual Responses*:
                    - Focus only on the data relevant to the user's question.
                    - Exclude unrelated columns or rows unless explicitly requested.
                    - Ensure summaries and tables are concise and well-organized.
                    5. *Error Reporting*:
                    - If required data is missing or improperly formatted, clearly state the issue and suggest corrective actions.
                    - Do not generate speculative or unsupported content.
                    6. *Output Format*:
                    - Provide results in tables wherever appropriate.
                    - Include detailed calculation steps and clarification notes below the results.

                    Context: {context}

                    Question: {question}

                    Response:
                    """
                    full_prompt = prompt_template.format(
                        context="Uploaded CSV data has been processed.",
                        question=user_input
                    )
                    response = st.session_state.chat_session.send_message(full_prompt)
                    clean_response = response.text.strip()
                    st.chat_message("assistant").markdown(clean_response)
                    st.session_state.chat_history[-1]["answer"] = clean_response
                except Exception as e:
                    st.error(f"Error generating response: {e}")
