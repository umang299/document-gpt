import os
import re
import sys
import PyPDF2


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


def upsert(collection, nodes):
    """
    Upsert (insert or update) text data into a collection.

    Args:
        collection (chromadb.Collection): The ChromaDB collection to upsert data into.
        text (list): A list of dictionaries containing text data to upsert.

    Returns:
        None
    """
    id = 1
    for node in nodes:
        hash = node.hash
        content = node.text
        page_number = node.metadata['page_label']
        
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
        id += 1