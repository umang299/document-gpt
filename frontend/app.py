import os
import io
import docx
import PyPDF2
import requests
import streamlit as st

base_url = os.environ['BASE_URL']


def extract_text(uploaded_file):
    if uploaded_file.name.endswith('.txt'):
        return uploaded_file.read().decode('utf-8')

    elif uploaded_file.name.endswith('.docx'):
        file_stream = io.BytesIO(uploaded_file.getvalue())
        doc = docx.Document(file_stream)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    elif uploaded_file.name.endswith('.pdf'):
        file_stream = io.BytesIO(uploaded_file.getvalue())
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text

    else:
        return "Unsupported file format"


st.title("Document GPT")
with st.sidebar:
    st.subheader(body='Database Info')
    response = requests.get(f'{base_url}/collections')

    if response.ok:
        collection = response.json()
        if len(collection) != 0:
            col = st.selectbox(
                        label='Select collection',
                        options=collection,
                        )
        else:
            st.write("Create a collection")
    else:
        collection = ['']

    col_name = st.text_input(label='Name of collection')
    col1, col2 = st.columns(2)
    with col1:
        if st.button(label='Delete Collection'):
            response = requests.delete(f'{base_url}/collection/{col_name}')
            if response.ok:
                st.write(f'Deleted {col_name} collection')
            else:
                st.write(f'Failed to delete {col_name} collection')
    with col2:
        if st.button(label='Create Collection'):
            response = requests.post(f'{base_url}/collection/{col_name}')
            if response.ok:
                st.write(f'Created {col_name} collection')
            else:
                st.write(f'Failed to create {col_name} collection')

    st.title('Upload File')
    uploaded_files = st.file_uploader(
                label='Choose a PDF file',
                accept_multiple_files=False
            )
    if uploaded_files is not None:
        extracted_text = extract_text(uploaded_file=uploaded_files)
        if st.button(label='Upload'):
            with st.spinner(text='Uploading'):

                params = {
                    'collection_name': col,
                    'text': extracted_text
                }

                response = requests.post(
                    f'{base_url}/upload', params=params
                )

                if response.ok:
                    st.success(body='Data Uploaded', icon='✅')
                else:
                    st.error('An error occurred during file upload.')
        else:
            pass

    else:
        pass


response = requests.get(f'{base_url}/collections')
if response.json() != []:
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            msg = st.session_state.messages[-1]['content']

            params = {'collection_name': col, 'message': msg}
            response = requests.get(f'{base_url}/response', params=params)
            st.markdown(response.json())

        st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": response.json()
                                        })
else:
    st.header('**← Create an collection to continue**')
