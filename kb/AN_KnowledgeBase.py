from langchain_openai import AzureOpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, CSVLoader
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)
import os
from langchain.text_splitter import CharacterTextSplitter
from azure.search.documents import SearchClient
import uuid
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
import pprint
from kb.utils import load_document

# Load environment variables from the .env file
load_dotenv()


class KnowledgeBaseManager:
    def __init__(self):

        # Defines the instance of AzureOpenAIEmbedding class
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.environ.get("TEXT_EMBEDDING_MODEL_DEPLOYMENT"),
            api_key=os.environ.get("AZURE_OPENAI_APIKEY"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            model=os.environ.get("TEXT_EMBEDDING_MODEL_NAME"),
        )

        # Finds the dimension of the embedding model
        sample_text = "Embeddings dimension finder"
        embedding_vector = self.embeddings.embed_query(sample_text)
        self.embedding_dimension = len(embedding_vector)

        # Defines instance of CharacterTextSplitter class with chunk size of 1500 and chunk overlap of 500
        self.text_splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=500)


    def create_index(self, index_name):  # for course
        try:
            # Defines instance of SearchIndexClient class
            search_index_client = SearchIndexClient(
                os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
                AzureKeyCredential(os.environ.get("AZURE_AI_SEARCH_API_KEY")),
            )

            # Defines the structure of the search index
            # TODO: adjust this?
            fields = [
                # Used for basic indexing
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True,
                    retrievable=True,
                    stored=True,
                    sortable=False,
                    facetable=False,
                ),
                # Used for complex search features
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=False,
                    retrievable=True,
                    stored=True,
                    sortable=False,
                    facetable=False,
                ),
                # Used for complex search features and has more flexibility than SearchableField
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=self.embedding_dimension,
                    vector_search_profile_name="my-vector-config",
                ),
                SearchableField(
                    name="filename",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    sortable=True,
                ),
            ]

            # Setting up vector search configuration
            vector_search = VectorSearch(
                profiles=[
                    VectorSearchProfile(
                        name="my-vector-config",
                        algorithm_configuration_name="my-algorithms-config",
                    )
                ],
                algorithms=[HnswAlgorithmConfiguration(name="my-algorithms-config")],
            )

            searchindex = SearchIndex(
                name=index_name, fields=fields, vector_search=vector_search
            )
            search_index_client.create_or_update_index(index=searchindex)

            # Update class attribute
            self.index_name = index_name
            return index_name
        except Exception as e:
            return e

    def add_or_update_docs(self, documents, index_name):
        try:
            search_client = SearchClient(
                endpoint=os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
                index_name=index_name,
                credential=AzureKeyCredential(
                    os.environ.get("AZURE_AI_SEARCH_API_KEY")
                ),
            )

            # List to store all the docs that need to be added
            docs_to_add_final = []

            # List to store all the docs that need to be updated
            docs_to_update_final = []

            # Loop to separate the docs that need to be updated from the docs that need to be added
            for doc in documents:
                filename = Path(doc.metadata["source"]).name

                # check if document already exists
                search_results = list(
                    search_client.search(filter=f"filename eq '{filename}'")
                )

                split_docs = self.text_splitter.split_documents([doc])
                

                if search_results:

                    docs_to_update_id = [result["id"] for result in search_results]
                    docs_to_update_page_content = [
                        sdoc.page_content for sdoc in split_docs
                    ]  # ["Hello", "There"]
                    docs_to_update_embeddings = self.embeddings.embed_documents(
                        docs_to_update_page_content
                    )  # [[0.001,0.003], [0.002, 0.005]]
                    num_existing_docs = len(search_results)

                     
                    for i, sdoc in enumerate(split_docs[:num_existing_docs]):
                        docs_to_update_final.append(
                            {
                                "id": docs_to_update_id[i],
                                "content": sdoc.page_content,
                                "content_vector": docs_to_update_embeddings[i],
                                "filename": filename,
                            }
                        )

                    # if updated document requires more chunks of docs to be stored, add them
                    if len(split_docs) > num_existing_docs:

                        for i, sdoc in enumerate(split_docs[num_existing_docs:]):

                            docs_to_add_final.append(
                                {
                                    "id": str(uuid.uuid4()),
                                    "content": sdoc.page_content,
                                    "content_vector": docs_to_update_embeddings[i+num_existing_docs],
                                    "filename": filename,
                                }
                            )

                    print(f"updated {filename}!")
                else:
                    docs_to_add_page_content = [
                        sdoc.page_content for sdoc in split_docs
                    ]
                    docs_to_add_embeddings = self.embeddings.embed_documents(
                        docs_to_add_page_content
                    )

                    for i, sdoc in enumerate(split_docs):
                        docs_to_add_final.append(
                            {
                                "id": str(uuid.uuid4()),
                                "content": sdoc.page_content,
                                "content_vector": docs_to_add_embeddings[i],
                                "filename": filename,
                            }
                        )

                    print(f"added {filename}!")

            if docs_to_update_final:
                search_client.merge_documents(docs_to_update_final)

            if docs_to_add_final:
                search_client.upload_documents(docs_to_add_final)

            return True

        except Exception as e:
            print(f"An error occurred: {e}")
            return e

    def delete_embeddings_function(self, fileName, index_name):
        search_client = SearchClient(
            endpoint=os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
            index_name=index_name,
            credential=AzureKeyCredential(os.environ.get("AZURE_AI_SEARCH_API_KEY")),
        )
        try:
            print(fileName)

            # Search for all the docs/chunks with that particular fileName
            search_result = search_client.search(filter=f"filename eq '{fileName}'")
            ids_to_delete = []
            for result in search_result:
                # Extract the doc's id
                print(result["id"])
                ids_to_delete.append({"id": result["id"]})

            if len(ids_to_delete) != 0:
                search_client.delete_documents(ids_to_delete)

            return True

        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def delete_index_function(self, index_name):
        search_index_client = SearchIndexClient(
            os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
            AzureKeyCredential(os.environ.get("AZURE_AI_SEARCH_API_KEY")),
        )
        try:
            search_index_client.delete_index(index_name)
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def update_qna_document(self, question, answer, index_name):
    
        # content to add to document
        content = f"\n\nQuestion: {question}\nAnswer: {answer}"

        # write to document
        # temporary solution -> write to a local txt file and upload the local txt file
        # TODO: think of a better storage method
        f = open(self.qna_document, "a")
        f.write(content)
        f.close()

        # add to index
        # temporary solution -> upload updated txt file
        doc = load_document(self.qna_document)
        kb.add_or_update_docs(documents=[doc], index_name=index_name)


if __name__ == "__main__":
    kb = KnowledgeBaseManager()
    new_index_name = "fyp-sc1015-without-faqs"

    # # creating index
    # kb.create_index(
    #     index_name= new_index_name
    # )

    # adding documents into ai search storage
    documents = []
    directory_path = "/Users/bern/Documents/FYP/[CONFIDENTIAL] Chatlog and test documents/sc1015_documents/Without FAQS/"
    for file_name in os.listdir(directory_path):
        if not file_name.startswith(("~",".")):
            print("at ", directory_path+file_name)
            doc = load_document(directory_path+file_name)
            documents.append(doc)

    kb.add_or_update_docs(documents=documents, index_name=new_index_name)

    # # query index
    # # Defines retriever used
    # search_client = SearchClient(
    #     endpoint=os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
    #     index_name="fyp-sc1015",
    #     credential=AzureKeyCredential(os.environ.get("AZURE_AI_SEARCH_API_KEY")),
    # )

    # query = "What is happening at each academic week?"
    # documents = list(search_client.search(query))
    # contexts = []
    # sources = []
    # for doc in documents[:3]:
    #     pprint.pprint(doc)
    #     print("-------")
    #     # contexts.append(doc["content"])
    #     # sources.append(doc["filename"])
    #     # print(
    #     #     f"=====Retriever Info======\nCONTEXTS: {contexts}\nSOURCES {sources}"
    #     # )
