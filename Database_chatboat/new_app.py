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

# Set your Google API Key (replace with your actual key)rshmexzzz
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
        ("system","You are a helpful assistant. Please response to the user queries, ans should be short and concise."),
        ("user","Question:{question}")
    ]
)
##

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
llm2 = Ollama(model="deepseek-r1:1.5b")
output_parser=StrOutputParser()
l2_chain=prompt|llm|output_parser

# SQL Query Generater Chain
def get_sql_query(db):
    generate_query = create_sql_query_chain(llm, db)
    return generate_query

# SQL query executer
def exe_query(db):
    execute_query = QuerySQLDataBaseTool(db=db)
    return execute_query

# Function to clean SQL query
def clean_query(query):
    # Regular expression to extract SQL query and stop before 
    sql_query = query.replace("```mysql", "").strip().replace("```","").strip().replace("sql", "").strip()   
    return sql_query

# Define the answer prompt template
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    if sql result is not empty, then answer should be in table format.
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
    return chain

# Invoke chain
#if _name_ == "_main_":
#    ques = input("Enter your question: ")
#     print(chain.invoke({"question": ques}))
#chain.invoke({"question": "How many patients spent an amount of more than 70000?"})


# Tryed code 
import os
import base64
import re
import pandas as pd
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from sqlalchemy.exc import SQLAlchemyError
import API_Keys as apik

# Load API keys
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = apik.LANGCHAIN_API_KEY
os.environ["GOOGLE_API_KEY"] = apik.GOOGLE_API_KEY

# Initialize LLM Models
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
output_parser = StrOutputParser()

# Convert Image to Base64
def get_image_as_base64(file_path):
    """Converts an image file to Base64 format."""
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# Logo Image Path
logo_image_path = r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\AiSPRY logo.jpg"

# Power BI Dashboard Embed
dashboard_url = "https://app.powerbi.com/view?r=eyJrIjoiYzQyYjEwZTctNGQ3Yi00ZGMxLTgzODMtZDZlYzU4Yzk0Y2IzIiwidCI6IjQyY2VjMjM1LTc4MTUtNDNhYy1iNjdiLTAxNTFkYmZkZmQ4ZiJ9"

# Database Connection
def db_connect(user, password, host, name):
    """Establishes connection to the MySQL database."""
    db = SQLDatabase.from_uri(f"mysql+pymysql://{user}:{password}@{host}/{name}")
    return db

# ✅ Improved: Generate SQL Query **Using Real Schema**
def get_sql_query(db):
    """Generates an SQL query ensuring no incorrect table names are used."""
    
    # Get actual table names from the database
    table_names = db.get_usable_table_names()

    # Get column names for each table
    table_info = {}
    for table in table_names:
        try:
            columns = db.get_table_info(table)
            table_info[table] = columns
        except Exception:
            table_info[table] = "Unknown columns"

    # Construct schema string
    schema_info = "\n".join([f"{table}: {table_info[table]}" for table in table_names])

    custom_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"You are an SQL expert. Generate an SQL query using ONLY the correct table and column names."
                       f"Here is the schema of the database:\n{schema_info}\n"
                       f"Do NOT use non-existent table names. Stick to the schema."),
            ("user", "Question: {question}")
        ]
    )
    
    generate_query = custom_prompt | llm | StrOutputParser()
    return generate_query

# ✅ Improved: SQL Query Execution **Checks for Invalid Tables**
def exe_query(db):
    """Executes SQL queries and ensures the query uses valid tables."""
    
    def safe_execute(query):
        try:
            # Get actual table names
            table_names = db.get_usable_table_names()
            
            # Extract table name from query
            match = re.search(r'FROM\s+`?(\w+)`?', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                if table_name not in table_names:
                    return f"⚠️ Error: The table `{table_name}` does not exist in the database. Available tables: {table_names}"
            
            # Execute the query safely
            result = db.run(query)
            return result
        except SQLAlchemyError as e:
            return f"⚠️ SQL Execution Error: {str(e)}"
        except Exception as e:
            return f"⚠️ Unexpected Error: {str(e)}"

    return safe_execute

# ✅ Improved: **Remove any `LIMIT` from Queries**
def clean_query(query):
    """Removes `LIMIT` from SQL queries if it's not explicitly required."""
    query = query.replace("```mysql", "").strip().replace("```", "").strip().replace("sql", "").strip()
    
    # Remove any existing LIMIT clause
    query = re.sub(r"\s+LIMIT\s+\d+", "", query, flags=re.IGNORECASE)
    
    return query

# ✅ Improved: Better Answer Formatting Template
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    If SQL result is not empty, ensure that all columns and rows are fully displayed in table format.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
)

# Ensure complete result display
rephrase_answer = answer_prompt | llm | StrOutputParser()

# ✅ Improved: **Better Answer Pipeline**
def answer_chain(generate_query, execute_query):
    """Pipeline for answering user queries and ensuring full result visibility."""
    chain = (
        RunnablePassthrough.assign(query=generate_query)  # Generates SQL query
        .assign(cleaned_query=itemgetter("query") | RunnableLambda(clean_query))  # Cleans query
        .assign(result=itemgetter("cleaned_query") | RunnableLambda(execute_query))  # Executes query safely ✅ FIXED
        .assign(
            formatted_result=itemgetter("result") | RunnableLambda(handle_errors)  # Handles SQL errors
        )
        | rephrase_answer  # Rephrases and formats the answer
    )
    return chain

# ✅ Improved: **Better Error Handling**
def handle_errors(result):
    """Checks for errors in the SQL result and returns a safe response."""
    if isinstance(result, str) and result.startswith("⚠️"):
        return result  # Return the error message directly
    if not result:
        return "⚠️ No data found for this query."
    return format_sql_result(result)  # Convert results to a displayable format

# ✅ Improved: **Formats SQL Results as a Markdown Table**
def format_sql_result(result):
    """Formats SQL result as a Pandas DataFrame for proper UI rendering."""
    if isinstance(result, list) and result:  # If the result is a list of tuples
        df = pd.DataFrame(result)
        return df.to_markdown()  # Converts the DataFrame to a markdown table
    elif isinstance(result, str):  # If the result is already a string
        return result
    return "No data available."

