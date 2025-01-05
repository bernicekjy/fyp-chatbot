import pymongo
import sys

atlas_connection_str = "mongodb+srv://bernicekoh1110:hell0mongodb123!@fyp-chatbot-poc.fjlxl.mongodb.net/?retryWrites=true&w=majority&appName=fyp-chatbot-poc"

try:
  client = pymongo.MongoClient(atlas_connection_str)
# return a friendly error if a URI error is thrown 
except pymongo.errors.ConfigurationError:
  print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
  sys.exit(1)

# use a database named "qnaDatabase"
db = client.qnaDatabase

# use a collection named "questions"
questions_collection = db["questions"]

question_documents = [{"question": "How about in 2008?", "answer": ""}, 
{"question": "Can I email the school to ask to change this to a Pass/Fail course?", "answer": ""}, 
{"question": "Who are all the TAs in this course?", "answer": "Mr. A, Ms. B"}, 
{"question": "Is this course graded on a bellcurve", "answer": ""}]

# drop the collection in case it already exists
try:
    questions_collection.drop()

# return a friendly error if an authentication error is thrown
except pymongo.errors.OperationFailure:
  print("An authentication error was received. Are your username and password correct in your connection string?")
  sys.exit(1)

# INSERT DOCUMENTS
#
# You can insert individual documents using collection.insert_one().
# In this example, we're going to create four documents and then 
# insert them all with insert_many().

try:
    result = questions_collection.insert_many(question_documents)

# return a friendly error if the operation fails
except pymongo.errors.OperationFailure:
  print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
  sys.exit(1)

else:
    inserted_count = len(result.inserted_ids)
    print("%x documents inserted." %(inserted_count))
    print("\n")

# FIND DOCUMENTS
#
# Now that we have data in Atlas, we can read it. To retrieve all of
# the data in a collection, we call find() with an empty filter. 

result = questions_collection.find()

if result:    
  for doc in result:
    print("doc: ", doc)
    print()



    
