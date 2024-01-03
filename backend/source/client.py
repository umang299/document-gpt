import os
from uuid import uuid4

import chromadb
from chromadb.utils import embedding_functions

from llama_index import SimpleDirectoryReader
from llama_index.node_parser import TokenTextSplitter
from llama_index.vector_stores import ChromaVectorStore
from llama_index import VectorStoreIndex, ServiceContext

from .config import DB_DIR, DATA_DIR, CONFIG_PATH
from .utils import load_yaml_file, load_conversation, conversation_logger

client = chromadb.PersistentClient(path=DB_DIR)
openai_api_key = os.environ['OPENAI_API_KEY']


def embedding_model():
    model = embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_api_key,
        model_name='text-embedding-ada-002'
    )
    return model


def list_collections():
    collections = client.list_collections()
    return [col.name for col in collections]


def get_collection(collection_name):
    try:
        collection = client.get_collection(
                            name=collection_name,
                            embedding_function=embedding_model()
                        )
        return collection
    except ValueError as e:
        print(e)
        return False


def create_collection(collection_name):
    list_collection = list_collections()
    if collection_name not in list_collection:
        collection = client.create_collection(
                        name=collection_name,
                        embedding_function=embedding_model()
                    )
    else:
        collection = client.get_collection(
                        name=collection_name
                    )
    return collection


def delete_collection(collection_name):
    client.delete_collection(name=collection_name)


def upload(collection_name, text):
    file_path = os.path.join(DATA_DIR, f'{uuid4()}.txt')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)

    collection = client.get_collection(
                    name=collection_name,
                    embedding_function=embedding_model()
                )

    documents = SimpleDirectoryReader(
                    input_files=[file_path],
                ).load_data()

    splitter = TokenTextSplitter(
                    chunk_size=512,
                    chunk_overlap=25,
                    separator='.',
                    include_metadata=True
                )

    nodes = splitter.get_nodes_from_documents(
                    documents=documents
                )
    for node in nodes:
        hash = node.hash
        content = node.text

        if content != '':
            content_metadata = {
                'id': hash,
                'Page_Text': content
            }

            collection.add(
                documents=[content],
                metadatas=[content_metadata],
                ids=[str(id)]
            )

    return True


def response(collection_name: str, message: str):
    collection = get_collection(
                            collection_name=collection_name,
                        )

    config = load_yaml_file(filename=CONFIG_PATH)
    chat_history = load_conversation()
    vector_store = ChromaVectorStore(chroma_collection=collection)
    service_context = ServiceContext.from_defaults(
                            chunk_size=config['CHUNK_SIZE'],
                            chunk_overlap=config['CHUNK_OVERLAP']
                        )

    index = VectorStoreIndex.from_vector_store(
                            vector_store,
                            service_context=service_context,
                        )

    chat_engine = index.as_chat_engine()
    conversation_logger(message=message, role='user')
    response = chat_engine.chat(
                            message=message,
                            chat_history=chat_history
                        )
    conversation_logger(message=response.response, role='assistant')
    return response.response
