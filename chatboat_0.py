
import streamlit as st
import os
import time
import pandas as pd
import re
import google.generativeai as genai

# Set your API key (use environment variables in production)
API_KEY = "AIzaSyDd4OKiCLlGW716L-ezmgvP4DrnN3nEHc4"
genai.configure(api_key=API_KEY)

# Set Streamlit page configuration to wide mode
st.set_page_config(layout="wide")

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

# Hide Streamlit's sidebar navigation
st.markdown(
    """
    <style>
    div[data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to upload file to Gemini
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# Function to wait for file processing to complete
def wait_for_files_active(files):
    """Waits for the given files to be active."""
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")

# Model configuration
generation_config = {
    "temperature": 0.2,  # Reduced for more deterministic responses
    "max_output_tokens": 1000,  # Limit response length
}

# Initialize the generative model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

# Streamlit app
st.title("Hospital Analytics Chatbot")

# Sidebar with branding
with st.sidebar:
    st.image(r"K:\SLMG_Dataset\LLM\aispry.png", width=200)  # Replace with your logo file path
    st.header("File Upload")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    st.sidebar.markdown(
        """
        <div style='position: fixed; bottom: 0; left: 60px; font-size: 17px;'>
            <span style='color: gray;'>Powered by</span> 
            <a href='https://www.aispry.com' target='_blank' style='color: #b8860b; text-decoration: none; font-weight: bold;'>AiSPRY</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
                df = pd.read_csv(file_path, encoding='utf-8', sep=',')  # Explicitly set encoding and separator
                if df.empty:
                    st.error("The uploaded CSV file is empty. Please provide a valid file.")
                    st.stop()
                df = df.drop_duplicates().fillna("Missing")  # Clean data
                st.session_state.df = df  # Store DataFrame in session state
                st.write("CSV file successfully loaded.")
            except pd.errors.ParserError:
                st.error("There was an error parsing the CSV file. Please check the file format.")
                st.stop()
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.stop()

            # Upload file to Gemini
            files = [upload_to_gemini(file_path, mime_type="text/csv")]
            wait_for_files_active(files)
            st.success("File uploaded and processed successfully!")

            chat_session = model.start_chat(
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
                        "parts": [
                            "File analysis complete. Ask me any question about the file!",
                        ],
                    },
                ]
            )
            st.success("Chatbot ready!")

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
        # Display the user's question immediately
        st.chat_message("user").write(user_input)

        # Save the question as the last processed question
        st.session_state.last_question = user_input
        st.session_state.chat_history.append({"role": "user", "question": user_input})

        with st.spinner("Generating answer..."):
            try:
                # Generate prompt with context and question
                full_prompt = prompt_template.format(
                    context="Uploaded CSV data has been processed.",
                    question=user_input,
                )
                response = st.session_state.chat_session.send_message(full_prompt)

                # Extract and clean the response text
                clean_response = response.text.strip()

                # Detect and display table if included in the response
                if "Table:" in clean_response:
                    try:
                        table_start = clean_response.index("Table:") + len("Table:")
                        table_data = clean_response[table_start:].strip()

                        # Split rows and columns for tabular representation
                        rows = [row.split("\t") for row in table_data.split("\n") if row.strip()]
                        if rows:
                            headers = rows[0]
                            data = rows[1:]
                            df = pd.DataFrame(data, columns=headers)
                            st.dataframe(df)

                            # Show detailed calculation steps if provided
                            if "Steps:" in clean_response:
                                steps_start = clean_response.index("Steps:") + len("Steps:")
                                steps_text = clean_response[steps_start:].strip()
                                st.markdown(f"### Calculation Steps:\n{steps_text}")

                            # Validate consistency between calculation and table values
                            if "Validation:" in clean_response:
                                validation_start = clean_response.index("Validation:") + len("Validation:")
                                validation_text = clean_response[validation_start:].strip()
                                st.markdown(f"### Validation:\n{validation_text}")
                        else:
                            st.warning("No valid table rows found.")
                    except Exception as e:
                        st.error(f"Error parsing table data: {e}")
                else:
                    st.chat_message("assistant").markdown(clean_response)

                # Save the answer to the chat history
                st.session_state.chat_history[-1]["answer"] = clean_response

            except Exception as e:
                st.error(f"Error generating response: {e}")

with st.sidebar:
    if st.button("Logout", key="logout_button"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()

