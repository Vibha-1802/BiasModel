from langchain_groq import ChatGroq
from config import GROQ_API_KEY, GROQ_API_KEY2,GROQ_API_KEY3

llm = ChatGroq(groq_api_key=GROQ_API_KEY3, model_name="llama-3.3-70b-versatile")
