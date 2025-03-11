from knowledge_base_manager.core.database_manager import DatabaseManager
from knowledge_base_manager.core.qna_manager import QnAManager
from knowledge_base_manager.core.knowledge_base_manager import KnowledgeBaseManager
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Initialising Ask Narelle's knowledge base manager
class AN_KB_Manager:
    def __init__(self):

        azure_openai_config={
                        "endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
                        "api_key": os.environ.get("AZURE_OPENAI_APIKEY"),
                        "deployment_name": os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
                        "model_name": os.environ.get("AZURE_OPENAI_MODEL_NAME"),
                        "api_version": os.environ.get("AZURE_OPENAI_API_VERSION")
                    }

        azure_text_embedding_config={
                        "azure_deployment": os.environ.get("TEXT_EMBEDDING_MODEL_DEPLOYMENT"),
                        "api_key": os.environ.get("AZURE_OPENAI_APIKEY"),
                        "endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
                        "model": os.environ.get("TEXT_EMBEDDING_MODEL_NAME")
                    }
        
        azure_ai_search_config = {
                        "endpoint": os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
                        "api_key": os.environ.get("AZURE_AI_SEARCH_API_KEY"),
        }

        # Defines index name
        self.index_name = "fyp-test-2"
 
        
        # Initialise LLM
        azure_openai_endpoint = azure_openai_config.get("endpoint")
        azure_openai_api_key = azure_openai_config.get("api_key")
        azure_openai_deployment_name = azure_openai_config.get("deployment_name")
        azure_openai_model_name = azure_openai_config.get("model_name")
        azure_opanai_api_version = azure_openai_config.get("api_version")

        llm =AzureChatOpenAI(
                azure_endpoint=azure_openai_endpoint,
                api_key=azure_openai_api_key,
                deployment_name=azure_openai_deployment_name,
                model_name=azure_openai_model_name,
                api_version=azure_opanai_api_version,
                temperature=0,
            )

        
        # Define QnA Manager
        self.qna_manager = QnAManager(db_connection_str=os.environ.get("AZURE_COSMOSDB_CONNECTION_STR"),
            db_name = "testDatabase",
            collection_name = "testQuestions2",
            rephrase_question=True,
            categorise_question=True,
            llm=llm)

        # Defines chatbot kb manager
        self.kb = KnowledgeBaseManager(azure_text_embedding_config=azure_text_embedding_config, azure_ai_search_config=azure_ai_search_config,
        index_name=self.index_name)

        

    def sync_qna_to_kb(self):
        # generate a new qna document and update kb
        return self.kb.fetch_and_index_cosmosdb_data( qna_manager=self.qna_manager)

