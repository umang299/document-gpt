import os
import unittest
from unittest.mock import MagicMock
from src.client import ChromaDBClient
from src.utils import load_yaml_file

conf = load_yaml_file(filename=os.path.join(os.path.dirname(__file__),
                                            '..',
                                            'config.yaml'))


class TestChromaDBClient(unittest.TestCase):
    def setUp(self):
        self.client = ChromaDBClient(
            openai_api_key=os.getenv('OPENAI_API_KEY')
            )

    def test_initialize_client(self):
        self.assertIsNotNone(self.client)

    def test_get_collection(self):
        self.client.client.get_or_create_collection = MagicMock(
                        return_value=conf['collection_name']
                        )
        collection = self.client.get_collection(conf['collection_name'])
        self.assertEqual(collection, conf['collection_name'])


if __name__ == '__main__':
    unittest.main()
