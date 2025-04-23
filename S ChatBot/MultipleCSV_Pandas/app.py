import os
import base64
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import API_Keys as apik

# Set Google API Key
os.environ["GOOGLE_API_KEY"] = apik.GOOGLE_API_KEY

# Function to convert an image to Base64
def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# Load datasets
dataset_paths = {
    "admission": r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\Dataset\Admission.csv",
    "appointment": r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\Dataset\Appointment.csv",
    "beds": r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\Dataset\Beds.csv",
    "bills": r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\Dataset\Bills.csv",
    "patients": r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\Dataset\Patients.csv",
    "rooms": r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\Dataset\Rooms.csv",
    "doctor": r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\Dataset\Doctor.csv"
}

dataframes = {name: pd.read_csv(path) for name, path in dataset_paths.items()}

# Initialize AI Model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

# Create an agent for each DataFrame

agents = {
    name: create_pandas_dataframe_agent(
        llm=llm, 
        df=df, 
        verbose=True, 
        allow_dangerous_code=True  # Explicitly allow execution
    )
    for name, df in dataframes.items()
}
# Function to identify the best dataset for a given question
def select_agent(question):
    keywords = {
        "admission": ["admit", "discharge", "hospitalized"],
        "appointment": ["appointment", "schedule", "consultation"],
        "beds": ["bed availability", "ICU", "ward"],
        "bills": ["billing", "invoice", "payment"],
        "patients": ["patient details", "history", "records"],
        "rooms": ["room", "accommodation"],
        "doctor": ["doctor", "physician", "surgeon"]
    }
    for dataset, keys in keywords.items():
        if any(key in question.lower() for key in keys):
            return agents[dataset]
    return None  # If no match, fallback to general response

# Function to query AI Agent
def ask_question(question):
    try:
        agent = select_agent(question)
        if agent:
            response = agent.invoke({"input": question})
            return response if isinstance(response, str) else response.get("output", "⚠️ No relevant data found.")
        else:
            return "⚠️ Unable to find relevant data. Try refining your question."
    except Exception as e:
        return f"⚠️ Error: {e}"

# Define a better response formatting prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a hospital analytics assistant. Provide responses in a structured format."),
    ("user", "For the question: '{question}', follow these formatting rules:\n\n"
             "- **If the response contains tabular data**, format it using markdown tables (`| Column | Column | Column |`).\n"
             "- **If the response does not require a table**, provide a clear and concise textual answer.\n"
             "- **Example Table Format:**\n"
             "  ```\n"
             "  | Column1 | Column2 | Column3 |\n"
             "  |---------|---------|---------|\n"
             "  | Value1  | Value2  | Value3  |\n"
             "  | ValueA  | ValueB  | ValueC  |\n"
             "  ```\n"
             "- If the response contains **numerical or structured data**, it should be formatted as a table.\n"
             "- If the response is **explanatory**, return a well-structured paragraph.\n\n"
             "Response:\n{ans}")
])

output_parser = StrOutputParser()
chain = prompt | llm | output_parser






# database app.py

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
                    print("chain invoke", response)
                except Exception as e:
                    st.warning("Plz Ask Question relate to Hospital Dataset...")

                    try:
                        response = dbh.l2_chain.invoke({"question": user_input})  # Use fallback model
                    except Exception as e2:
                        st.error(f"❌ Backup model also failed: {e2}. Please try again later 🙏.")
                        response = "I'm sorry, but I couldn't generate an answer at this time."

                st.chat_message("assistant").markdown(response)
                st.session_state.chat_history[-1]["answer"] = response



#database new_app.py

import os
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import re
import base64
import API_Keys as apik
from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM


# Set your Google API Key (replace with your actual key)
os.environ["GOOGLE_API_KEY"] = apik.GOOGLE_API_KEY

# Function to convert a local image to Base64 string
def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# logo_image path
logo_image_path = r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\AiSPRY logo.jpg"
# Power BI Dashboard Embed
dashboard_url = "https://app.powerbi.com/view?r=eyJrIjoiYzQyYjEwZTctNGQ3Yi00ZGMxLTgzODMtZDZlYzU4Yzk0Y2IzIiwidCI6IjQyY2VjMjM1LTc4MTUtNDNhYy1iNjdiLTAxNTFkYmZkZmQ4ZiJ9"


load_dotenv()
# Set your Google API Key (replace with your actual key)
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"] = apik.LANGCHAIN_API_KEY
os.environ["GOOGLE_API_KEY"] = apik.GOOGLE_API_KEY


# db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=1,include_tables=['customers','orders'],custom_table_info={'customers':"customer"})
def db_connect(user,password,host,name):
    db = SQLDatabase.from_uri(f"mysql+pymysql://{str(user)}:{str(password)}@{str(host)}/{str(name)}")
    return db

## Prompt Template

prompt=ChatPromptTemplate.from_messages(
    [
            ("system", "You are a SQL expert. Generate an accurate SQL query based on the user's question."
                       "Do NOT add a LIMIT clause unless the user explicitly asks for it."),
            ("user", "Question: {question}")
    ]
)
##
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
#llm2 = Ollama(model="deepseek-r1:1.5b") 
# llm2 = OllamaLLM(model="deepseek-r1:1.5b")

output_parser=StrOutputParser()
l2_chain=prompt|llm|output_parser

# SQL Query Generater Chain
def get_sql_query(db):
    generate_query = create_sql_query_chain(llm, db)
    return generate_query

# SQL query executer
def exe_query(db):
    execute_query = QuerySQLDataBaseTool(db=db)
    print(execute_query)
    return execute_query

# Function to clean SQL query
def clean_query(query):
    # Regular expression to extract SQL query and stop before 
    sql_query = query.replace("```mysql", "").strip().replace("```","").strip().replace("sql", "").strip()   
    return sql_query

# Define the answer prompt template

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    If SQL result is not empty, ensure that all columns and rows are fully displayed in table format.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
)


# Pipeline modification
rephrase_answer = answer_prompt | llm | StrOutputParser()
def answer_chain(generate_query, execute_query):
    chain = (
            RunnablePassthrough.assign(query=generate_query)  # Generates SQL query
            .assign(cleaned_query=itemgetter("query") | RunnableLambda(clean_query))  # Cleans query
            .assign(result=itemgetter("cleaned_query") | execute_query)  # Executes query
            | rephrase_answer  # Rephrases the answer
    )
    print("chain", chain)
    return chain

# Invoke chain
#if _name_ == "_main_":
#    ques = input("Enter your question: ")
#     print(chain.invoke({"question": ques}))
#chain.invoke({"question": "How many patients spent an amount of more than 70000?"})

