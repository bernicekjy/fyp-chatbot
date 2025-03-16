from typing import List, Dict, Any
from .database_manager import DatabaseManager
from datetime import datetime
from langchain.callbacks import get_openai_callback
from openai import BadRequestError
from langchain_core.language_models import BaseLanguageModel
from knowledge_base_manager.knowledge_base_manager.types import Category

class QnAManager:
    def __init__(self, db_connection_str: str, db_name: str, collection_name: str, llm:BaseLanguageModel=None, rephrase_question:bool = False, categorise_question:bool=False, categories:List[Category]=None):
        """
        Initializes the QnAManager with the specified parameters.

        Args:
            db_connection_str (str): The connection string for the database.
            db_name (str): The name of the database.
            collection_name (str): The name of the collection within the database.
            llm (BaseLanguageModel, optional): The language model to use for processing questions. Defaults to None.
            rephrase_question (bool, optional): Whether to rephrase the question before processing. Defaults to False.
            categorise_question (bool, optional): Whether to categorize the question. Defaults to False.
            categories (List[Category], optional): A list of categories for question classification. Defaults to None.

        Example:
            qna_manager = QnAManager(
                db_connection_str="your_connection_string",
                db_name="your_db_name",
                collection_name="your_collection_name",
                llm=your_language_model,
                rephrase_question=True,
                categorise_question=True,
                categories=[Category(title="Example", description="Example category", example_question="What is an example?")]
            )
        """
       

        # Set flags for LLM features
        self.rephrase_question = rephrase_question
        self.categorise_question = categorise_question

        # If LLM configs provided, initialise Azure OpenAI LLM
        if llm is not None:
            self.llm = llm
    
        else:
            # if LLM configs not provided, do not allow rephrasing
            if self.rephrase_question is True:
                raise Exception("Rephrasing not allowed. To allow rephrasing, please provide Azure OpenAI LLM configs.")

                self.rephrase_question = False

            # if LLM configs not provided, do not allow categorising questions
            if self.categorise_question is True:
                raise Exception("Categorising questions not allowed. To allow rephrasing, please provide Azure OpenAI LLM configs.")

                self.categorise_question = False

        # initialise database manager
        self.db_manager = DatabaseManager(db_connection_str=db_connection_str, db_name=db_name, collection_name=collection_name) 

        # Initialise categorise question prompt
        if self.categorise_question:
            if categories is not None:
                self.categories = categories
            else:
                raise Exception("Categorising questions not allowed. To allow rephrasing, please provide the relevant categories.")
        

    def generate_categories_list_string(self, categories: List[Category]) -> str:
        """
        Generates a formatted categories list string from a list of category dictionaries.

        Args:
            categories (List[Category]): A list of type Category, each containing 'title', 'description', and 'example_question'.

        Returns:
            str: A formatted categories list string.
        """
        categories_list = "CATEGORIES:\n"
        for category in categories:
            categories_list += f"- {category.title.upper()}: {category.description}\n"
        categories_list += "\n"
        
        for i, category in enumerate(categories):
            categories_list += f"EXAMPLE {i + 1}\n"
            categories_list += f"Question: \"{category.example_question}\"\n"
            categories_list += f"Return: {category.title.upper()}\n\n"
        
        return categories_list

    def add_unanswered_question(self, question:str, category:str=None)->bool:
        """Add a new unanswered question to the database

        Args:
            question (str): The question to add

        Returns:
            bool: True if the operation is successful
        """
        # add current time
        now = datetime.now()

        if category is None:
            document = {"question": question, "answer": "", "status": "Unanswered", "timestamp": now, "irrelevant": False}
        else:
            if category == "IRRELEVANT":
                document = {"question": question, "answer": "", "status": "Unanswered", "category": category, "timestamp": now, "irrelevant": True}
            else:
                document = {"question": question, "answer": "", "status": "Unanswered", "category": category, "timestamp": now, "irrelevant": False}

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

    
    def mark_question_relevant(self, question: str) -> bool:
        """
        Mark a question as relevant.

        :param question: The question to mark
        :return: True if the question is found and updated
        """

        query = {"question": question}

        # get new status of question
        answer = self.db_manager.find_documents(query)

        print("answer: ", answer)
        if answer == "":
            new_status = "Unanswered"
        else:
            new_status = "Answered"

        update = {"status": new_status, "irrelevant":False}

        
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
            raise Exception("Error occurred while rephrasing question: "+str(e))
            return None

        return rephrased_question

    def get_question_category(self,user_question:str)->str:
        """
        Categorizes a student's question into one of several predefined categories.

        Args:
            user_question (str): The question asked by the student.
        Returns:
            str: The category name
        """

        # unused variable
        categorise_prompt_full = f"""You are a helpful assistant for a course instructor. 
                                Your task is to categorize student questions into one of the following categories. 
                                You should return ONLY the category name in CAPITAL LETTERS. 
                                Do not explain your reasoning or provide additional text. 
                                Choose the most appropriate category from the list below:

                                CATEGORIES:
                                - ADMIN: Questions about deadlines, submission processes, group work policies, lab sites, or assignment logistics.
                                - TECHNICAL: Questions about programming errors, technical setup, or software issues.
                                - CONTENT: Questions about course material, lecture content, concepts, or explanations of topics.
                                - EVALUATION: Questions about grading criteria, marking schemes, or assessment feedback.
                                - RESOURCE: Questions requesting additional resources, study materials, or sample solutions.
                                - UNCATEGORISED: Questions that do not clearly fit into any of the above categories.
                                - IRRELEVANT: Questions that are unrelated to the course or inappropriate.

                                EXAMPLE 1
                                Question: "Where do I submit the mini project?"
                                Return: ADMIN

                                EXAMPLE 2
                                Question: "How do I resolve this error when installing the library?"
                                Return: TECHNICAL

                                EXAMPLE 3
                                Question: "Can you explain the concept of dynamic programming again?"
                                Return: CONTENT

                                EXAMPLE 4
                                Question: "How many marks is the final project worth?"
                                Return: EVALUATION

                                EXAMPLE 5
                                Question: "Do you have any sample solutions from last year’s exam?"
                                Return: RESOURCE

                                EXAMPLE 6
                                Question: "What’s the best pizza place near campus?"
                                Return: IRRELEVANT

                                EXAMPLE 7
                                Question: "I am confused about something but I’m not sure how to explain it."
                                Return: UNCATEGORISED

                                NOW CATEGORIZE THE FOLLOWING QUESTION:
                                Question: "{user_question}"
                                Return:

                                """

        # get the categories in a form of a string
        categories_list = self.generate_categories_list_string(self.categories)

        categorise_prompt = f"""You are a helpful assistant for a course instructor. Your task is to categorize student questions into one of the following categories. You should return ONLY the category name in CAPITAL LETTERS. 
                                Do not explain your reasoning or provide additional text. Choose the most appropriate category from the list below:

                                {categories_list}

                                NOW CATEGORIZE THE FOLLOWING QUESTION:
                                Question: "{user_question}"
                                Return:

                                """
        
        print("categorise_prompt:\n", categorise_prompt)
        # invoke LLM
        with get_openai_callback() as cb:

            response = self.llm.invoke(categorise_prompt)

            # logger.info(
            #     f"=======[LLM COST] total cost: {cb.total_cost}; total tokens: {cb.total_tokens}"
            # )

            total_cost = cb.total_cost
            total_tokens = cb.total_tokens
                
        return response.content
    

    def resolve_non_trivial_query(self, chat_history: List[str]):
        """
        Resolves a non-trivial query by rephrasing the chat history into a single question (if LLM configs provided) and adding it to the list of unanswered questions.
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

        # Rephrase question if flag is set
        if self.rephrase_question is True:
            try:
                # rephrase query into a single question with LLM
                query_to_add = self.rephrase_to_single_question(chat_history=chat_history)
            except Exception as e:
                raise Exception("Error occurred while rephrasing question.")
                return
        else:
            # use latest question as query
            query_to_add = chat_history[-1]

        # Categorise question if flag is set
        if self.categorise_question is True:
            # categorise the question
            category = self.get_question_category(user_question=query_to_add)

            # add question to database
            self.add_unanswered_question(question=query_to_add, category=category)
        else:
            self.add_unanswered_question(question=query_to_add)
            