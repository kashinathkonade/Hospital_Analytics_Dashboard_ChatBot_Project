import re
import mysql.connector
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

token = "7579669715:AAFi-3yxA532K6Yxg-ks2WWCasGKcW71Anw"


# MySQL database connection
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="",  # Replace with your MySQL password
        database="user_data"
    )

# Validation functions
def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Store data in MySQL
def store_data(first_name, last_name, phone, email):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO user_info (first_name, last_name, phone, email) VALUES (%s, %s, %s, %s)",
        (first_name, last_name, phone, email)
    )
    connection.commit()
    cursor.close()
    connection.close()

# Start the bot conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! Let's start your registration.")
    await update.message.reply_text("Please enter your First Name:")
    context.user_data['step'] = 'first_name'

# Handler for user input
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    step = context.user_data.get('step')

    if step == 'first_name':
        first_name = update.message.text
        if first_name.isalpha():
            context.user_data['first_name'] = first_name
            context.user_data['step'] = 'last_name'
            await update.message.reply_text("Please enter your Last Name:")
        else:
            await update.message.reply_text("First Name should only contain letters. Please try again.")

    elif step == 'last_name':
        last_name = update.message.text
        if last_name.isalpha():
            context.user_data['last_name'] = last_name
            context.user_data['step'] = 'phone'
            await update.message.reply_text("Please enter your Phone Number (10 digits):")
        else:
            await update.message.reply_text("Last Name should only contain letters. Please try again.")

    elif step == 'phone':
        phone = update.message.text
        if is_valid_phone(phone):
            context.user_data['phone'] = phone
            context.user_data['step'] = 'email'
            await update.message.reply_text("Please enter your Email (e.g., example@domain.com):")
        else:
            await update.message.reply_text("Phone number should be 10 digits. Please try again.")

    elif step == 'email':
        email = update.message.text
        if is_valid_email(email):
            context.user_data['email'] = email
            context.user_data['step'] = 'submit'
            await update.message.reply_text(
                f"First Name: {context.user_data['first_name']}\n"
                f"Last Name: {context.user_data['last_name']}\n"
                f"Phone: {context.user_data['phone']}\n"
                f"Email: {context.user_data['email']}\n\n"
                "Do you want to submit? (Yes/No)"
            )
        else:
            await update.message.reply_text("Please enter a valid email address.")

    elif step == 'submit':
        if update.message.text.lower() == 'yes':
            store_data(
                context.user_data['first_name'],
                context.user_data['last_name'],
                context.user_data['phone'],
                context.user_data['email']
            )
            await update.message.reply_text("Your submission was successful!")
            del context.user_data
        elif update.message.text.lower() == 'no':
            await update.message.reply_text("Do you want to Re App or Close?")
            context.user_data['step'] = 're_app_or_close'
        else:
            await update.message.reply_text("Please reply with 'Yes' or 'No'.")

    elif step == 're_app_or_close':
        if update.message.text.lower() == 're app':
            context.user_data['step'] = 'first_name'
            await update.message.reply_text("Please enter your First Name:")
        elif update.message.text.lower() == 'close':
            await update.message.reply_text("Have a great day!")
            del context.user_data
        else:
            await update.message.reply_text("Please reply with 'Re App' or 'Close'.")

def main():
    application = ApplicationBuilder().token("YOUR_BOT_TOKEN").read_timeout(30).connect_timeout(30).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    application.run_polling(timeout=30, allowed_updates=["message", "edited_message", "callback_query"])

if __name__ == '__main__':
    main()