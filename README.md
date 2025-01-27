# Iterative Learning with AskNarelle 🙋🏻‍♀️ 🧠 ✨

## Overview
This repository consists of two main components:

1. **`knowledge_base_manager` Python Library**: A reusable library that provides functionality for managing knowledge bases, including QnA management and integrations with Azure AI Search and OpenAI models.
2. **Sample Application**: A Streamlit-based application demonstrating how to use the library in two interfaces:
   - **Admin Frontend**: Allows admins to manage the list of questions and answers.
   - **Chatbot Frontend**: Provides a user-facing chatbot interface that leverages the knowledge base.

The `AN_KnowledgeBase.py` file in the `chatbot` module provides an example of how to use the library's functionality.

---

## Setup Instructions

### 1. Prerequisites
- Python 3.13+
- Poetry (for managing dependencies)
- Streamlit

### 2. Cloning the Repository
```bash
git clone https://github.com/bernicekjy/fyp-chatbot.git
```

### 3. Setting up the Environment

#### Install Dependencies
Use Poetry to install all dependencies:
```bash
poetry install
```

#### Setting Up the `.env` File
Create a `.env` file in the root directory of the project with the following structure:

```env
# Azure CosmosDB Connection String
AZURE_COSMOSDB_CONNECTION_STR="<your_cosmosdb_connection_string>"

# Azure AI Search Configuration
AZURE_AI_SEARCH_ENDPOINT="<your_ai_search_endpoint>"
AZURE_AI_SEARCH_API_KEY="<your_ai_search_api_key>"
AZURE_AI_SEARCH_INDEX_NAME="<your_ai_search_index_name>"

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT="<your_openai_endpoint>"
AZURE_OPENAI_APIKEY="<your_openai_api_key>"
AZURE_OPENAI_DEPLOYMENT_NAME="<your_openai_deployment_name>"
AZURE_OPENAI_MODEL_NAME="<your_openai_model_name>"
AZURE_OPENAI_API_VERSION="<your_openai_api_version>"

# Text Embedding Model Deployment
TEXT_EMBEDDING_MODEL_DEPLOYMENT="<your_text_embedding_model_deployment>"
TEXT_EMBEDDING_MODEL_NAME="<your_text_embedding_model_name>"
```

Replace `<your_value>` with the appropriate values for your Azure services.

---

## Running the Application

### 1. Admin Frontend
To start the admin frontend for managing the knowledge base, navigate to the `app/admin-homepage` directory and run:

```bash
streamlit run AdminHome.py
```

### 2. Chatbot Frontend
To start the chatbot frontend for interacting with users, navigate to the `app/chatbot-homepage` directory and run:

```bash
streamlit run Home.py
```

---

## Using the `knowledge_base_manager` Library

The `AN_KnowledgeBase.py` file in the `chatbot` module provides an example of how to use the library's functionality. Below is a brief overview:

### Example Code
```python
import os
from knowledge_base_manager.core.database_manager import DatabaseManager
from knowledge_base_manager.core.qna_manager import QnAManager
from knowledge_base_manager.core.knowledge_base_manager import KnowledgeBaseManager
from azure.search.documents import SearchClient
from azure.search.documents.models import SearchOptions
from azure.core.credentials import AzureKeyCredential
from langchain.chat_models import AzureChatOpenAI

# Defines database manager with QnAs
qna_db_manager = DatabaseManager(
    db_connection_str=os.environ.get("AZURE_COSMOSDB_CONNECTION_STR"),
    db_name="qnaDatabase",
    collection_name="questions"
)

# Defines QnA kb manager
qna_manager = QnAManager(qna_db_manager)

# Defines chatbot kb manager
kb_manager = KnowledgeBaseManager(
    text_embedding_azure_deployment=os.environ.get("TEXT_EMBEDDING_MODEL_DEPLOYMENT"),
    azure_openai_api_key=os.environ.get("AZURE_OPENAI_APIKEY"),
    azure_openai_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    text_embedding_model=os.environ.get("TEXT_EMBEDDING_MODEL_NAME"),
    azure_ai_search_endpoint=os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
    azure_ai_search_api_key=os.environ.get("AZURE_AI_SEARCH_API_KEY"),
    index_name=os.environ.get("AZURE_AI_SEARCH_INDEX_NAME")
)
)
```

