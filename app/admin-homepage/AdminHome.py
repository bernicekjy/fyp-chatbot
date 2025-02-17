import streamlit as st
import os
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from knowledge_base_manager.core.database_manager import DatabaseManager
from knowledge_base_manager.core.qna_manager import QnAManager
from knowledge_base_manager.core.knowledge_base_manager import KnowledgeBaseManager
from chatbot.AN_Knowledge_Base import AN_KB_Manager
import pandas as pd
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

# Define color formatting for the "Status" column
def status_color_formatter(status):
    if status == "Answered":
        return "background-color: #D4F5F2; color: #155724;"
    elif status =="Unanswered":
        return "background-color: #FFF3CD; color: #856404;"
    elif status == "Irrelevant":
        return "background-color: #F5D4D7; color: #721c24;" 
    return ""  # default styling

# define columns config
columns_config = {
    'question' : st.column_config.TextColumn('Question', width="large"),
    'answer' : st.column_config.TextColumn('Answer', width='large'),
    'status' : st.column_config.TextColumn('Status', width='small'),
    'timestamp' : st.column_config.DatetimeColumn('Timestamp', width='small'),
    'irrelevant': st.column_config.CheckboxColumn('Mark as irrelevant', width='small'),
    'category': st.column_config.TextColumn('Category', width='small')
}

# define column order
column_order = ("status", "timestamp","question", "answer",  "category", 'irrelevant')

# # Initialise session state for checkbox
# if "hide_irrelevant" not in st.session_state:
#     st.session_state["hide_irrelevant"] = True 

# Initialise session state for df
if 'qna_df ' not in st.session_state:
    # if st.session_state["hide_irrelevant"]:
    #     # fetch unanswered questions
    st.session_state["qna_df"] = pd.DataFrame(an_kb.qna_manager.get_all_questions())
    # else:
    #     # fetch unanswered questions
    #     st.session_state["qna_df"] = pd.DataFrame(an_kb.qna_manager.get_all_questions())

# apply the color formatting to the DataFrame for the "status" column
styled_df = st.session_state["qna_df"].style.map(
    status_color_formatter, subset=pd.IndexSlice[:, ["status"]]
)

try:
    # display the DataFrame
    display_df = st.data_editor(
                    styled_df,  
                    key="all_qna_list",  
                    column_config=columns_config,  
                    column_order=column_order,  
                    disabled=["status", "timestamp"],  # make "status" column non-editable
                    use_container_width=True,
                    hide_index=True,
                    height=700,
                    )
except KeyError:
    st.markdown("<p style='color:grey;'>No data to display.</p>", unsafe_allow_html=True)


# # Checkbox with persistent state
# hide_irrelevant = st.checkbox(
#     "Hide Irrelevant Rows", value=st.session_state["hide_irrelevant"]
# )

# # Update session state when checkbox changes
# if hide_irrelevant != st.session_state["hide_irrelevant"]:
#     st.session_state["hide_irrelevant"] = hide_irrelevant


# Configure "Update Knowledge Base" button
if st.button("Update Knowledge Base"):
    
    try:
        edited_rows = st.session_state.get("all_qna_list", {}).get("edited_rows", {})
        
        st.write(edited_rows)

        # update knowledge base
        if len(edited_rows)>0:
            
            num_updated_entries = 0
            num_marked_irrelevant = 0

            # update each edited row
            for row_num in list(edited_rows.keys()):

                row_to_update = display_df.iloc[int(row_num)]

                if row_to_update['irrelevant']:
                    # extract the updated question and answer
                    question = row_to_update['question']
                    an_kb.qna_manager.mark_question_irrelevant(question=question)
                    num_marked_irrelevant += 1
                
                if row_to_update['answer']:
                    # extract the updated question and answer
                    question = row_to_update['question']
                    answer = row_to_update['answer']
                
                    # update document
                    an_kb.qna_manager.add_answer_to_question(question=question, answer=answer)
                    num_updated_entries += 1

            # sync qna list to chatbot's knowledge base
            an_kb.sync_qna_to_kb()

            if num_updated_entries > 0:
                # show success message
                st.success(f"Successfully updated the knowledge base with {num_updated_entries} new entries!")

            if num_marked_irrelevant > 0:
                st.success(f"Marked {num_marked_irrelevant} questions as irrelevant.")
            # # show success message
            # st.success(f"Successfully updated the knowledge base with {len(edited_rows)} new entries!")

            # Reload data to refresh the unanswered questions list
            st.session_state["qna_df"] = pd.DataFrame(an_kb.qna_manager.get_relevant_questions())
        else:
            st.warning("No changes detected. Please edit a question to update the knowledge base.")
    except Exception as e:
        st.error(f"An error occurred while attempting to update the knowledge base: {e}")
