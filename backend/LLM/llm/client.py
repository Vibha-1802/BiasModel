from langchain_groq import ChatGroq
from config import GROQ_API_KEY

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")
