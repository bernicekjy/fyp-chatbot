from knowledge_base_manager.knowledge_base_manager.core.qna_manager import QnAManager
from knowledge_base_manager.knowledge_base_manager.core.knowledge_base_manager import KnowledgeBaseManager
from knowledge_base_manager.knowledge_base_manager.types import Category
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
        self.index_name = "fyp-test-3" # <--- change index name here
 
        
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

        # Define question categories
        question_categories = [
            Category(title="ADMIN", description="Questions about deadlines, submission processes, group work policies, lab sites, or assignment logistics.", example_question="Where do I submit the mini project?"),
            Category(title="TECHNICAL", description="Questions about programming errors, technical setup, or software issues.", example_question="How do I resolve this error when installing the library?"),
            Category(title="CONTENT", description="Questions about course material, lecture content, concepts, or explanations of topics.", example_question="Can you explain the concept of dynamic programming again?"),
            Category(title="EVALUATION", description="Questions about grading criteria, marking schemes, or assessment feedback.", example_question="How many marks is the final project worth?"),
            Category(title="RESOURCE", description="Questions requesting additional resources, study materials, or sample solutions.", example_question="Do you have any sample solutions from last year’s exam?"),
            Category(title="UNCATEGORISED", description="Questions that do not clearly fit into any of the above categories.", example_question="I am confused about something but I’m not sure how to explain it."),
            Category(title="IRRELEVANT", description="Questions that are unrelated to the course or inappropriate.", example_question="What’s the best pizza place near campus?")
        ]
        
        # Define QnA Manager
        self.qna_manager = QnAManager(db_connection_str=os.environ.get("AZURE_COSMOSDB_CONNECTION_STR"),
            db_name = "testDatabase", # <--- change database name here
            collection_name = "testQuestions4", # <--- change collection name here
            llm=llm,
            rephrase_question=True,
            categorise_question=True,
            categories=question_categories)

        # Defines chatbot kb manager
        self.kb = KnowledgeBaseManager(azure_text_embedding_config=azure_text_embedding_config, azure_ai_search_config=azure_ai_search_config,
        index_name=self.index_name)

        

    def sync_qna_to_kb(self):
        # generate a new qna document and update kb
        return self.kb.fetch_and_index_cosmosdb_data( qna_manager=self.qna_manager)

    def create_index(self):
        return self.kb.create_index()
