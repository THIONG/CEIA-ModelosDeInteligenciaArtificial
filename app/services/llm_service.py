from langchain_ollama import ChatOllama
from app.config import config

class LLMService:
    
    def __init__(self):
        self.model = ChatOllama(model=config.LLM_MODEL)
    
    def generate_response(self, messages):
        return self.model.invoke(messages).content

llm_service = LLMService()
