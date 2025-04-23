import streamlit as st
from streamlit_chat import message
import tempfile
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_community.llms import CTransformers
from langchain.chains import ConversationalRetrievalChain
from google.cloud import aiplatform
from transformers import GPT2Tokenizer

# Authenticate with Google Cloud
PROJECT_ID = "streamlitapp-448509"  # Replace with your GCP project ID
LOCATION = "asia-east1"  # Update based on your location
ENDPOINT_ID = "projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/<your-endpoint-id>"  # Replace with your endpoint ID

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
            model=r"C:\\Users\\kashinath konade\\Downloads\\Hospital Analytics Project\\llama-2-7b-chat.ggmlv3.q8_0.bin",  # Update with your local path to the model
            model_type="llama",
            max_new_tokens=512,
            temperature=0.5
        )
        return llm
    except Exception as e:
        st.error(f"Error loading LLM: {e}")
        return None

# Function to get Google Embeddings
def get_google_embeddings(texts):
    try:
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)
        
        instances = [{"content": text} for text in texts]
        response = endpoint.predict(instances=instances)
        
        embeddings = response.predictions
        return embeddings
    except Exception as e:
        st.error(f"Error generating embeddings: {e}")
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

        # Debugging: Check the structure of the loaded data
        st.write(data)  # This will help you understand the structure of each document

        # Assuming the documents have 'text' as part of the dictionary, adjust how you access it
        embeddings = get_google_embeddings([doc.get('text', '') for doc in data])  # Update this based on the actual structure

        if not embeddings:
            st.stop()

        db = FAISS.from_embeddings(data, embeddings)

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

# Set your Google API Key (replace with your actual key)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAUCWJBXyHatp39iRZqMTGofQ913Cep160"

from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType

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
        print(f"Error initializing agent: {e}")
        return None

# Function to ask a question to the agent
def ask_question(agent, question):
    try:
        response = agent.invoke({"input": question})
        return response["output"]
    except Exception as e:
        print(f"Error getting response: {e}")
        return None

# Main function
def main():
    # Step 1: Path to the CSV file
    csv_file_path = input("Enter the path to your CSV file: ")
    if not os.path.exists(csv_file_path):
        print("CSV file not found. Please check the path and try again.")
        return

    # Step 2: Initialize the agent
    agent = initialize_agent(csv_file_path)

    if not agent:
        print("Failed to initialize agent.")
        return

    print("Agent initialized successfully!")

    # Step 3: Ask questions about the CSV data
    while True:
        question = input("Ask a question about the CSV data (or type 'exit' to quit): ")
        if question.lower() == "exit":
            break

        response = ask_question(agent, question)
        if response:
            print("Response:")
            print(response)
        else:
            print("No response received.")

if __name__ == "__main__":
    main()
