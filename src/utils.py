import os
import re
import json
import yaml
import time
import openai
import PyPDF2
from uuid import uuid4
from datetime import datetime

from llama_index.llms.base import ChatMessage
from llama_index.llms.types import MessageRole
from .logger import logging

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


def load_yaml_file(filename):
    """
    Load data from a YAML file.

    Args:
    filename (str): The path to the YAML file.

    Returns:
    dict: The data loaded from the YAML file.
    """
    try:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)

        return data

    except Exception as e:
        logging.error(f'Load yaml file: {e}')
        return None


def save_uploaded_file(uploadedfile):
    try:
        config = load_yaml_file(filename=os.path.join(cwd, 'config.yaml'))
        os.makedirs(os.path.join(cwd, config['data_dir']), exist_ok=True)

        with open(os.path.join(
                            cwd,
                            config['data_dir'],
                            uploadedfile.name), "wb") as f:

            f.write(uploadedfile.getbuffer())

        return os.path.join(cwd, 'data', uploadedfile.name)

    except Exception as e:
        logging.error(f'Save uploade file: {e}')
        return None


def extract_text_from_pdf(pdf_file_path):
    """
    Extract text from a PDF file.

    Args:
        pdf_file_path (str): The path to the PDF file to be processed.

    Returns:
        list: A list of dictionaries containing extracted text and page
              numbers.
            Each dictionary has two keys: 'Page_No' and 'Page_Text'.
    """
    try:
        start = time.time()
        with open(pdf_file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            extracted_text = list()
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()

                extracted_text.append({
                    'Page_No': str(i + 1),
                    'Page_Text': preprocess_text(page_text),
                })

        end = time.time()

        dur = end - start
        return extracted_text, dur

    except Exception as e:
        logging.error(f"Extract text from pdf: {str(e)}")
        return None


def preprocess_text(text):
    """
    Preprocess text by removing newlines, tabs, and multiple spaces.

    Args:
        text (str): The input text to be preprocessed.

    Returns:
        str: The preprocessed text.
    """
    try:
        start = time.time()
        r = text.replace("\n", ' ')
        r = r.replace('\t', ' ')
        result = re.sub(r'\s+', ' ', r)
        end = time.time()
        dur = end - start
        logging.info(f'text preprocessing: Execution time {dur}')

        return result

    except Exception as e:
        logging.error(f'text preprocessing: {e}')
        return None


def logger(message, role):
    try:
        config = load_yaml_file(filename=os.path.join(cwd, 'config.yaml'))
        os.makedirs(os.path.join(cwd, config['conv_dir']),
                    exist_ok=True)

        payload = {
                'Id': str(uuid4()),
                'Role': role,
                'Message': message,
                'Timestamp': datetime.isoformat(datetime.now()),
            }

        dst_path = os.path.join(cwd, "conversation", f"{payload['Id']}.json")
        with open(dst_path, 'w') as f:
            json.dump(payload, f)

    except Exception as e:
        logging.error(f'Logging error: {e}')
        return None


def load_conversation():
    try:
        config = load_yaml_file(filename=os.path.join(cwd, 'config.yaml'))
        top_n = config['top_n']
        os.makedirs(os.path.join(cwd, config['conv_dir']),
                    exist_ok=True)

        start = time.time()
        data_list = []
        conv_dir = os.path.join(cwd, config['conv_dir'])
        for filename in os.listdir(conv_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(conv_dir, filename)
                with open(file_path, "r") as file:
                    data = json.load(file)
                    data_list.append(data)

        data_list.sort(
            key=lambda x: datetime.strptime(
                x["Timestamp"], "%Y-%m-%dT%H:%M:%S.%f"
                ),
            reverse=False
            )

        chat_history = list()
        for data in data_list[:top_n]:
            if data['Role'] == MessageRole.USER:
                chat_history.append(ChatMessage(role=MessageRole.USER,
                                                content=data['Message']))
            else:
                chat_history.append(ChatMessage(role=MessageRole.ASSISTANT,
                                                content=data['Message']))
        end = time.time()

        dur = end - start
        logging.info(f'Load conversation: Execution time {dur}')

        return chat_history

    except Exception as e:
        logging.info(f'Load conversation: {e}')
        return None


def upsert(collection, nodes):
    """
    Upsert (insert or update) text data into a collection.

    Args:
        collection (chromadb.Collection): The ChromaDB collection to upsert
        data into.
        text (list): A list of dictionaries containing text data to upsert.

    Returns:
        None
    """
    try:
        start = time.time()
        for node in nodes:
            hash = node.hash
            content = node.text
            page_number = node.metadata['page_label']

            if content != '':
                content_metadata = {
                    'id': hash,
                    'Page_No': page_number,
                    'Page_Text': content
                }

                collection.add(
                    documents=[content],
                    metadatas=[content_metadata],
                    ids=[str(id)]
                )
        end = time.time()

        dur = end - start
        return dur, len(nodes)

    except Exception as e:
        logging.error(f'Upsert Error: {e}')
        return None


def is_api_key_valid():
    env = load_yaml_file(filename=os.path.join(cwd, 'config.yaml'))
    openai.api_key = env['OPENAI_API_KEY']

    try:
        openai.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "You are a helpful" +
                      "assistant."},
                    {"role": "user", "content": "Knock knock."},
                    {"role": "assistant", "content": "Who's there?"},
                    {"role": "user", "content": "Orange."}],
                temperature=0,
        )

    except ValueError:
        return False

    else:
        return True
