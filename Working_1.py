#original 
import os
import pandas as pd
import streamlit as st
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType

# Set Streamlit page configuration
st.set_page_config(page_title="CSV Data Analytics", layout="wide")

# Set Google API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAUCWJBXyHatp39iRZqMTGofQ913Cep160"

# Function to merge multiple CSV files intelligently
def merge_csv_files(uploaded_files):
    try:
        # Read all CSV files
        dataframes = {file.name: pd.read_csv(file) for file in uploaded_files}

        # Find common columns between CSVs
        common_keys = set.intersection(*(set(df.columns) for df in dataframes.values()))

        if common_keys:
            # Merge using the first common key
            merge_column = list(common_keys)[0]
            merged_df = None

            for file_name, df in dataframes.items():
                if merged_df is None:
                    merged_df = df  # Start with the first file
                else:
                    merged_df = pd.merge(merged_df, df, on=merge_column, how="outer")  # Merge step by step
        else:
            # If no common column, merge intelligently in steps
            merged_df = None
            while dataframes:
                # Pick any dataframe to start
                file_name, df = dataframes.popitem()

                if merged_df is None:
                    merged_df = df
                else:
                    # Find common columns with the current merged dataframe
                    merge_keys = set(merged_df.columns) & set(df.columns)

                    if merge_keys:
                        common_key = list(merge_keys)[0]  # Use any common key found
                        merged_df = pd.merge(merged_df, df, on=common_key, how="outer")
                    else:
                        # If no common key, just concatenate as last option
                        merged_df = pd.concat([merged_df, df], axis=1, ignore_index=False, sort=False)

        # Replace NaN values with meaningful defaults
        for col in merged_df.columns:
            if merged_df[col].dtype == "object":
                merged_df[col].fillna("Unknown", inplace=True)
            else:
                merged_df[col].fillna(0, inplace=True)

        # Save merged dataset
        merged_csv_path = "merged_dataset.csv"
        merged_df.to_csv(merged_csv_path, index=False)

        return merged_csv_path, merged_df
    except Exception as e:
        st.error(f"Error merging CSV files: {e}")
        return None, None

# Function to initialize the AI agent
def initialize_agent(csv_file_path):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", max_tokens=None)
        agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION

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

# Sidebar Navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Dashboard 🖥"):
    st.session_state.selected_page = "Dashboard"
if st.sidebar.button("Chatbot 💬"):
    st.session_state.selected_page = "Chatbot"

# Main Page Content
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Welcome"

if st.session_state.selected_page == "Dashboard":
    st.title("📊 Power BI Dashboard")
    dashboard_url = "https://app.powerbi.com/view?r=eyJrIjoiYzQyYjEwZTctNGQ3Yi00ZGMxLTgzODMtZDZlYzU4Yzk0Y2IzIiwidCI6IjQyY2VjMjM1LTc4MTUtNDNhYy1iNjdiLTAxNTFkYmZkZmQ4ZiJ9"
    st.markdown(f"""
        <iframe title="Power BI Dashboard" width="100%" height="600px" src="{dashboard_url}" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)

elif st.session_state.selected_page == "Chatbot":
    st.title("💬 CSV Data Chatbot")

    # File Upload (Now in Chatbot Section)
    uploaded_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)

    if uploaded_files:
        st.session_state.csv_files = uploaded_files  # Store files in session state
        merged_csv_path, merged_df = merge_csv_files(uploaded_files)

        if merged_csv_path:
            st.success(f"✅ CSV files merged successfully!")
            st.session_state.csv_path = merged_csv_path  # Store path for chatbot use
            st.session_state.merged_df = merged_df  # Store DataFrame in session state

            # **Updated: Show Merged Data Preview with Fixed Alignment**
            st.write("📜 **Preview of Merged CSV Data (Aligned Correctly):**")
            st.dataframe(merged_df.head())

    else:
        st.warning("⚠️ Please upload at least one CSV file.")

    # Check if CSV file exists
    if "csv_path" not in st.session_state or not os.path.exists(st.session_state.csv_path):
        st.warning("⚠️ Please upload and merge CSV files first.")
    else:
        # Initialize AI Agent only once
        if "agent" not in st.session_state:
            with st.spinner("🚀 Initializing AI agent..."):
                st.session_state.agent = initialize_agent(st.session_state.csv_path)

        if "agent" in st.session_state and st.session_state.agent:
            st.success("🤖 AI Agent is ready! Ask a question below.")

            # Chat History
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # Display chat history
            for chat in st.session_state.chat_history:
                st.chat_message("user").write(chat["question"])
                st.chat_message("assistant").write(chat["answer"])

            # User Input for Questions
            user_input = st.chat_input("🤔 Your Question:")
            if user_input:
                st.chat_message("user").write(user_input)

                # Special handling for column name request
                if "columns" in user_input.lower():
                    column_names = list(st.session_state.merged_df.columns)
                    answer = ", ".join(column_names)
                else:
                    with st.spinner("💡 Generating answer..."):
                        try:
                            response = st.session_state.agent.invoke({"input": user_input})
                            answer = response.get("output", "No response received.")
                        except Exception as e:
                            answer = "⚠️ Error: Could not generate a response."

                st.chat_message("assistant").markdown(answer)

                # Store chat history
                st.session_state.chat_history.append({"question": user_input, "answer": answer})
