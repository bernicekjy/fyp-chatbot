from azure.search.documents import SearchClient
import os
from azure.core.credentials import AzureKeyCredential
from langchain_openai import AzureChatOpenAI
from typing import List
from langchain.callbacks import get_openai_callback
from datetime import datetime

# ----DEFAULT CONFIGS-----
course_name = "SC1015 Data Science and Artificial Intelligence"
dummy = ""
now = datetime.now().strftime("%Y-%m-%d")
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
            index_name="fyp-sc1015-without-faqs",
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

        self.sysmsg_temp = (
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
            f"provided, respond with ONLY 'QUERY_INSTRUCTOR' and the question will be directed to the instructor"
        )

        self.chat_history = []

        self.total_api_cost = 0
        self.total_api_tokens = 0

    def get_context(self, query, k=5):
        contexts = []
        sources = []

        documents = self.search_client.search(query, top=k)
        for doc in documents:
            # pprint.pprint(doc)
            # print("-------")
            contexts.append(doc["content"])
            sources.append(doc["filename"])
        # pprint.pprint(
        #     f"=====Retriever Info======\nCONTEXTS: {contexts}\nSOURCES {sources}"
        # )
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

    def is_trivial_query(self, query, num_chat_history=6):
        # get context
        context, sources = self.get_context(query=query)

        # extract top few chats
        latest_chat_history = self.get_latest_chat_history(
            num_chat_history=num_chat_history
        )

        trivial_query_prompt = (
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
            f"YYYY-MM-DD."
            f"Based on the context retrieved and user query, please assess whether more context is required regarding the course.\nContext: {context}\nChat History: {latest_chat_history}\nUser Query: {query}"
            f"Respond with ONLY 'YES' if you need more context regarding the course information, or ONLY 'NO' if "
            f"the provided context is sufficient and you do not need more context regarding the course."
        )

        trivial_query_prompt_2 = (
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
            f"YYYY-MM-DD."
            f"Based on the context retrieved and user query, decide if you have enough context information regarding the course in order to answer the query. If more information is required, the query will be forwarded to the course instructor for them to answer. It is only necessary to ask for more information if you are unable to answer the query AND more context on course information would help you answer the query.\nContext: {context}\nUser Query: {query}"
            f"\nRespond with ONLY 'YES' if you need more information from the course instructor, or ONLY 'NO' if "
            f"the provided context on course information is sufficient and you do not need more context regarding the course."
        )

        

        trivial_query_prompt_3 = (
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
            f"YYYY-MM-DD."
            f"Based on the context retrieved and user query, determine you are unsure how to respond to a query based on the course information. \nContext: {context}\nChat History: {latest_chat_history}\nUser Query: {query}"
            f"Respond with ONLY 'YES' if you are unsure on how to respond to the query, or ONLY 'NO' if "
            f"you are able to answer the query"
        )

        trivial_query_prompt_4 = (
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
            f"YYYY-MM-DD."
            f"Based on the context retrieved and user query, decide if it is necessary to forward the query to the course instructor for them to answer.\nContext: {context}\nUser Query: {query}"
            f"\nRespond with ONLY 'YES' if you need more information from the course instructor, or ONLY 'NO' if "
            f"the provided context is sufficient and you do not need more context regarding the course."
        )

        # invoke LLM
        with get_openai_callback() as cb:
            print("\n\n---prompt used:\n", trivial_query_prompt_4)
            response = self.llm.invoke(trivial_query_prompt_4)

            total_cost = cb.total_cost
            total_tokens = cb.total_tokens

        return {"is_trivial_query":response.content}

    def answer_this(self, query, num_chat_history=6):
        # get context
        context, sources = self.get_context(query=query)

        # extract top few chats
        latest_chat_history = self.get_latest_chat_history(
            num_chat_history=num_chat_history
        )

        # print("latest chat history: ", latest_chat_history)

        # compose complete prompt (with history)
        full_prompt = (
            self.sysmsg_temp
            + "Chat History: "
            + str(latest_chat_history)
            + "\nContext: "
            + str(context)
            + "\nQuery: "
            + query
        )

        # # compose complete prompt (WITHOUT history)
        # full_prompt = self.sysmsg + "\nContext: " + str(context) + "\nQuery: " + query

        # print("FULL PROMPT: ", full_prompt)

        # print("\n\nchat_history: ", latest_chat_history)

        # invoke LLM
        with get_openai_callback() as cb:
            response = self.llm.invoke(full_prompt)

            # print(
            #     f"=======[COST] total cost: {cb.total_cost}; total tokens: {cb.total_tokens}"
            # )

            total_cost = cb.total_cost
            total_tokens = cb.total_tokens

        return {
            "chatbot_response": response.content,
            "context": context,
            "cost": total_cost,
            "tokens": total_tokens,
        }


if __name__ == "__main__":
    bot = Narelle()

    while True:
        query = input("Enter your query: ")
        tq_response = bot.is_trivial_query(query)
        response = bot.answer_this(query=query)
        print("non-trivial query?",tq_response["is_trivial_query"],"\nbot response: \n", response["chatbot_response"])
        print("-------")
