from kb.AN_KnowledgeBase import KnowledgeBaseManager
from kb.utils import load_document
import pymongo
import sys
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Load environment variables from the .env file
load_dotenv()

class RLKnowledgeBaseManager(KnowledgeBaseManager):
    def __init__(self):
        super().__init__()
    
        # Name of QnA document
        self.qna_document = "/Users/bern/Documents/GitHub/fyp-chatbot/db/asknarelle_qna.txt"

        # Connect to question database
        # Get MongoDB Atlas connection string
        db_connection_str = os.environ.get("ATLAS_CONNECTION_STR")
        
        try:
            client = pymongo.MongoClient(db_connection_str)
            # return a friendly error if a URI error is thrown 
        except pymongo.errors.ConfigurationError:
            print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
            sys.exit(1)
        
        # use a database named "qnaDatabase"
        db = client.qnaDatabase

        # use a collection named "questions"
        self.questions_collection = db["questions"]
        

    def initialise_collection(self):
        # drop the collection in case it already exists
        try:
            self.questions_collection.drop()
        # return a friendly error if an authentication error is thrown
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are your username and password correct in your connection string?")
            sys.exit(1)

    def update_qna_document(self, index_name):
        # content of qna document
        content = self.generate_qna_str()
        print("Content: ", content)

        # write to document
        with open(self.qna_document, "w") as file:
            file.write(content)

        # add to index
        doc = load_document(self.qna_document)
        super().add_or_update_docs(documents=[doc], index_name=index_name)

    def generate_qna_str(self):
        # find all questions that have been answered
        result = self.questions_collection.find({"answer":{"$ne":""}})

        # convert result to Python dict
        result_str = ""
        
        if result:
            for doc in result:
                # get question and answer
                question = doc["question"]
                answer = doc["answer"]

                # add qna pair to result_str
                result_str += f"Question: {question}\nAnswer: {answer}\n\n"

        return result_str


    def add_unanswered_question(self, new_question):

        self.questions_collection.insert_one({"question": new_question, "answer": "", "status": "unanswered"})

        return True
    
    def add_answer_to_question(self, question, answer):
        new_doc = self.questions_collection.find_one_and_update({"question": question}, {"$set": { "answer": answer , "status": "answered"}}, new=True)

        if new_doc is not None: # return True if question found and updated
            return True
        else: # return False if question not found
            return False


    def mark_question_irrelevant(self, question):
        new_doc = self.questions_collection.find_one_and_update({"question": question}, {"$set": {"status": "irrelevant"}}, new=True)

        if new_doc is not None: # return True if question found and updated
            return True
        else: # return False if question not found
            return False

    def delete_unanswered_question(self, question_to_delete):
        # delete documents with the question as question_to_delete
        deletion_result = self.questions_collection.delete_one({"question":question_to_delete})
        
        return deletion_result
    
    def get_unanswered_questions(self):
        # find questions with no answer
        result = self.questions_collection.find({"answer":""})

        # convert result to Python dict
        result_dict = []
        
        if result:
            for doc in result:
                result_dict.append(doc)

        return result_dict

    def get_answered_questions(self):
        # find all questions that have been answered
        result = self.questions_collection.find({"answer":{"$ne":""}})

        # convert result to Python dict
        result_dict = []
        
        if result:
            for doc in result:
                result_dict.append(doc)

        return result_dict

    def get_all_questions(self):
        # find all list of questions
        result = self.questions_collection.find()

        # convert result to Python dict
        result_dict = []
        
        if result:
            for doc in result:
                result_dict.append(doc)

        return result_dict

