from azure.search.documents import SearchClient
import os
from azure.core.credentials import AzureKeyCredential
from langchain_openai import AzureChatOpenAI
from typing import List
from langchain.callbacks import get_openai_callback
from datetime import datetime
from rl_knowledge_base_manager.core.database_manager import DatabaseManager
from rl_knowledge_base_manager.core.qna_manager import QnAManager
from utils.logger import get_logger

# import logger
logger = get_logger(__name__)
course_name = os.environ.get("COURSE_NAME")

class Narelle:
    def __init__(
        self, 
    ):
        # Defines the instance of AzureChatOpenAI class
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_APIKEY"),
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
            model_name=os.environ.get("AZURE_OPENAI_MODEL_NAME"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            temperature=0,
        )

        # Defines retriever used
        self.search_client = SearchClient(
            endpoint=os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
            index_name="fyp-sc1015-without-faqs",
            credential=AzureKeyCredential(os.environ.get("AZURE_AI_SEARCH_API_KEY")),
        )

        # Defines chatbot prompt
        now = datetime.now()
        self.sysmsg = (
            f"You are a university course assistant. Your name is Narelle. Your task is to answer student "
            f"queries for the course {course_name} based on the information retrieved from the knowledge bas"
            f"e along with the conversation with user. There are some terminologies which "
            f"referring to the same thing, for example: assignment is also refer to assessment, project also "
            f"refer to mini-project, test also refer to quiz. Week 1 starting from 15 Jan 2024, Week 8 starting "
            f"from 11 March 2024, while Week 14 starting from 22 April 2024. \n\nIn addition to that, "
            f"the second half of this course which is the AI part covers the syllabus and content from the "
            f"textbook named 'Artificial Intelligence: A Modern Approach (3rd edition)' by Russell and Norvig . "
            f"When user ask for tips or sample questions for AI Quiz or AI Theory Quiz, you can generate a few "
            f"MCQ questions with the answer based on the textbook, 'Artificial Intelligence: A Modern Approach ("
            f"3rd edition)' from Chapter 1, 2, 3, 4, and 6. Lastly, remember today is {now} in the format of "
            f"YYYY-MM-DD.\n\nIf you are unsure how to respond to a query based on the course information "
            f"provided, respond with ONLY 'QUERY_INSTRUCTOR' and the question will be directed to the instructor."
        )

        # Initialise chat history
        self.chat_history = []

        # Defines QnA manager and database to store QnAs
        qna_db_manager = DatabaseManager(
            db_connection_str=os.environ.get("ATLAS_CONNECTION_STR"),
            db_name = "qnaDatabase",
            collection_name = "questions")
        self.qna_manager = QnAManager(qna_db_manager)

        # Cost tracking
        self.total_api_cost = 0
        self.total_api_tokens = 0

    def get_context(self, context_query:str, k:int=5) -> (list, list):
        """Retrieves context from knowledge base based on query

        Args:
            context_query (str): Query for retrieving
            k (int, optional): Number of top documents to retrieve. Defaults to 5.

        Returns:
            context, sources (list, list): Returns list of contexts and their corresponding sources
        """
        contexts = []
        sources = []

        documents = self.search_client.search(context_query, top=k)
        for doc in documents:
            contexts.append(doc["content"])
            sources.append(doc["filename"])

        return contexts, list(set(sources))

    def get_total_tokens_cost(self):
        return {
            "overall_cost": self.total_api_cost,
            "overall_tokens": self.total_api_tokens,
        }

    def set_chat_history(self, chat_history: List[str]):
        self.chat_history = chat_history

    def clear_chat_history(self):
        self.chat_history = []

    def get_latest_chat_history(self, num_chat_history):
        # extract top few chats
        latest_chat_history = self.chat_history

        if len(latest_chat_history) > num_chat_history:
            latest_chat_history = self.chat_history[(num_chat_history * -1) :]

        return latest_chat_history

    def answer_this(self, query, num_chat_history=6):
        # get context
        context, sources = self.get_context(context_query=query)

        context_string = "\n\n---------------\n".join(context)

        # extract top few chats
        latest_chat_history = self.get_latest_chat_history(
            num_chat_history=num_chat_history
        )

        # compose complete prompt (with history)
        full_prompt = (
            self.sysmsg
            + "Chat History: "
            + str(latest_chat_history)
            + "\nContext: "
            + context_string
            + "\nQuery: "
            + query
        )

        # print context
        logger.info("\n\n===== CONTEXT FOR QUERY '"+query+"' =====\n\n"+context_string+"\n===================\n")

        # invoke LLM
        with get_openai_callback() as cb:
            response = self.llm.invoke(full_prompt)

            logger.info(
                f"=======[LLM COST] total cost: {cb.total_cost}; total tokens: {cb.total_tokens}"
            )

            total_cost = cb.total_cost
            total_tokens = cb.total_tokens
        
        chatbot_response = response.content

        # if non-trivial question, query instructor
        if "QUERY_INSTRUCTOR" in chatbot_response:

            # chatbot response upon non-trivial question
            chatbot_response = "Sorry, I am unable to answer your question. I have forwarded your question to your course instructor."

            # add question to unanswered questions
            self.qna_manager.add_unanswered_question(question=query)
            

        return {
            "chatbot_response": chatbot_response,
            "context": context_string,
            "cost": total_cost,
            "tokens": total_tokens,
        }
    

if __name__ == "__main__":
    bot = Narelle()

    while True:
        query = input("Enter your query: ")
        tq_response = bot.is_trivial_query(query)
        response = bot.answer_this(query=query)
        
        print("Response: \n", response)
