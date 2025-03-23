import streamlit as st
import os
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from chatbot.AN_Knowledge_Base import AN_KB_Manager
import pandas as pd
# # Load environment variables from the .env file
# load_dotenv()

# Set up page
st.set_page_config(
    page_title="AskNarelle - Course Coordinator Page", page_icon="🙋", layout='wide'
)
st.title(":woman-raising-hand: Ask Narelle Admin Page")
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

# Define color formatting for the "Category" column
def category_color_formatter(category):
    if category == "ADMIN":
        return "background-color: #c6dbef; color: black;"  # light blue
    elif category == "TECHNICAL":
        return "background-color: #ffddc1; color: black;"  # light orange
    elif category == "CONTENT":
        return "background-color: #cfe9f1; color: black;"  # light cyan
    elif category == "IRRELEVANT":
        return "background-color: #f4cccc; color: black;"  # light red
    elif category == "EVALUATION":
        return "background-color: #e4d7f5; color: black;"  # light purple
    elif category == "RESOURCE":
        return "background-color: #e6cfc7; color: black;"  # light brown
    elif category == "UNCATEGORISED":
        return "background-color: #d7d7d7; color: black;"  # light grey
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


tab1, tab2 = st.tabs(["All Questions", "Relevant Questions"])

with tab1:
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
    ).map(category_color_formatter, subset=pd.IndexSlice[:, ["category"]])

    try:
        # display the DataFrame
        display_df = st.data_editor(
                        styled_df,  
                        key="all_qna_list",  
                        column_config=columns_config,  
                        column_order=column_order,  
                        disabled=["status", "timestamp", "category"],  # make "status" column non-editable
                        use_container_width=True,
                        hide_index=False,
                        height=600,
                        )
    except KeyError:
        st.markdown("<p style='color:grey;'>No data to display.</p>", unsafe_allow_html=True)



    # Configure "Update Knowledge Base" button
    if st.button("Update Knowledge Base", key="update_kb_1"):
        
        try:
            edited_rows = st.session_state.get("all_qna_list", {}).get("edited_rows", {})
            
            # st.write(edited_rows)

            # update knowledge base
            if len(edited_rows)>0:
                
                num_updated_entries = 0
                num_marked_irrelevant = 0

                # update each edited row
                for row_num in list(edited_rows.keys()):

                    row_to_update = display_df.iloc[int(row_num)]

                    print("row_to_update: ", row_to_update)

                    # extract the updated question and answer
                    question = row_to_update['question']
                    answer = row_to_update['answer']

                    # update answer of document
                    if row_to_update['answer']:
                        an_kb.qna_manager.add_answer_to_question(question=question, answer=answer)

                    if row_to_update['irrelevant']:
                        an_kb.qna_manager.mark_question_irrelevant(question=question)
                    else:
                        an_kb.qna_manager.mark_question_relevant(question=question)
                        print("marked qn relevant")
                    
                    if row_to_update['answer']:
                        # update document
                        an_kb.qna_manager.add_answer_to_question(question=question, answer=answer)

                # sync qna list to chatbot's knowledge base
                an_kb.sync_qna_to_kb()

                # show success message
                st.success("Successfully updated the knowledge base!")

                # # show success message
                # st.success(f"Successfully updated the knowledge base with {len(edited_rows)} new entries!")

                # Reload data to refresh the unanswered questions list
                st.session_state["qna_df"] = pd.DataFrame(an_kb.qna_manager.get_relevant_questions())
            else:
                st.warning("No changes detected. Please edit a question to update the knowledge base.")
        except Exception as e:
            st.error(f"An error occurred while attempting to update the knowledge base: {e}")
with tab2:
        # Initialise session state for df
    if 'relevant_df ' not in st.session_state:
        st.session_state["relevant_df"] = pd.DataFrame(an_kb.qna_manager.get_relevant_questions())

    # apply the color formatting to the DataFrame for the "status" column
    styled_df = st.session_state["relevant_df"].style.map(
        status_color_formatter, subset=pd.IndexSlice[:, ["status"]]
    ).map(category_color_formatter, subset=pd.IndexSlice[:, ["category"]])

    try:
        # display the DataFrame
        display_df = st.data_editor(
                        styled_df,  
                        key="relevant_qna_list",  
                        column_config=columns_config,  
                        column_order=column_order,  
                        disabled=["status", "timestamp", "category"],  # make "status" column non-editable
                        use_container_width=True,
                        hide_index=False,
                        height=600,
                        )
    except KeyError:
        st.markdown("<p style='color:grey;'>No data to display.</p>", unsafe_allow_html=True)



    # Configure "Update Knowledge Base" button
    if st.button("Update Knowledge Base", key="update_kb_2"):
        
        try:
            edited_rows = st.session_state.get("relevant_qna_list", {}).get("edited_rows", {})
            
            # update knowledge base
            if len(edited_rows)>0:
                
                num_updated_entries = 0
                num_marked_irrelevant = 0

                # update each edited row
                for row_num in list(edited_rows.keys()):

                    row_to_update = display_df.iloc[int(row_num)]

                    print("row_to_update: ", row_to_update)

                    # extract the updated question and answer
                    question = row_to_update['question']
                    answer = row_to_update['answer']

                    # update answer of document
                    if row_to_update['answer']:
                        an_kb.qna_manager.add_answer_to_question(question=question, answer=answer)

                    if row_to_update['irrelevant']:
                        an_kb.qna_manager.mark_question_irrelevant(question=question)
                    else:
                        an_kb.qna_manager.mark_question_relevant(question=question)
                        print("marked qn relevant")
                    
                    if row_to_update['answer']:
                        # update document
                        an_kb.qna_manager.add_answer_to_question(question=question, answer=answer)

                # sync qna list to chatbot's knowledge base
                an_kb.sync_qna_to_kb()

                # show success message
                st.success("Successfully updated the knowledge base!")

                # # show success message
                # st.success(f"Successfully updated the knowledge base with {len(edited_rows)} new entries!")

                # Reload data to refresh the unanswered questions list
                st.session_state["qna_df"] = pd.DataFrame(an_kb.qna_manager.get_relevant_questions())
            else:
                st.warning("No changes detected. Please edit a question to update the knowledge base.")
        except Exception as e:
            st.error(f"An error occurred while attempting to update the knowledge base: {e}")

with st.sidebar:
    try:
        st.header("Question Status")
        st.write(st.session_state["qna_df"]['status'].value_counts())

        st.header("Question Categories")
        st.write(st.session_state["qna_df"]['category'].value_counts())
    except KeyError:
        st.markdown("<p style='color:grey;'>No data to display.</p>", unsafe_allow_html=True)