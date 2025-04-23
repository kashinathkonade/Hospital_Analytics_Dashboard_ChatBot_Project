import streamlit as st
import os
import time
import pandas as pd
import re
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

# Image file path for the sidebar logo
image_base64 = fun.get_image_as_base64(fun.logo_image_path)

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

# Initialize session state for page navigation
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Welcome"  # Default to Welcome page

# Sidebar navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Dashboard"):
    st.session_state.selected_page = "Dashboard"
if st.sidebar.button("Chatbot"):
    st.session_state.selected_page = "Chatbot"

# Main page content
if st.session_state.selected_page == "Welcome":
    st.title("Welcome to HealthCare Analytics")
    st.write("Navigate to the Dashboard or Chatbot using the sidebar.")
elif st.session_state.selected_page == "Dashboard":
    st.title("Hospital Analytics Dashboard")

    st.markdown(f"""
        <iframe title="Power BI Dashboard" width="100%" height="600px" src="{fun.dashboard_url}" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)

elif st.session_state.selected_page == "Chatbot":
    st.title("Hospital Analytics Chatbot")
    mai_placefolder = st.empty()

    # Sidebar file uploader
    with st.sidebar:
        st.header("File Upload")
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    # Initialize session state for Chatbot
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'last_question' not in st.session_state:
        st.session_state.last_question = None
    if 'df' not in st.session_state:
        st.session_state.df = None

    if uploaded_file is not None:
        # Define a temporary file path to save the uploaded file
        temp_file_path = fun.geting_file_path(uploaded_file)
        mai_placefolder.text("File uploaded successfully!.....✅✅")
        # Initialize the agent
        agent = fun.initialize_agent(temp_file_path)

        if agent:
            mai_placefolder.text("Agent initialized successfully!...✅✅")
            st.session_state.chat_open = True
        else:
            st.error("Failed to initialize the agent.")

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
            mai_placefolder.text("")
            with st.spinner("Generating answer..."):
                try:
                    response = fun.ask_question(agent, user_input)
                    final = fun.chain.invoke({"ans": response, "question": user_input})
                    st.chat_message("assistant").markdown(final)
                    st.session_state.chat_history[-1]["answer"] = final
                except Exception as e:
                    st.error(f"Error generating response: {e}")





