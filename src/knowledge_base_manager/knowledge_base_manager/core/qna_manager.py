from typing import List, Dict, Any
from .database_manager import DatabaseManager
from datetime import datetime
from utils.logger import get_logger
from langchain.callbacks import get_openai_callback
from openai import BadRequestError
from langchain_openai import AzureChatOpenAI
import os

# import logger
logger = get_logger(__name__)

class QnAManager:
    def __init__(self, db_connection_str:str, db_name:str, collection_name: str):
        """Initialise the QnAManager with a DatabaseManager instance
        """

        # Defines the instance of AzureChatOpenAI class
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_APIKEY"),
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
            model_name=os.environ.get("AZURE_OPENAI_MODEL_NAME"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            temperature=0,
        )

        self.db_manager = DatabaseManager(db_connection_str=db_connection_str, db_name=db_name, collection_name=collection_name)


    def add_unanswered_question(self, question:str)->bool:
        """Add a new unanswered question to the database

        Args:
            question (str): The question to add

        Returns:
            bool: True if the operation is successful
        """
        # add current time
        now = datetime.now()

        document = {"question": question, "answer": "", "status": "Unanswered", "timestamp": now, "irrelevant": False}
        return self.db_manager.insert_document(document)

    def add_answer_to_question(self, question:str, answer:str)->bool:
        """Add an answer to an existing question in the database

        Args:
            question (str): The question to update
            answer (str): The answer to add

        Returns:
            bool: Returns True if the question is found and updated.
        """

        query = {"question": question}
        update = {"answer": answer, "status": "Answered"}

        return self.db_manager.update_document(query=query, update=update)


    def mark_question_irrelevant(self, question: str) -> bool:
        """
        Mark a question as irrelevant.

        :param question: The question to mark
        :return: True if the question is found and updated
        """
        query = {"question": question}
        update = {"status": "Irrelevant", "irrelevant":True}
        return self.db_manager.update_document(query=query, update=update)

    def get_answered_questions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all answered questions from the database.

        :return: A list of answered question documents
        """
        query = {"status": "Answered", "irrelevant": False}
        return self.db_manager.find_documents(query)

    def get_unanswered_questions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all unanswered questions from the database.

        :return: A list of unanswered question documents
        """
        query = {"status": "Unanswered"}
        return self.db_manager.find_documents(query)

    def get_all_questions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all questions from the database.

        :return: A list of all question documents
        """
        return self.db_manager.find_documents()
    
    def get_relevant_questions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all relevant questions from the database.

        :return: A list of relevant question documents
        """
        query = {"irrelevant": False}
        return self.db_manager.find_documents(query)
    
    def generate_qna_string(self) -> str:
        """
        Generate a formatted string of all answered questions and their answers.

        :return: A formatted QnA string

        Example of QnA string:
        "Question: Will the Lab TAs teach new topics during the Lab Sessions
        Answer: No. There will be no formal lecture or teaching during the Lab Sessions. The main course material is just the LAMS sequences, videos and respective slides. The labs are meant for hands-on programming, and the codes that you work on will be tested through the Lab Exercises. However, your Lab TAs may introduce you to some new material every week while they recap the main ideas behind the respective Lab Exercise. These will not be examinable.

        Question: Can I email the school to S/U this course?
        Answer: Yes, you may email abc@gmail.com"
        """
        # get all answered questions
        answered_questions = self.get_answered_questions()

        # generate qna string
        qna_str = ""
        for doc in answered_questions:
            qna_str += f"Question: {doc['question']}\nAnswer: {doc['answer']}\n\n"

        
        return qna_str

    def rephrase_to_single_question(self, chat_history:List[str]) -> str:
        """
        Rephrases the latest user query in the chat history to be a standalone question.

        Args:
            chat_history (List[str]): The conversation history including the latest user query.

        Returns:
            str: The rephrased standalone question, or None if an error occurs.

        Raises:
            BadRequestError: If an error occurs while invoking the language model.

        Example:
            chat_history = [
            "User: How does the subscription model work?",
            "Bot: The subscription model allows you to access premium features.",
            "User: Can I cancel anytime?"
            ]

            Returns:
            "Can I cancel the subscription anytime?"
        """
        
        rephrase_prompt = f"""Given the following conversation and a follow up question, rephrase the latest user query to be a standalone query. Respond with only the rephrased question.

                            Chat History:
                            {chat_history}"""
        
        logger.info("chat_history: "+str(chat_history))

        try:
            # invoke LLM
            with get_openai_callback() as cb:

                response = self.llm.invoke(rephrase_prompt)

                # logger.info(
                #     f"=======[LLM COST] total cost: {cb.total_cost}; total tokens: {cb.total_tokens}"
                # )

                total_cost = cb.total_cost
                total_tokens = cb.total_tokens

            rephrased_question = response.content
        except BadRequestError as e:
            logger.error("Error occurred while rephrasing question: "+str(e))
            return None

        return rephrased_question

    def resolve_non_trivial_query(self, chat_history: List[str]):
        """
        Resolves a non-trivial query by rephrasing the chat history into a single question and adding it to the list of unanswered questions.
        Args:
            chat_history (List[str]): The conversation history including the latest user query.
        Example:
            chat_history = [
            "What is the capital of France?",
            "I mean, where is the Eiffel Tower located?",
            "Can you tell me the city where the Eiffel Tower is?"
            ]
        Returns:
            None
        """

        # rephrase query into a single question
        rephrased_query = self.rephrase_to_single_question(chat_history=chat_history)

        if rephrased_query is not None:
                # print latest_chat_history
                logger.info("Rephrased query: "+rephrased_query)
                # add question to unanswered questions
                self.add_unanswered_question(question=rephrased_query)
        else:
            logger.error("Error in resolving non-trivial query")
            