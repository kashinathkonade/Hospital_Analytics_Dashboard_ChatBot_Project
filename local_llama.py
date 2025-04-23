import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

# Load environment variables
load_dotenv()

# Ensure LangChain API key is set (optional if not using LangSmith)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")  # Use from .env

# Define the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user queries."),
        ("user", "Question: {question}")
    ]
)

# Initialize Streamlit app
st.title("LangChain Demo with LLAMA2 API (DeepSeek-R1:1.5B)")

# User input field
input_text = st.text_input("Search the topic you want:")

# Initialize Ollama model
llm = Ollama(model="deepseek-r1:1.5b")

# Create output parser
output_parser = StrOutputParser()

# Define chain
chain = prompt | llm | output_parser

# If user provides input, process the request
if input_text:
    response = chain.invoke({"question": input_text})
    st.write(response)
