from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if self.api_key:
            self.llm = ChatOpenAI(
                api_key=self.api_key,
                model="gpt-4-turbo-preview", # Or gpt-3.5-turbo
                temperature=0.7
            )
        else:
            logger.warning("OPENAI_API_KEY not found. AI features will be disabled.")
            self.llm = None

    async def process_text_order(self, text: str, language: str = "ar"):
        """
        Process a natural language order text and extract structured data.
        """
        if not self.llm:
            return {"error": "AI service not configured"}

        # Simple prompt for now
        system_prompt = """
        You are a helpful restaurant ordering assistant. 
        Extract the order items, quantity, and any special notes from the user's message.
        Return the result as a JSON object.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{text}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        
        try:
            response = await chain.ainvoke({"text": text})
            return response # In real implementation, parse JSON here
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return {"error": str(e)}

ai_service = AIService()
