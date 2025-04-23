import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configure the Generative AI API
genai.configure(api_key="AIzaSyBxCOi6uS0G1UKgq-aFgHE3umgrgCAA6Q8")
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to load CSV file into a DataFrame
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return None

# Function to prepare chatbot context
def create_chatbot_context(df):
    if df is None:
        return ""

    # Summarize the dataset for initial context
    context = """You are a chatbot with access to a CSV dataset. Use the data to answer questions accurately.\n\n"""

    # Include sample rows for the bot to understand structure
    sample_data = df.head(100).to_dict(orient="records")
    context += f"Here is the structure of the dataset with sample rows:\n{sample_data}\n\n Output should be short and concise."

    return context

# Streamlit UI
def main():
    st.title("Chatbot For Hospital Module Analysis")
    st.sidebar.title("Upload Dataset")

    # File uploader
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    data = None
    context = ""

    if uploaded_file:
        # Load dataset
        data = load_csv(uploaded_file)
        if data is not None:
            st.sidebar.success("Dataset loaded successfully!")
            st.write("### Dataset Overview")
            st.dataframe(data.head(5))

            # Generate chatbot context
            context = create_chatbot_context(data)

    st.write("### Chat with the Bot")
    if data is not None:
        user_input = st.text_input("You: ", "")
        if user_input:
            try:
                response = model.generate_content(context + user_input)
                st.write(f"Chatbot: {response.text}")
            except Exception as e:
                st.error(f"Error generating response: {e}")
    else:
        st.info("Please upload a CSV file to start chatting.")

if __name__ == "__main__":
    main()




