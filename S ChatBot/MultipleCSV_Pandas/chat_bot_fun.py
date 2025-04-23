import streamlit as st
import app as fun

st.set_page_config(page_title="Hospital Analytics", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Welcome"

# Navigation Handling
if st.sidebar.button("Dashboard"):
    st.session_state.selected_page = "Dashboard"

if st.sidebar.button("Chatbot"):
    st.session_state.selected_page = "Chatbot"

# Power BI Dashboard URL (Fixed)
dashboard_url = "https://app.powerbi.com/view?r=eyJrIjoiYzQyYjEwZTctNGQ3Yi00ZGMxLTgzODMtZDZlYzU4Yzk0Y2IzIiwidCI6IjQyY2VjMjM1LTc4MTUtNDNhYy1iNjdiLTAxNTFkYmZkZmQ4ZiJ9"

# Page Handling   
if st.session_state.selected_page == "Welcome":
    st.title("Welcome to HealthCare Analytics")
    st.write("Navigate to the **Dashboard** or **Chatbot** using the sidebar.")

elif st.session_state.selected_page == "Dashboard":
    st.title("Hospital Analytics Dashboard")

    try:
        st.markdown(
            f'<iframe title="Power BI Dashboard" width="100%" height="600px" src="{dashboard_url}" frameborder="0" allowFullScreen="true"></iframe>',
            unsafe_allow_html=True
        )
        # Provide an external link to open in a new tab
        st.markdown(f"[🔗 Open Power BI Dashboard in New Tab]({dashboard_url})", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Error loading Power BI Dashboard: {e}")

elif st.session_state.selected_page == "Chatbot":
    st.title("Hospital Analytics Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("💬 Ask a question about hospital data:")

    if user_input:
        st.chat_message("user").write(user_input)

        with st.spinner("🔎 Fetching response..."):
            response = fun.ask_question(user_input)

            if response and isinstance(response, str):
                final_answer = fun.chain.invoke({"ans": response, "question": user_input})
            else:
                final_answer = "⚠️ AI could not generate an answer. Try rephrasing."

            st.session_state.chat_history.append({"question": user_input, "answer": final_answer})
            st.chat_message("assistant").markdown(final_answer)

    # Display Chat History
    for chat in st.session_state.chat_history:
        st.chat_message("user").write(chat["question"])
        st.chat_message("assistant").markdown(chat["answer"])
