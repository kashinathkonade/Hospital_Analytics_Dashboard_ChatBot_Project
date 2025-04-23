import streamlit as st
import os
import pandas as pd
import chat_bot_fun as fun

# Set Streamlit page configuration
st.set_page_config(page_title="Hospital Analytics Project", layout="wide")

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

# Sidebar file uploader (Allow Multiple Files)
st.sidebar.header("File Upload")
uploaded_files = st.sidebar.file_uploader("Upload multiple CSV files", type=["csv"], accept_multiple_files=True)

# Initialize session state for chatbot
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_question' not in st.session_state:
    st.session_state.last_question = None
if 'agents' not in st.session_state:
    st.session_state.agents = {}

# Load multiple datasets
if uploaded_files:
    st.session_state.agents = fun.initialize_agents(uploaded_files)
    st.session_state.chat_open = True
    st.success("Files uploaded and agents initialized successfully! ✅")

# Chatbot UI
st.title("Hospital Analytics Chatbot")

# Display chat history
for chat in st.session_state.chat_history:
    st.chat_message("user").write(chat["question"])
    st.chat_message("assistant").write(chat["answer"])

# User input
user_input = st.chat_input("Your Question:")
if user_input and user_input != st.session_state.last_question:
    st.chat_message("user").write(user_input)
    st.session_state.last_question = user_input
    st.session_state.chat_history.append({"role": "user", "question": user_input})

    with st.spinner("Generating answer..."):
        try:
            response = fun.ask_question_multiple(st.session_state.agents, user_input)
            st.chat_message("assistant").markdown(response)
            st.session_state.chat_history[-1]["answer"] = response
        except Exception as e:
            st.error(f"Error generating response: {e}")
