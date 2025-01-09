from typing import List, Dict, Any
from .database_manager import DatabaseManager
import uuid

class QnAManager:
    def __init__(self, db_manager: DatabaseManager):
        """Initialise the QnAManager with a DatabaseManager instance

        Args:
            db_manager (DatabaseManager): A DatabaseManager object instance 
        """

        self.db_manager = db_manager
    
    def add_unanswered_question(self, question:str)->bool:
        """Add a new unanswered question to the database

        Args:
            question (str): The question to add

        Returns:
            bool: True if the operation is successful
        """

        document = {"id": str(uuid.uuid4()),"question": question, "answer": "", "status": "unanswered"}
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
        update = {"answer": answer, "status": "answered"}

        return self.db_manager.update_document(query=query, update=update)


    def mark_question_irrelevant(self, question: str) -> bool:
        """
        Mark a question as irrelevant.

        :param question: The question to mark
        :return: True if the question is found and updated
        """
        query = {"question": question}
        update = {"status": "irrelevant"}
        return self.db_manager.update_document(query=query, update=update)

    def get_answered_questions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all answered questions from the database.

        :return: A list of answered question documents
        """
        query = {"status": "answered"}
        return self.db_manager.find_documents(query)

    def get_unanswered_questions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all unanswered questions from the database.

        :return: A list of unanswered question documents
        """
        query = {"status": "unanswered"}
        return self.db_manager.find_documents(query)

    def get_all_questions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all questions from the database.

        :return: A list of all question documents
        """
        return self.db_manager.find_documents()
    
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