import streamlit as st
from streamlit_chat import message
import tempfile
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import CTransformers
from langchain.chains import ConversationalRetrievalChain
from huggingface_hub import login
from transformers import GPT2Tokenizer

# Authenticate with Hugging Face
login(token="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")  # Replace with your Hugging Face token

DB_FAISS_PATH = 'vectorstore/db_faiss'

# Initialize tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")  # Adjust based on your model

# Function to truncate text to fit within max token limit
def truncate_text(text, max_length):
    tokens = tokenizer.encode(text)
    if len(tokens) > max_length:
        tokens = tokens[:max_length]
    return tokenizer.decode(tokens)

# Function to load the LLM
def load_llm():
    try:
        llm = CTransformers(
            model=r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\llama-2-7b-chat.ggmlv3.q8_0.bin",  # Update with your local path to the model
            model_type="llama",
            max_new_tokens=512,
            temperature=0.5
        )
        return llm
    except Exception as e:
        st.error(f"Error loading LLM: {e}")
        return None

# Streamlit application setup
st.title("Chat with CSV using LLaMA2 🤙")

uploaded_file = st.sidebar.file_uploader("Upload your Data", type="csv")

if uploaded_file:
    try:
        # Use tempfile because CSVLoader only accepts a file path
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        # Load the CSV data
        loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8", csv_args={'delimiter': ','})
        data = loader.load()

        # Initialize embeddings and FAISS vector store
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                           model_kwargs={'device': 'cpu'})

        db = FAISS.from_documents(data, embeddings)
        db.save_local(DB_FAISS_PATH)

        # Load the LLM
        llm = load_llm()
        if not llm:
            st.stop()

        # Set up conversational retrieval chain
        chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever())

        # Function for conversational chat
        def conversational_chat(query):
            # Truncate query to fit within context limit
            query = truncate_text(query, 512 - 100)  # Reserving space for context
            try:
                result = chain({"question": query, "chat_history": st.session_state['history']})
                st.session_state['history'].append((query, result["answer"]))
                return result["answer"]
            except Exception as e:
                st.error(f"Error during chat: {e}")
                return "Error occurred, please try again."

        # Initialize session states
        if 'history' not in st.session_state:
            st.session_state['history'] = []

        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["Hello! Ask me anything about " + uploaded_file.name + " 🤗"]

        if 'past' not in st.session_state:
            st.session_state['past'] = ["Hey! 👋"]

        # Container for chat history
        response_container = st.container()
        # Container for user input
        container = st.container()

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input("Query:", placeholder="Talk to your CSV data here (:", key='input')
                submit_button = st.form_submit_button(label='Send')

            if submit_button and user_input:
                output = conversational_chat(user_input)

                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

        # Display chat history
        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                    message(st.session_state['generated'][i], key=str(i), avatar_style="thumbs")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        # Cleanup temporary file
        if 'tmp_file_path' in locals() and tmp_file_path:
            try:
                import os
                os.remove(tmp_file_path)
            except Exception as e:
                st.warning(f"Could not delete temporary file: {e}")
else:
    st.info("Upload a CSV file to get started!")











import os
import base64

# Set your Google API Key (replace with your actual key)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAUCWJBXyHatp39iRZqMTGofQ913Cep160"

from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType

# Function to convert a local image to Base64 string
def get_image_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

# logo_image path
logo_image_path = r"C:\Users\kashinath konade\Downloads\Hospital Analytics Project\AiSPRY logo.jpg"
# Power BI Dashboard Embed
dashboard_url = "https://app.powerbi.com/view?r=eyJrIjoiYzQyYjEwZTctNGQ3Yi00ZGMxLTgzODMtZDZlYzU4Yzk0Y2IzIiwidCI6IjQyY2VjMjM1LTc4MTUtNDNhYy1iNjdiLTAxNTFkYmZkZmQ4ZiJ9"

# Function to initialize the agent
def initialize_agent(csv_file_path):
    try:
        # Initialize the Google Generative AI model with tuned parameters
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            max_tokens=2000,  # Allow detailed and long outputs
            temperature=0.7,  # Adjust creativity (higher value = more creative)
        )
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
        print(f"Error initializing agent: {e}")
        return None

# Function to handle file path for uploaded files
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
        # Modify the input question to request detailed answers explicitly
        detailed_question = f"Please provide a detailed and comprehensive answer: {question}"

        # Get response from the agent
        response = agent.invoke({"input": detailed_question})
        return response["output"]
    except Exception as e:
        print(f"Error getting response: {e}")
        return None




    
