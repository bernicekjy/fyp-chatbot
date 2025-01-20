from langchain.embeddings import AzureOpenAIEmbeddings
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
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)
import os
from langchain.text_splitter import CharacterTextSplitter
from azure.search.documents import SearchClient
import uuid
from pathlib import Path
from dotenv import load_dotenv
from knowledge_base_manager.utils.document_loaders import load_document, strings_to_documents
from knowledge_base_manager.core.qna_manager import QnAManager

# Load environment variables from the .env file
load_dotenv()

class KnowledgeBaseManager:
    def __init__(self, text_embedding_azure_deployment:str, azure_openai_api_key:str, azure_openai_endpoint:str, text_embedding_model:str,   azure_ai_search_endpoint:str, azure_ai_search_api_key:str, index_name:str):

        # Define chunk size and overlap for splitting text
        chunk_size = 1024
        chunk_overlap = 500

        # Defines the instance of AzureOpenAIEmbedding class
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=text_embedding_azure_deployment,
            openai_api_key=azure_openai_api_key,
            azure_endpoint=azure_openai_endpoint,
            model=text_embedding_model,
            chunk_size=chunk_size,
        )

        # Defines instance of SearchIndexClient class
        self.search_index_client = SearchIndexClient(
                endpoint=azure_ai_search_endpoint,
                credential=azure_ai_search_api_key,
            )
        
        # # Defines the instance of AzureOpenAIEmbedding class
        # self.embeddings = AzureOpenAIEmbeddings(
        #     azure_deployment=os.environ.get("TEXT_EMBEDDING_MODEL_DEPLOYMENT"),
        #     openai_api_key=os.environ.get("AZURE_OPENAI_APIKEY"),
        #     azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        #     model=os.environ.get("TEXT_EMBEDDING_MODEL_NAME"),
        #     chunk_size=chunk_size,
        # )

        # # Defines instance of SearchIndexClient class
        # self.search_index_client = SearchIndexClient(
        #         endpoint=os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
        #         credential=AzureKeyCredential(os.environ.get("AZURE_AI_SEARCH_API_KEY")),
        #     )

        # create SearchClient for search function
        self.search_client = SearchClient(endpoint=azure_ai_search_endpoint,
                credential=azure_ai_search_api_key,index_name=index_name)
        
        # Find the dimension of the embedding model
        sample_text = "Embeddings dimension finder"
        embedding_vector = self.embeddings.embed_query(sample_text)
        self.embedding_dimension = len(embedding_vector)

        # Define instance of CharacterTextSplitter class with chunk size of 1500 and chunk overlap of 500
        self.text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


    def create_index(self):  # for course
        try:  

            # Defines the structure of the search index
            fields = [
                # Used for basic indexing
                SearchableField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True,
                    retrievable=True,
                    stored=True,
                    sortable=False,
                    facetable=False,
                    analyzer_name="keyword"
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
                    name="title",
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
                name=self.index_name, fields=fields, vector_search=vector_search
            )

            # Creates the new search index or updates it if it already exists
            self.search_index_client.create_or_update_index(index=searchindex)


            return self.index_name
        except Exception as e:
            return e

    def add_or_update_docs(self, documents):
        
        try:
            # List to store all the docs that need to be added
            docs_to_add_final = []

            # List to store all the docs that need to be updated
            docs_to_update_final = []

            # Loop to separate the docs that need to be updated from the docs that need to be added
            for doc in documents:
                filename = Path(doc.metadata["source"]).name


                # check if document already exists
                search_results = list(
                    self.search_client.search(filter=f"title eq '{filename}'")
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
                                "title": filename,
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
                                    "title": filename,
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
                                "title": filename,
                            }
                        )

                    print(f"added {filename}!")

            if docs_to_update_final:
                self.search_client.merge_documents(docs_to_update_final)

            if docs_to_add_final:
                self.search_client.upload_documents(docs_to_add_final)

            return True

        except Exception as e:
            print(f"An error occurred: {e}")
            return e
    
    def add_or_update_from_strings(self, strings):
        # Transform strings into documents
        documents = strings_to_documents(strings)

        return self.add_or_update_docs(documents, self.index_name)

    
    def fetch_and_index_cosmosdb_data(self, qna_manager:QnAManager):
        try:
            # Fetch all data from Azure CosmosDB
            qna_list_str = qna_manager.generate_qna_string()

            self.add_or_update_from_strings(strings=[qna_list_str], index_name=self.index_name)

            return True
        except Exception as e:
            print(f"Failed to index data: {e}")

            return False

    def delete_embeddings_function(self, fileName):

        try:
            print(fileName)

            # Search for all the docs/chunks with that particular fileName
            search_result = self.search_index_client.search(filter=f"filename eq '{fileName}'")
            ids_to_delete = []
            for result in search_result:
                # Extract the doc's id
                print(result["id"])
                ids_to_delete.append({"id": result["id"]})

            if len(ids_to_delete) != 0:
                self.search_index_client.delete_documents(ids_to_delete)

            return True

        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def delete_index_function(self):
        try:
            self.search_index_client.delete_index(self.index_name)
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False



if __name__ == "__main__":
    kb = KnowledgeBaseManager()
    new_index_name = "fyp-sc1015-without-faqs"

    # adding documents into ai search storage
    documents = []
    directory_path = "/Users/bern/Documents/FYP/[CONFIDENTIAL] Chatlog and test documents/sc1015_documents/Without FAQS/"
    for file_name in os.listdir(directory_path):
        if not file_name.startswith(("~",".")):
            print("at ", directory_path+file_name)
            doc = load_document(directory_path+file_name)
            documents.append(doc)

    kb.add_or_update_docs(documents=documents, index_name=new_index_name)

    

