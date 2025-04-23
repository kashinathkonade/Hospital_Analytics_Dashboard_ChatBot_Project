import os
import base64
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType

# Set Google API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAUCWJBXyHatp39iRZqMTGofQ913Cep160"

# Function to convert an image to Base64
def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# Function to save uploaded files and return file paths
def save_uploaded_files(uploaded_files):
    file_paths = []
    os.makedirs("temp", exist_ok=True)  # Create temp directory if not exists

    for file in uploaded_files:
        temp_path = os.path.join("temp", file.name)
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        file_paths.append(temp_path)

    return file_paths

# Function to initialize agents for multiple CSVs
def initialize_agents(uploaded_files):
    file_paths = save_uploaded_files(uploaded_files)
    agents = {}

    for file_path in file_paths:
        agent = initialize_agent(file_path)
        if agent:
            agents[file_path] = agent

    return agents

# Function to initialize a single agent
def initialize_agent(csv_file_path):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", max_tokens=None)
        agent = create_csv_agent(
            llm=llm,
            path=csv_file_path,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            allow_dangerous_code=True,
        )
        return agent
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return None

# Function to ask a question across multiple datasets
def ask_question_multiple(agents, question):
    responses = []

    for file_path, agent in agents.items():
        try:
            response = agent.invoke({"input": question})["output"]
            responses.append(f"**File:** `{os.path.basename(file_path)}`\n{response}\n")
        except Exception as e:
            responses.append(f"**File:** `{os.path.basename(file_path)}`\nError: {e}\n")

    return "\n---\n".join(responses) if responses else "No response generated."
