import os
import base64
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import API_Keys as apik


# Set your Google API Key (replace with your actual key)
os.environ["GOOGLE_API_KEY"] = apik.GOOGLE_API_KEY

# Function to convert a local image to Base64 string
def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# logo_image path
logo_image_path = r"C:\Users\triku\OneDrive\Desktop\Hospital Module Analysis\ChatBot\aispry_logo.png"
# Power BI Dashboard Embed
dashboard_url = "https://app.powerbi.com/view?r=eyJrIjoiYzQyYjEwZTctNGQ3Yi00ZGMxLTgzODMtZDZlYzU4Yzk0Y2IzIiwidCI6IjQyY2VjMjM1LTc4MTUtNDNhYy1iNjdiLTAxNTFkYmZkZmQ4ZiJ9"

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
            verbose=True,
            allow_dangerous_code=True,
        )
        return agent
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return None

def geting_file_path(file):
    # Define a temporary file path to save the uploaded file
    temp_file_path = os.path.join("temp", file.name)
    os.makedirs("temp", exist_ok=True)  # Create 'temp' directory if it doesn't exist

    # Save the uploaded file to the temporary file path
    with open(temp_file_path, "wb") as f:
        f.write(file.getbuffer())
    return temp_file_path

# Function to ask a question to the agent
def ask_question(agent, question):
    try:
        response = agent.invoke({"input": question})
        return response["output"]
    except Exception as e:
        print(f"Error getting response: {e}")
        return None


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Provide concise and clear responses to user queries."),
        ("user",
         """My answer is {ans} for this question: {question}. 
         Please provide the output in a **table format** or a **sentence format**, ensuring the answer is short and easy to understand."""
        )
    ]
)

# gemini LLm
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

output_parser = StrOutputParser()
chain = prompt|llm|output_parser
