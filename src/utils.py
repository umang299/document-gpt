import os
import re
import sys
import json
import PyPDF2
from uuid import uuid4
from datetime import datetime

from llama_index.llms.base import ChatMessage, MessageRole

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(cwd)


def save_uploaded_file(uploadedfile):
    with open(os.path.join(cwd, 'data', uploadedfile.name), "wb") as f:
        f.write(uploadedfile.getbuffer())
    return os.path.join(cwd, 'data', uploadedfile.name)

def extract_text_from_pdf(pdf_file_path):
    """
    Extract text from a PDF file.

    Args:
        pdf_file_path (str): The path to the PDF file to be processed.

    Returns:
        list: A list of dictionaries containing extracted text and page numbers.
            Each dictionary has two keys: 'Page_No' and 'Page_Text'.
    """
    try:
        with open(pdf_file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            extracted_text = list()
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()

                extracted_text.append({
                    'Page_No': str(i + 1),
                    'Page_Text': preprocess_text(page_text),
                })

            return extracted_text
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def preprocess_text(text):
    """
    Preprocess text by removing newlines, tabs, and multiple spaces.

    Args:
        text (str): The input text to be preprocessed.

    Returns:
        str: The preprocessed text.
    """
    r = text.replace("\n", ' ')
    r = r.replace('\t', ' ')
    result = re.sub(r'\s+', ' ', r)
    return result

def logger(message, role):
    os.makedirs(os.path.join(cwd, 'conversation'), exist_ok=True)

    payload = {
            'Id' : str(uuid4()),
            'Role' : role,
            'Message' : message,
            'Timestamp' : datetime.isoformat(datetime.now()),
        }
    
    dst_path = os.path.join(cwd, "conversation", f"{payload['Id']}.json")
    with open(dst_path, 'w') as f:
        json.dump(payload, f)


def load_conversation(top_n):
    data_list = []
    conv_dir = os.path.join(cwd, 'conversation')
    for filename in os.listdir(conv_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(conv_dir, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                data_list.append(data)

    
    data_list.sort(key=lambda x: datetime.strptime(x["Timestamp"], "%Y-%m-%dT%H:%M:%S.%f"), reverse=False)

    chat_history = list()
    for data in data_list[:top_n]:
        if data['Role'] == MessageRole.USER:
            chat_history.append(ChatMessage(role=MessageRole.USER, content=data['Message']))
        else:
            chat_history.append(ChatMessage(role=MessageRole.ASSISTANT, content=data['Message']))

    return chat_history


def upsert(collection, nodes):
    """
    Upsert (insert or update) text data into a collection.

    Args:
        collection (chromadb.Collection): The ChromaDB collection to upsert data into.
        text (list): A list of dictionaries containing text data to upsert.

    Returns:
        None
    """
    for node in nodes:
        hash = node.hash
        content = node.text
        page_number = node.metadata['page_label']
        
        if content != '':
            content_metadata = {
                'id' : hash,
                'Page_No': page_number,
                'Page_Text': content
            }

            collection.add(
                documents=[content],
                metadatas=[content_metadata],
                ids=[str(id)]
            )