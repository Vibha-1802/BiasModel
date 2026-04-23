import os
from dotenv import load_dotenv

# Ensure the .env file is loaded from the current directory
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_KEY2 = os.getenv("GROQ_API_KEY2")
GROQ_API_KEY3 = os.getenv("GROQ_API_KEY3")

BIAS_DB_URI = os.getenv("BIAS_DB_URI") # Example for external data
