import os
import sys
import unittest
from unittest.mock import MagicMock

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(cwd)

from src.client import ChromaDBClient
from src.utils import load_yaml_file

conf = load_yaml_file(filename=os.path.join(cwd, 'config.yaml'))

class TestChromaDBClient(unittest.TestCase):
    def setUp(self):
        self.client = ChromaDBClient(openai_api_key=conf['OPENAI_API_KEY'])

    def test_initialize_client(self):
        self.assertIsNotNone(self.client)

    def test_get_collection(self):
        self.client.client.get_or_create_collection = MagicMock(return_value=conf['collection_name'])
        collection = self.client.get_collection(conf['collection_name'])
        self.assertEqual(collection, conf['collection_name'])

    def test_create_collection(self):
        self.client.client.create_collection = MagicMock(return_value=conf['new_collection_name'])
        collection = self.client.create_collection(conf['new_collection_name'])
        self.assertEqual(collection, conf['new_collection_name'])

if __name__ == '__main__':
    unittest.main()