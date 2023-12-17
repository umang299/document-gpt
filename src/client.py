"""
ChromaDB Client - A module for interacting with ChromaDB for
collection management and data upload.


This module provides a client class for interacting with ChromaDB, allowing
the creation, querying, and deletion of collections.
It also provides methods for loading and uploading data to the database.

Args:
    openai_api_key (str): The API key for accessing the OpenAI service.
    encoding (str, optional): The text encoding to use (default is 'utf-8').
    required_ext (list, optional): A list of required file extensions
                                   (default is ['.pdf']).

    num_files_limit (int, optional): The maximum number of files to load
                                     (default is 2).

    chunk_size (int, optional): The chunk size for text splitting
                                (default is 512).

    chunk_overlap (int, optional): The chunk overlap for text splitting
                                   (default is 25).

    host (str, optional): The hostname or IP address of the ChromaDB server
                          (default is 'localhost').
    port (int, optional): The port number for the ChromaDB server
                          (default is 8000).

Attributes:
    openai_api_key (str): The API key for accessing the OpenAI service.
    host (str): The hostname or IP address of the ChromaDB server.
    port (int): The port number for the ChromaDB server.
    text_encoding (str): The text encoding to use.
    required_exts (list): A list of required file extensions.
    num_files_limit (int): The maximum number of files to load.
    chunk_size (int): The chunk size for text splitting.
    chunk_overlap (int): The chunk overlap for text splitting.
    client (chromadb.HttpClient): An instance of the ChromaDB HTTP client for
                                  communication with ChromaDB.

Methods:
    get_collection(collection_name): Get an existing collection by name.
    create_collection(collection_name): Create a new collection or get an
                                        existing one by name.
    load_data(file_path): Load data from a file into ChromaDB.
    get_info(collection_name, n=10): Get information about a collection,
                                     including the count of items and a
                                     preview of the first 'n' items.

Example Usage:
    client = ChromaDBClient(openai_api_key='your_openai_api_key')
    my_collection = client.create_collection('my_collection')
    collection_info = client.get_info('my_collection')
"""

import os
import sys
import chromadb
from chromadb.utils import embedding_functions

from llama_index import SimpleDirectoryReader
from llama_index.node_parser import TokenTextSplitter

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(cwd)


class ChromaDBClient:
    """
    A client class for interacting with ChromaDB, responsible for creating,
    querying, and deleting collections.

    Args:
        openai_api_key (str): The API key for accessing the OpenAI service.
        encoding (str, optional): The text encoding to use (default is 'utf-8')
        required_ext (list, optional): A list of required file extensions
                                       (default is ['.pdf']).

        num_files_limit (int, optional): The maximum number of files to load
                                         (default is 2).

        chunk_size (int, optional): The chunk size for text splitting
                                    (default is 512).

        chunk_overlap (int, optional): The chunk overlap for text splitting
                                       (default is 25).

        host (str, optional): The hostname or IP address of the ChromaDB
                              server (default is 'localhost').

        port (int, optional): The port number for the ChromaDB server
                              (default is 8000).

    Methods:
        get_collection(collection_name): Get an existing collection by name.
        create_collection(collection_name): Create a new collection or get an
                                            existing one by name.
        load_data(file_path): Load data from a file into ChromaDB.
        get_info(collection_name, n=10): Get information about a collection,
                                         including the count of items and a
                                         preview of the first 'n' items.

    Example Usage:
        client = ChromaDBClient(openai_api_key='your_openai_api_key')
        my_collection = client.create_collection('my_collection')
        collection_info = client.get_info('my_collection')
    """

    def __init__(self, openai_api_key: str = None,
                 encoding: str = None,
                 required_ext: list = None,
                 num_files_limit: int = None,
                 chunk_size: int = None,
                 chunk_overlap: int = None,
                 host: str = 'localhost',
                 port: int = 8000):
        """
        Initialize the ChromaDBClient.

        Args:
            openai_api_key (str): The API key for accessing the OpenAI service.
            encoding (str, optional): The text encoding to use
                                      (default is 'utf-8').
            required_ext (list, optional): A list of required file extensions
                                           (default is ['.pdf']).
            num_files_limit (int, optional): The maximum number of files to
                                             load (default is 2).
            chunk_size (int, optional): The chunk size for text splitting
                                        (default is 512).
            chunk_overlap (int, optional): The chunk overlap for text
                                           splitting (default is 25).
            host (str, optional): The hostname or IP address of the ChromaDB
                                  server (default is 'localhost').
            port (int, optional): The port number for the ChromaDB server
                                  (default is 8000).

        Returns:
            None
        """
        self.openai_api_key = openai_api_key
        self.host = host
        self.port = port
        self.text_encoding = 'utf-8' if encoding == '' else encoding
        self.required_exts = ['.pdf'] if required_ext is [] else required_ext

        if num_files_limit is None:
            self.num_files_limit = 2
        else:
            self.num_files_limit = num_files_limit

        self.chunk_size = 512 if chunk_size is None else chunk_size
        self.chunk_overlap = 25 if chunk_overlap is None else chunk_overlap
        self.client = self.__initialize_client()

    def __initialize_client(self):
        """
        Initialize the ChromaDB HTTP client.

        Returns:
            chromadb.HttpClient: An instance of the ChromaDB HTTP client.
        """
        client = chromadb.HttpClient(
            host=self.host,
            port=self.port
        )
        return client

    def __embedding_model(self):
        """
        Create and return an OpenAI text embedding model.

        Returns:
            embedding_functions.OpenAIEmbeddingFunction: An instance of the
            OpenAI text embedding model.
        """
        model = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.openai_api_key,
            model_name="text-embedding-ada-002"
        )
        return model

    def get_collection(self, collection_name):
        """
        Get an existing collection by name.

        Args:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            chromadb.Collection: An instance of the requested collection.
        """
        collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.__embedding_model()
        )
        return collection

    def create_collection(self, collection_name):
        """
        Create a new collection or get an existing one by name.

        Args:
            collection_name (str): The name of the collection to create or
            retrieve.

        Returns:
            chromadb.Collection: An instance of the created or retrieved
            collection.
        """
        collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.__embedding_model()
        )
        return collection

    def __dataloader(self, file_path):
        loader = SimpleDirectoryReader(
                        input_files=[file_path],
                        encoding=self.text_encoding,
                        required_exts=self.required_exts,
                        num_files_limit=self.num_files_limit
                    )

        return loader

    def __node_splitter(self):
        splitter = TokenTextSplitter(
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap
                    )
        return splitter

    def load_data(self, file_path):
        """
        Load data from a file into ChromaDB.

        Args:
            file_path (str): The path to the data file to be uploaded to the
            database.

        Returns:
            list: A list of data nodes loaded into the database.
        """
        loader = self.__dataloader(file_path=file_path)
        splitter = self.__node_splitter()

        documents = loader.load_data()
        nodes = splitter.get_nodes_from_documents(documents=documents)
        return nodes

    def get_info(self, collection_name, n=10):
        """
        Get information about a collection, including the count of items and a
        preview of the first 'n' items.

        Args:
            collection_name (str): The name of the collection to query.
            n (int): The number of items to preview (default is 10).

        Returns:
            dict: A dictionary containing collection information, including
            'count' and 'items'.
        """
        collection = self.client.get_collection(
            name=collection_name,
            embedding_function=self.__embedding_model()
        )

        return {
            'count': collection.count(),
            'items': collection.peek(limit=n)
            }
