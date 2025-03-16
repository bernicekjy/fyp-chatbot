import streamlit as st
import os
import sys
from dotenv import load_dotenv
from chatbot.Narelle import Narelle
import pprint
from knowledge_base_manager.knowledge_base_manager.core.database_manager import DatabaseManager
from knowledge_base_manager.knowledge_base_manager.core.qna_manager import QnAManager

# Load environment variables from the .env file
load_dotenv()

# Initialise chatbot
chatbot = Narelle()

# Set up page
st.set_page_config(
    page_title="AskNarelle - Your friendly course assistant", page_icon="🙋‍♀️",layout='wide'
)
st.title(":woman-raising-hand: Ask Narelle")
st.write(f"For queries related to {os.environ.get('COURSE_NAME')}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

chat_avatars = {
    "ai": "imgs/ai_avatar.jpg",
    "user": {
        "Male": "imgs/male_user_avatar.jpg",
        "Female": "imgs/female_user_avatar.jpg",
    },
}

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Accept user input
if prompt := st.chat_input("Ask Narelle a question..."):

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Ask chatbot question
    response = chatbot.answer_this(query=prompt)
    chatbot_response = response["chatbot_response"]
    context = response["context"]

    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(prompt)

    # Display chatbot message
    with st.chat_message("assistant"):
        
        st.write(chatbot_response)

        # with st.popover("View context used"):
        #     st.write(context)
        

    st.session_state.messages.append({"role": "assistant", "content": chatbot_response})

    # # update backend's chat history
    # chat_history_content = [message["content"] for message in st.session_state.messages]
    # chatbot.set_chat_history(chat_history=chat_history_content)

    # print("Chat history: ", chatbot.chat_history)


# st.write(st.session_state.messages)

