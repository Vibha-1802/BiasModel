import os
from dotenv import load_dotenv

# Ensure the .env file is loaded from the current directory
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BIAS_DB_URI = os.getenv("BIAS_DB_URI") # Example for external data
