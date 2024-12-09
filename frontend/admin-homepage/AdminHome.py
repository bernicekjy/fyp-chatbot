import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from kb.AN_RL_KnowledgeBase import RLKnowledgeBaseManager
import pprint

# # Load environment variables from the .env file
# load_dotenv()

# Set up page
st.set_page_config(
    page_title="AskNarelle - Course Coordinator Page", page_icon="🙋"
)
st.title(":woman-raising-hand: AN Admin")
st.write(f"For answering non-trivial queries related to {os.environ.get('COURSE_NAME')}")

# initialise KB manager
kb = RLKnowledgeBaseManager()

# sample data
initial_sample = pd.DataFrame(
    [
        {"question": "Question 1?", "answer": ""},
        {"question": "Question 2", "answer": ""},
        {"question": "Question 3", "answer": ""},
    ]
)

initial_data = kb.get_unanswered_questions()

# if 'initial_df' not in st.session_state:
#     st.session_state['initial_df'] = initial_data

st.session_state['initial_df'] = kb.get_unanswered_questions()
if 'updated_df ' not in st.session_state:
    st.session_state['updated_df '] = ''

config = {
    'question' : st.column_config.TextColumn('Question'),
    'answer' : st.column_config.TextColumn('Answer', width='large'),
}

st.session_state["updated_df"] = st.data_editor(st.session_state["initial_df"], key="qna_list", column_config=config)

# st.write("st.session_state['initial_df']: ",st.session_state['initial_df'])
# st.write("st.session_state['updated_df']: ",st.session_state['updated_df'])

if st.button("Update Knowledge Base"):

    edited_rows = st.session_state["qna_list"]["edited_rows"]


    # update knowledge base
    if len(edited_rows)>0:

        # update each edited row
        for row_num in list(st.session_state["qna_list"]["edited_rows"].keys()):
            row_to_update = st.session_state['updated_df'][row_num]
            
        
            # update document
            kb.add_answer_to_question(question=row_to_update['question'], answer=row_to_update['answer'])

            # generate a new qna document and update kb
            kb.update_qna_document(index_name="fyp-sc1015-without-faqs")

    

