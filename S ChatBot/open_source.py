import os
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import re
import API_Keys as apik

load_dotenv()
# Set your Google API Key (replace with your actual key)
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"] = apik.LANGCHAIN_API_KEY
os.environ["GOOGLE_API_KEY"] = apik.GOOGLE_API_KEY

db_user = "root"
db_password = apik.db_password
db_host = "localhost"
db_name = "bot_app"

# db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=1,include_tables=['customers','orders'],custom_table_info={'customers':"customer"})
db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
# SQL Query Generater Chain
generate_query = create_sql_query_chain(llm, db)
# SQL query executer
execute_query = QuerySQLDataBaseTool(db=db)

# Function to clean SQL query
def clean_query(query):
    # Regular expression to extract SQL query and stop before ```
    pattern = r"SELECT\s[\s\S]*?(?=```)"  # Stops before ending triple backticks

    # Find the SQL query
    match = re.search(pattern, query, re.DOTALL)
    sql_query = match.group(0).strip() if match else None  # Extract match and strip spaces
    return sql_query

# Define the answer prompt template
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
)

# Pipeline modification
rephrase_answer = answer_prompt | llm | StrOutputParser()

chain = (
    RunnablePassthrough.assign(query=generate_query)  # Generates SQL query
    .assign(cleaned_query=itemgetter("query") | RunnableLambda(clean_query))  # Cleans query
    .assign(result=itemgetter("cleaned_query") | execute_query)  # Executes query
    | rephrase_answer  # Rephrases the answer
)

# Invoke chain
if __name__ == "__main__":
    ques = input("Enter your question: ")
    print(chain.invoke({"question": ques}))
#chain.invoke({"question": "How many patients spent an amount of more than 70000?"})


