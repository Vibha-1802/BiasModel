from langchain_groq import ChatGroq
from config import GROQ_API_KEY, GROQ_API_KEY2

llm = ChatGroq(groq_api_key=GROQ_API_KEY2, model_name="llama-3.3-70b-versatile")
