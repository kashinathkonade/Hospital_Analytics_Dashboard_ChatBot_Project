import pandas as pd
import google.generativeai as genai


# Load CSV file into a DataFrame
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None


# Prepare the chatbot's responses
def create_chatbot_context(df):
    if df is None:
        return ""

    # Summarize the dataset for initial context
    context = """You are a chatbot with access to a CSV dataset. Use the data to answer questions accurately.\n\n"""

    # Include sample rows for the bot to understand structure
    sample_data = df.head(5).to_dict(orient="records")
    context += f"Here is the structure of the dataset with sample rows:\n{sample_data}\n\n"

    return context


# Initialize the chatbot using Google Generative AI
def chatbot_genai(user_input, context):
    genai.configure(api_key="AIzaSyBxCOi6uS0G1UKgq-aFgHE3umgrgCAA6Q8")  # Replace with your Generative AI API key

    try:
        response = genai.chat(  # Use chat for conversational interactions
            model="chat-bison-001",  # Use the appropriate GenAI chat model
            messages=[
                {"author": "system", "content": context},
                {"author": "user", "content": user_input},
            ],
        )

        return response.messages[-1]["content"] if response.messages else "No response from the model."
    except Exception as e:
        return f"Error during chat completion: {e}"


if __name__ == "__main__":
    # Path to the uploaded CSV file
    csv_file_path = r"C:\Users\triku\OneDrive\Desktop\Hospital Module Analysis\ChatBot\Test.csv"  # Replace with the correct path if needed

    # Load the dataset
    data = load_csv(csv_file_path)

    # Create the chatbot context
    context = create_chatbot_context(data)

    print("Chatbot is ready! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break

        # Get the response from the chatbot
        response = chatbot_genai(user_input, context)
        print(f"Chatbot: {response}")
