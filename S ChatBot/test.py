import os
import streamlit as st
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType

# Set your Google API Key (replace with your actual key)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAUCWJBXyHatp39iRZqMTGofQ913Cep160"

# Function to initialize the agent
def initialize_agent(csv_file_path):
    try:
        # Initialize the Google Generative AI model
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", max_tokens=None)
        agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION

        # Create the CSV agent
        agent = create_csv_agent(
            llm=llm,
            path=csv_file_path,
            agent_type=agent_type,
            verbose=True,
            allow_dangerous_code=True,
        )
        return agent
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        return None

# Function to ask a question to the agent
def ask_question(agent, question):
    try:
        response = agent.invoke({"input": question})
        return response["output"]
    except Exception as e:
        print(f"Error getting response: {e}")
        return None

# Streamlit app
def main():
    st.title("CSV Data Q&A with LangChain and Google Generative AI")

    # Step 1: File uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        # Save uploaded file temporarily
        csv_file_path = f"temp_{uploaded_file.name}"
        with open(csv_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File uploaded and saved as {csv_file_path}")

        # Initialize the chat visibility state
        if "show_chat" not in st.session_state:
            st.session_state.show_chat = False

        # Button to open the chatbot
        if not st.session_state.show_chat:
            if st.button("Open Chatbot"):
                st.session_state.show_chat = True

        # Chat interface
        if st.session_state.show_chat:
            # Step 2: Initialize the agent
            agent = initialize_agent(csv_file_path)
            if agent:
                st.success("Agent initialized successfully!")
            else:
                st.error("Failed to initialize the agent.")
                return

            # Step 3: Chat interface
            if "messages" not in st.session_state:
                st.session_state.messages = []

            st.subheader("Chat with your CSV data")

            # Display chat messages
            for message in st.session_state.messages:
                if message["is_user"]:
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"])

            # User input
            user_input = st.chat_input("Ask a question about the CSV data")
            if user_input:
                # Add user message to session state
                st.session_state.messages.append({"content": user_input, "is_user": True})
                st.chat_message("user").write(user_input)

                # Get response from the agent
                response = ask_question(agent, user_input)
                if response:
                    st.session_state.messages.append({"content": response, "is_user": False})
                    st.chat_message("assistant").write(response)
                else:
                    st.error("No response received from the agent.")

if __name__ == "__main__":
    main()
