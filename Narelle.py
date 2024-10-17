
from azure.search.documents import SearchClient
import os
from azure.core.credentials import AzureKeyCredential
import pprint
from langchain_openai import AzureChatOpenAI

# ----DEFAULT CONFIGS-----
course_name = "SC1015 Data Science and Artificial Intelligence"
dummy = ""
now = "19 September 2024"
directory_path = "/Users/bern/Documents/GitHub/fyp-chatbot/test_document/"


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
            index_name="index1",
            credential=AzureKeyCredential(os.environ.get("AZURE_AI_SEARCH_API_KEY")),
        )

        self.sysmsg = (
            f"You are a university course assistant. Your name is Narelle. Your task is to answer student "
            f"queries for the course {course_name} based on the information retrieved from the knowledge bas"
            f"e (as of {dummy}) along with the conversation with user. There are some terminologies which "
            f"referring to the same thing, for example: assignment is also refer to assessment, project also "
            f"refer to mini-project, test also refer to quiz. Week 1 starting from 15 Jan 2024, Week 8 starting "
            f"from 11 March 2024, while Week 14 starting from 22 April 2024. \n\nIn addition to that, "
            f"the second half of this course which is the AI part covers the syllabus and content from the "
            f"textbook named 'Artificial Intelligence: A Modern Approach (3rd edition)' by Russell and Norvig . "
            f"When user ask for tips or sample questions for AI Quiz or AI Theory Quiz, you can generate a few "
            f"MCQ questions with the answer based on the textbook, 'Artificial Intelligence: A Modern Approach ("
            f"3rd edition)' from Chapter 1, 2, 3, 4, and 6. Lastly, remember today is {now} in the format of "
            f"YYYY-MM-DD.\n\nIf you are unsure how to respond to a query based on the course information "
            f"provided, just say sorry, inform the user you are not sure, and recommend the user to email to the "
            f"course coordinator or instructors (smitha@ntu.edu.sg | chinann.ong@ntu.edu.sg). "
        )

    def get_context(self, query, k=5):
        contexts = []
        sources = []

        documents = self.search_client.search(query)
        for doc in documents:
            # pprint.pprint(doc)
            # print("-------")
            contexts.append(doc["content"])
            sources.append(doc["filename"])
        pprint.pprint(
            f"=====Retriever Info======\nCONTEXTS: {contexts}\nSOURCES {sources}"
        )
        return contexts, list(set(sources))

    def answer_this(self, query):
        # get context
        context, sources = self.get_context(query=query)

        response = self.llm.invoke(
            self.sysmsg + "\nContext: " + " ".join(context) + "\nQuery: " + query
        )

        return response.content


if __name__ == "__main__":
    bot = Narelle()

    while True:
        query = input("Enter your query: ")
        bot.answer_this(query)
        print("-------")
