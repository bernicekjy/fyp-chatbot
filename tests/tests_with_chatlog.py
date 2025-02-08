import json
from chatbot.Narelle import Narelle
import pprint
import pandas as pd
import json
import os
from utils.logger import get_logger

# import logger
logger = get_logger(__name__)

# Function to take in a json object and print in JSON-structured format
def print_json(data, indent=2):
    output = json.dumps(data, indent=indent)
    print(output)

def import_chatlog(chatlog_file="/Users/bern/Documents/FYP/[CONFIDENTIAL] Chatlog and test documents/chatlog/chatlog.json") -> dict:
    with open(chatlog_file, 'r') as f:
        chatlog = json.load(f)

    return chatlog

def test_with_chatlog():
    
    # Load chatlog conversations
    chatlog = import_chatlog()

    chatlog_conversations = chatlog["chatlog"][:3]

    # Load Ask Narelle chatbot
    chatbot = Narelle()

    # Initialize results list
    results = []

    # Loop through chatlog conversations
    for i, conversation in enumerate(chatlog_conversations):
        logger.info("Processing conversation "+ str(i+1))

        id = conversation["_id"]['$oid']

        message_counter = 1

        for message in conversation["messages"]:

            # Generate chatbot response for each user message
            if message["role"]=="user":
                # output user's query
                query = message["content"]
                result = chatbot.answer_this(query=query)
                
                result.update({"query":query, "message_order": message_counter, "conversation_id":id})

                # update message counter
                message_counter+=1
                
                results.append(result)
        
        # clear chat history after conversation ends
        chatbot.clear_chat_history()
    
    # Save results to json file
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # convert results to dataframe
    df = pd.DataFrame(data=results)

    # reorder columns
    ordered_columns = ['conversation_id', 'message_order', 'query','chatbot_response', 'context', 'cost', 'tokens' ]
    df = df[ordered_columns]

    # export to csv
    test_results_dir = "test_results"

    df.to_csv(path_or_buf=test_results_dir+os.sep+"basic_indexing_results.csv", index=False)

test_with_chatlog()