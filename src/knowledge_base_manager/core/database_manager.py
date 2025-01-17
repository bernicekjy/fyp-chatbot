import pymongo
from pymongo.errors import ConfigurationError, OperationFailure
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self, db_connection_str:str, db_name:str, collection_name: str):
        """Initialise DatabaseManager with MongoDB connection details.

        Args:
            db_connection_str (str): MongoDB connection string
            db_name (str): Name of the database
            collection_name (str): Name of the collection
        """

        # attempt to connect to MongoDB
        try:
            self.client = pymongo.MongoClient(db_connection_str)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        except ConfigurationError as e:
            raise ValueError("Invalid MongoDB connection string.") from e

    def initialise_collection(self):
        """Drops the collection if it already exists
        """
        try:
            self.collection.drop()
        except OperationFailure as e:
            raise PermissionError("Authentication Failed. Check your credentials.") from e

    def insert_document(self, document: Dict[str, Any])->bool:
        """Insert a single document into the collection

        Args:
            document (Dict[str, Any]): The document to insert

        Returns:
            bool: True if the operation is successful
        """
        self.collection.insert_one(document)
        
        return True

    def find_documents(self, query: Dict[str, Any]={})-> List[Dict[str, Any]]:
        """Find documents in the collection based on a query.

        e.g. result = db_manager.find_documents({"status": "unanswered"}

        Args:
            query (Dict[str, Any], optional): The query to filter documents

        Returns:
            List[Dict[str, Any]]: List of documents matching the query
        """
        return list(self.collection.find(query))

    def update_document(self, query: Dict[str, Any], update: Dict[str,Any]) -> bool:
        """Update a document in the collection based on a query

        Args:
            query (Dict[str, Any]): The query to identify the document
            update (Dict[str,Any]): The update to apply

        Returns:
            bool: True if the document is found and updated
        """
        result = self.collection.find_one_and_update(query, {"$set": update}, return_document=pymongo.ReturnDocument.AFTER)
        return result is not None

    def delete_document(self, query: Dict[str,Any]) -> int:
        """Delete a document from the collection. 

        Args:
            query (Dict[str,Any]): The query to identify the document to delete

        Returns:
            int: The number of documents deleted
        """

        result = self.collection.delete_one(query)

        return result.deleted_count

    def count_document(self, query: Dict[str, Any]={}) -> int:
        """Count the number of documents in the collection that match a query.

        Args:
            query (Dict[str, Any], optional): The query to filter document

        Returns:
            int: The number of matching documents
        """

        return self.collection.count_documents(query)

    def drop_collection(self):
        """Drop the collection entirely.
        """
        self.collection.drop()