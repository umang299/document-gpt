"""
ChromaDB Chat - A module for interacting with ChromaDB to perform chat-based
retrieval.

This module provides functions for interacting with ChromaDB to perform
chat-based retrieval.
It allows you to query the database for responses to user messages and upload
new data to the database.

Args:
    client (ChromaDBClient): An instance of the ChromaDBClient for database
                             interaction.
    message (str): The user's message for which a response is requested.
    file_path (str): The path to the data file to be uploaded to the database.

Functions:
    get_response(client, message): Retrieve a response from ChromaDB based on
                                   the user's message.
    upload(client, file_path): Upload data from a file to the ChromaDB
                               database.

Example Usage:
    client = ChromaDBClient(openai_api_key='your_openai_api_key')
    message = "Tell me about ChromaDB"
    response = get_response(client=client, message=message)
    print(f"Response: {response}")

    file_path = 'data.json'
    upload(client=client, file_path=file_path)
"""

import os
import time
import chromadb

from llama_index.vector_stores import ChromaVectorStore
from llama_index import VectorStoreIndex, ServiceContext
from src.utils import upsert, logger, load_conversation

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


def get_response(client, message):
    """
    Retrieve a response from ChromaDB based on the user's message.

    Args:
        client (ChromaDBClient): An instance of the ChromaDBClient for
                                 database interaction.
        message (str): The user's message for which a response is requested.

    Returns:
        str: The response generated by ChromaDB.
    """
    start = time.time()
    conversation, conv_dur = load_conversation(top_n=10)
    collection, col_dur = client.get_collection(collection_name='database')
    vector_store = ChromaVectorStore(chroma_collection=collection)
    service_context = ServiceContext.from_defaults(
                                chunk_size=512, chunk_overlap=25
                                )

    index = VectorStoreIndex.from_vector_store(
                            vector_store,
                            service_context=service_context,
                        )

    chat_engine = index.as_chat_engine()
    logger(message=message, role='user')

    agent_response = chat_engine.chat(
                            message=message,
                            chat_history=conversation
                        )
    end = time.time()
    logger(message=agent_response.response, role='assistant')

    dur = (end - start)
    return {
            'response': agent_response.response,
            'duration': {
                        'time': dur,
                        'conv_dur': conv_dur,
                        'col_dur': col_dur
                        }
            }


def upload(client, file_path):
    """
    Upload data from a file to the ChromaDB database.

    Args:
        client (ChromaDBClient): An instance of the ChromaDBClient for
                                 database interaction.
        file_path (str): The path to the data file to be uploaded to the
                         database.
    Returns:
        None
    """
    start = time.time()
    collection = client.get_collection('database')
    nodes = client.load_data(file_path)
    upsert(collection=collection, nodes=nodes)

    storage_path = os.path.join(cwd, 'storage')
    chromadb.PersistentClient(path=storage_path)
    end = time.time()

    dur = end - start
    return dur
