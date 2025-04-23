import streamlit as st
import os
import time
import pandas as pd
import re
import new_app as dbh
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
image_base64 = dbh.get_image_as_base64(dbh.logo_image_path)

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
if st.sidebar.button("Dashboard 🖥"):
    st.session_state.selected_page = "Dashboard"
if st.sidebar.button("Chatbot 💬"):
    st.session_state.selected_page = "Chatbot"

# Main page content
if st.session_state.selected_page == "Welcome":
    st.title("🎉 Welcome to HealthCare Analytics 🎉")
    st.write("Navigate to the *Dashboard* 🖥 or *Chatbot* 💬 using the sidebar.")
elif st.session_state.selected_page == "Dashboard":
    st.title("Hospital Analytics Dashboard")

    st.markdown(f"""
        <iframe title="Power BI Dashboard" width="100%" height="600px" src="{dbh.dashboard_url}" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)

elif st.session_state.selected_page == "Chatbot":
    st.title("💬 Hospital Analytics Chatbot")

    # Initialize session state variables
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'last_question' not in st.session_state:
        st.session_state.last_question = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'db' not in st.session_state:  # Initialize db to avoid NameError
        st.session_state.db = None
    if 'db_connected' not in st.session_state:  # Track connection status
        st.session_state.db_connected = False

    # Sidebar for Database Connection
    with st.sidebar:
        st.header("Database Connection")

        # User inputs for DB credentials
        db_user = st.text_input("👨🏻‍💻 Enter your database user:")
        db_password = st.text_input("🔑 Enter your database password:", type="password")
        db_host = st.text_input("🌐 Enter your database host:")
        db_name = st.text_input("⛃ Enter your database name:")

        # Button to connect to the database
        if st.button("Connect to Database ⚡"):
            db = dbh.db_connect(db_user, db_password, db_host, db_name)
            if db:
                st.success("✅ Connection successful!")
                st.session_state.chat_open = True  # Open chat if connection is successful
                st.session_state.db = db  # Store DB connection in session state
                st.session_state.db_connected = True  # Mark connection as successful
            else:
                st.error("❌ Failed to connect to the database. Please check your credentials.")
                st.session_state.db_connected = False  # Connection failed

    # Check if the database connection is available
    if st.session_state.db is None:
        st.warning("No database connection")
    elif st.session_state.db_connected:
        st.write("💡 Available Tables:")
        st.write(st.session_state.db.get_usable_table_names())
        # Assuming dbh.get_sql_query uses the db object for getting queries
        get_query = dbh.get_sql_query(st.session_state.db)
        exe_query = dbh.exe_query(st.session_state.db)
        chain = dbh.answer_chain(get_query, exe_query)

        # Display chat history
        for chat in st.session_state.chat_history:
            st.chat_message("user").write(chat["question"])
            st.chat_message("assistant").write(chat["answer"])

        # Input box for user question
        user_input = st.chat_input("🤔 Your Question:")
        if user_input and user_input != st.session_state.last_question:
            st.chat_message("user").write(user_input)
            st.session_state.last_question = user_input
            st.session_state.chat_history.append({"role": "user", "question": user_input})

            with st.spinner("💡 Generating answer..."):
                try:
                    response = chain.invoke({"question": user_input})
                except Exception as e:
                    st.warning("Plz Ask Question relate to Hospital Dataset...")

                    try:
                        response = dbh.l2_chain.invoke({"question": user_input})  # Use fallback model
                    except Exception as e2:
                        st.error(f"❌ Backup model also failed: {e2}. Please try again later 🙏.")
                        response = "I'm sorry, but I couldn't generate an answer at this time."

                st.chat_message("assistant").markdown(response)
                st.session_state.chat_history[-1]["answer"] = response

