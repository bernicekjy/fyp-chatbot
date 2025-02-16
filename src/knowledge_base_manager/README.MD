# Knowledge Base Manager Library

## Overview

The `knowledge_base_manager` Python library provides functionality for managing knowledge bases, including QnA management and integrations with Azure AI Search and OpenAI models. This library is designed to be reusable and can be integrated into various applications.

## Features

- **QnA Management 🤝**: Manage questions and answers in a structured format.
- **Azure AI Search Integration 🧠**: Utilize Azure AI Search for indexing and searching documents.
- **OpenAI Integration 💬**: Leverage OpenAI models for text embedding and other NLP tasks.

## Installation

To install the required dependencies, use Poetry:

```bash
poetry install
```

## Setup

Ensure you have the following environment variables set up in your `.env` file:

```env
# OpenAI Service Configuration
AZURE_OPENAI_ENDPOINT=<your-azure-openai-endpoint>
AZURE_OPENAI_APIKEY=<your-azure-openai-apikey>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-azure-openai-deployment-name>
AZURE_OPENAI_MODEL_NAME=<your-azure-openai-model-name>
AZURE_OPENAI_API_VERSION=<your-azure-openai-api-version>

# Azure AI Search Service Configuration
AZURE_AI_SEARCH_ENDPOINT=<your-azure-ai-search-endpoint>
AZURE_AI_SEARCH_API_KEY=<your-azure-ai-search-api-key>

# Azure Cosmos DB Configuration
AZURE_COSMOSDB_CONNECTION_STR=<your-azure-cosmosdb-connection-str>

# Text Embedding Model Configuration
TEXT_EMBEDDING_MODEL_DEPLOYMENT=<your-text-embedding-model-deployment>
TEXT_EMBEDDING_MODEL_NAME=<your-text-embedding-model-name>
```

## Usage

### Initializing the Knowledge Base Manager

```python
import os
from knowledge_base_manager.core.database_manager import DatabaseManager
from knowledge_base_manager.core.qna_manager import QnAManager
from knowledge_base_manager.core.knowledge_base_manager import KnowledgeBaseManager

# Initialize the database manager
qna_db_manager = DatabaseManager(
    db_connection_str=os.environ.get("AZURE_COSMOSDB_CONNECTION_STR"),
    db_name="qnaDatabase",
    collection_name="questions"
)

# Initialize the QnA manager
qna_manager = QnAManager(qna_db_manager)

# Initialize the knowledge base manager
kb_manager = KnowledgeBaseManager(
    azure_text_embedding_config={
        "azure_deployment": os.environ.get("TEXT_EMBEDDING_MODEL_DEPLOYMENT"),
        "api_key": os.environ.get("AZURE_OPENAI_APIKEY"),
        "endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        "model": os.environ.get("TEXT_EMBEDDING_MODEL_NAME")
    },
    azure_ai_search_config={
        "endpoint": os.environ.get("AZURE_AI_SEARCH_ENDPOINT"),
        "api_key": os.environ.get("AZURE_AI_SEARCH_API_KEY")
    },
    index_name="your-index-name"
)
```

### Adding Documents

```python
documents = [
    {"id": "1", "content": "What is the course schedule?"},
    {"id": "2", "content": "How do I submit assignments?"}
]

kb_manager.add_or_update_docs(documents)
```

### Fetching and Indexing Data

```python
kb_manager.fetch_and_index_cosmosdb_data(qna_manager=qna_manager)
```

### Deleting Documents

```python
kb_manager.delete_embeddings_function(fileName="document_id")
```


### Using QnAManager

#### Adding Unanswered Questions

```python
# Add an unanswered question to the database
qna_manager.add_unanswered_question("What is the course duration?")
```

#### Adding Answers to Questions

```python
# Add an answer to an existing question in the database
qna_manager.add_answer_to_question(
    question="What is the course duration?",
    answer="The course duration is 10 weeks."
)
```

#### Marking Questions as Irrelevant

```python
# Mark a question as irrelevant
qna_manager.mark_question_irrelevant("What is the course duration?")
```

#### Fetching All Questions

```python
# Retrieve all questions from the database
all_questions = qna_manager.get_all_questions()
```

#### Fetching Relevant Questions

```python
# Retrieve all relevant questions from the database
relevant_questions = qna_manager.get_relevant_questions()
```

#### Fetching Answered Questions

```python
# Retrieve all answered questions from the database
answered_questions = qna_manager.get_answered_questions()
```

#### Fetching Unanswered Questions

```python
# Retrieve all unanswered questions from the database
unanswered_questions = qna_manager.get_unanswered_questions()
```
## Example Application

Refer to the `chatbot` [directory](https://github.com/bernicekjy/fyp-chatbot/tree/main/src/chatbot) at the [sample application with Ask Narelle](https://github.com/bernicekjy/fyp-chatbot) for an example that demonstrates how to use the `knowledge_base_manager` library in a Streamlit-based interface.
