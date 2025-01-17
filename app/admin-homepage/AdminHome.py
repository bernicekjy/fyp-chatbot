import streamlit as st
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from rl_knowledge_base_manager.core.database_manager import DatabaseManager
from rl_knowledge_base_manager.core.qna_manager import QnAManager
from src.kb.AN_KnowledgeBase import KnowledgeBaseManager
# # Load environment variables from the .env file
# load_dotenv()

# Set up page
st.set_page_config(
    page_title="AskNarelle - Course Coordinator Page", page_icon="🙋", layout='wide'
)
st.title(":woman-raising-hand: AN Admin")
st.write(f"For answering non-trivial queries related to {os.environ.get('COURSE_NAME')}")

# Defines database manager with QnAs
qna_db_manager = DatabaseManager(
    db_connection_str=os.environ.get("AZURE_COSMOSDB_CONNECTION_STR"),
    db_name = "qnaDatabase",
    collection_name = "questions")

# Defines QnA kb manager
qna_manager = QnAManager(qna_db_manager)

# Defines chatbot kb manager
kb = KnowledgeBaseManager()

# define columns config
columns_config = {
    'question' : st.column_config.TextColumn('Question'),
    'answer' : st.column_config.TextColumn('Answer', width='large'),
    'status' : st.column_config.TextColumn('Status'),
}

# define column order
column_order = ("question", "answer", "status")

# define tabs on UI
tab1, tab2, tab3 = st.tabs(["Unanswered Questions", "QnA Knowledge Base", "All questions"])

with tab1:
    st.session_state['initial_df'] = qna_manager.get_unanswered_questions()

    if 'updated_df ' not in st.session_state:
        st.session_state['updated_df '] = ''

    st.session_state["updated_df"] = st.data_editor(st.session_state["initial_df"], key="unanswered_qna_list", column_config=columns_config, column_order=column_order)

    # Configure "Update Knowledge Base" button
    if st.button("Update Knowledge Base"):

        edited_rows = st.session_state["unanswered_qna_list"]["edited_rows"]

        # update knowledge base
        if len(edited_rows)>0:

            # update each edited row
            for row_num in list(edited_rows.keys()):
                row_to_update = st.session_state['updated_df'][row_num]
            
                # update document
                qna_manager.add_answer_to_question(question=row_to_update['question'], answer=row_to_update['answer'])

                # generate a new qna document and update kb
                kb.fetch_and_index_cosmosdb_data(index_name="fyp-test", qna_manager=qna_manager)

            # show success message
            st.success(f"Successfully updated the knowledge base with {len(edited_rows)} new entries!")
        else:
            st.warning("No changes detected. Please edit a question to update the knowledge base.")

                

with tab2:
    st.session_state['initial_df'] = qna_manager.get_answered_questions()

    if 'updated_df ' not in st.session_state:
        st.session_state['updated_df '] = ''

    st.session_state["updated_df"] = st.data_editor(st.session_state["initial_df"], key="qna_kb_list", column_config=columns_config)

with tab3:
    st.session_state['initial_df'] = qna_manager.get_all_questions()

    if 'updated_df ' not in st.session_state:
        st.session_state['updated_df '] = ''

    st.session_state["updated_df"] = st.data_editor(st.session_state["initial_df"], key="all_qna_list", column_config=columns_config)