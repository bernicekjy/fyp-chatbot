from knowledge_base_manager.core.database_manager import DatabaseManager
from knowledge_base_manager.core.qna_manager import QnAManager
from knowledge_base_manager.core.knowledge_base_manager import KnowledgeBaseManager
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Initialising Ask Narelle's knowledge base manager
class AN_KB_Manager:
    def __init__(self):

        # Defines QnA kb manager
        self.qna_manager = QnAManager(db_connection_str=os.environ.get("AZURE_COSMOSDB_CONNECTION_STR"),
            db_name = "qnaDatabase",
            collection_name = "questions")

        # Defines chatbot kb manager
        self.kb = KnowledgeBaseManager(text_embedding_azure_deployment=os.environ.get("TEXT_EMBEDDING_MODEL_DEPLOYMENT"), 
        azure_openai_api_key=os.environ.get("AZURE_OPENAI_APIKEY"), 
        azure_openai_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"), 
        text_embedding_model=os.environ.get("TEXT_EMBEDDING_MODEL_NAME"),
        azure_ai_search_endpoint=os.environ.get("AZURE_AI_SEARCH_ENDPOINT"), 
        azure_ai_search_api_key=os.environ.get("AZURE_AI_SEARCH_API_KEY"),
        index_name=os.environ.get("AZURE_AI_SEARCH_INDEX_NAME"))

        # Defines index name
        self.index_name = os.environ.get("AZURE_AI_SEARCH_INDEX_NAME")

    def sync_qna_to_kb(self):
        # generate a new qna document and update kb
        return self.kb.fetch_and_index_cosmosdb_data( qna_manager=self.qna_manager)

