import os
import chromadb
from chromadb.utils import embedding_functions

import llama_index
from llama_index import SimpleDirectoryReader
from llama_index.node_parser import TokenTextSplitter

from .log import logging
from .config import CONFIG_PATH
from .utils import load_yaml_file


class ChromaDBClient:
    def __init__(self,
                 encoding: str = None,
                 required_ext: list = None,
                 num_files_limit: int = None,
                 ):

        self.config = load_yaml_file(filename=CONFIG_PATH)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.host = os.getenv('HOST')
        self.port = os.getenv('PORT')

        self.text_encoding = 'utf-8' if encoding == '' else encoding
        self.required_exts = ['.pdf'] if required_ext is [] else required_ext

        if num_files_limit is None:
            self.num_files_limit = 2
        else:
            self.num_files_limit = num_files_limit

        self.client = self.__initialize_client()

    def __initialize_client(self):
        try:
            client = chromadb.HttpClient(
                host=self.host,
                port=self.port
            )
            return client

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None

    def __embedding_model(self):
        try:
            model = embedding_functions.OpenAIEmbeddingFunction(
                api_key=self.openai_api_key,
                model_name="text-embedding-ada-002"
            )
            return model

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None

    def get_collection(self, collection_name):
        assert type(collection_name) is str, f"""TypeError: Expected
        collection name as string, received {type(collection_name)}"""

        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.__embedding_model()
            )

            assert type(collection) is \
                chromadb.api.models.Collection.Collection, """
            Received invalid collection, check chromadb documentation.
            """

            assert collection.name == collection_name, f"""
            Returned collection name {collection.name} does not match the input
            collection name {collection_name}
            """

            return collection

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None

    def create_collection(self, collection_name):
        try:
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.__embedding_model()
            )

            assert type(collection) is \
                chromadb.api.models.Collection.Collection, """
                Received invalid collection, check chromadb documentation.
                """

            assert collection.name == collection_name, f"""
            Created collection name {collection.name} does not match the input
            collection name {collection_name}
            """
            return collection

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None

    def __dataloader(self, file_path):
        try:
            assert type(file_path) is str, f"""TypeError: Expected
            file_path as string, received {type(file_path)}"""

            loader = SimpleDirectoryReader(
                            input_files=[file_path],
                            encoding=self.text_encoding,
                            required_exts=self.required_exts,
                            num_files_limit=self.num_files_limit
                        )

            assert type(loader) is \
                llama_index.readers.file.base.SimpleDirectoryReader, """
            Received invalid dataloader, check llama-index documentation.
            """

            return loader

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None

    def __node_splitter(self):
        try:
            splitter = TokenTextSplitter(
                            chunk_size=self.config['CHUNK_SIZE'],
                            chunk_overlap=self.config['CHUNK_OVERLAP']
                        )

            return splitter

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None

    def load(self, file_path):
        try:
            loader = self.__dataloader(file_path=file_path)
            splitter = self.__node_splitter()

            documents = loader.load_data()
            nodes = splitter.get_nodes_from_documents(documents=documents)

            return nodes

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None

    def get_info(self, collection_name, n=10):
        try:
            assert type(n) is int, f"""TypeError: Expected
            n as Integer, received {type(n)}"""

            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.__embedding_model()
            )

            assert type(collection) is \
                chromadb.api.models.Collection.Collection, """
                Received invalid collection, check chromadb documentation.
                """

            return {
                'count': collection.count(),
                'items': collection.peek(limit=n),
                }

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None

    def get_all_collections(self):
        try:
            client = self.__initialize_client()
            collections = client.list_collections()
            collections = [c.name for c in collections]
            logging.info('Fetched list of collections in the database')
            return {'collections': collections}

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None

    def delete_collection(self, collection_name):
        try:
            client = self.__initialize_client()
            client.delete_collection(name=collection_name)

            logging.info(msg=f'Deleted {collection_name} collections')

        except Exception as e:
            logging.error(msg=f'Error: {e}')
            return None
