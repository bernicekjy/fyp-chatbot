from kb.AN_KnowledgeBase import KnowledgeBaseManager
from kb.utils import load_document
import json

class RLKnowledgeBaseManager(KnowledgeBaseManager):
    def __init__(self):
        super().__init__()
    
        # Name of QnA document
        self.qna_document = "db/asknarelle_qna.txt"

        # List of unanswered questions
        self.unanswered_questions_file = "db/unanswered_questions.json"

    def update_qna_document(self, question, answer, index_name):
        # content to add to document
        content = f"\n\nQuestion: {question}\nAnswer: {answer}"

        # write to document
        f = open(self.qna_document, "a")
        f.write(content)
        f.close()

        # add to index
        doc = load_document(self.qna_document)
        super().add_or_update_docs(documents=[doc], index_name=index_name)

    def add_unanswered_question(self, new_question):
        # open JSON file consisting of unanswered questions
        with open(self.unanswered_questions_file, "r") as jsonFile:
            data = json.load(jsonFile)

        data.append({"question": new_question, "answer": ""})

        # write updated data to JSON file
        with open(self.unanswered_questions_file, "w") as jsonFile:
            json.dump(data, jsonFile)

        return True
    
    def delete_unanswered_question(self, question_to_delete):
        fileDeleted = False

        # open JSON file consisting of unanswered questions
        with open(self.unanswered_questions_file, "r") as jsonFile:
            data = json.load(jsonFile)

        # delete question
        for i, row in enumerate(data):

            if row["question"]==question_to_delete:
                data.pop(i)
                fileDeleted = True
                break

        # write updated data to JSON file
        with open(self.unanswered_questions_file, "w") as jsonFile:
            json.dump(data, jsonFile)
        
        return fileDeleted
    
    def get_unanswered_questions(self):
        # open JSON file consisting of unanswered questions
        with open(self.unanswered_questions_file, "r") as jsonFile:
            data = json.load(jsonFile)

        return data
