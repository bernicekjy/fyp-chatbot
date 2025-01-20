import streamlit as st
import os
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from knowledge_base_manager.core.database_manager import DatabaseManager
from knowledge_base_manager.core.qna_manager import QnAManager
from knowledge_base_manager.core.knowledge_base_manager import KnowledgeBaseManager
from chatbot.AN_Knowledge_Base import AN_KB_Manager
# # Load environment variables from the .env file
# load_dotenv()

# Set up page
st.set_page_config(
    page_title="AskNarelle - Course Coordinator Page", page_icon="🙋", layout='wide'
)
st.title(":woman-raising-hand: AN Admin")
st.write(f"For answering non-trivial queries related to {os.environ.get('COURSE_NAME')}")


# Get Ask Narelle's knowledge base manager
an_kb = AN_KB_Manager()

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
    st.session_state['initial_df'] = an_kb.qna_manager.get_unanswered_questions()

    if 'updated_df ' not in st.session_state:
        st.session_state['updated_df '] = ''

    st.session_state["updated_df"] = st.data_editor(st.session_state["initial_df"], key="unanswered_qna_list", column_config=columns_config, column_order=column_order)

    # Configure "Update Knowledge Base" button
    if st.button("Update Knowledge Base"):

        try:
            edited_rows = st.session_state["unanswered_qna_list"]["edited_rows"]

            # update knowledge base
            if len(edited_rows)>0:

                # update each edited row
                for row_num in list(edited_rows.keys()):
                    row_to_update = st.session_state['updated_df'][row_num]
                
                    # update document
                    an_kb.qna_manager.add_answer_to_question(question=row_to_update['question'], answer=row_to_update['answer'])

                    # sync qna list to chatbot's knowledge base
                    an_kb.sync_qna_to_kb()

                # show success message
                st.success(f"Successfully updated the knowledge base with {len(edited_rows)} new entries!")
            else:
                st.warning("No changes detected. Please edit a question to update the knowledge base.")
        except Exception as e:
            st.error(f"An error occurred while attempting to update the knowledge base: {e}")
                

with tab2:
    st.session_state['initial_df'] = an_kb.qna_manager.get_answered_questions()

    if 'updated_df ' not in st.session_state:
        st.session_state['updated_df '] = ''

    st.session_state["updated_df"] = st.data_editor(st.session_state["initial_df"], key="qna_kb_list", column_config=columns_config)

with tab3:
    st.session_state['initial_df'] = an_kb.qna_manager.get_all_questions()

    if 'updated_df ' not in st.session_state:
        st.session_state['updated_df '] = ''

    st.session_state["updated_df"] = st.data_editor(st.session_state["initial_df"], key="all_qna_list", column_config=columns_config)