import os
import sys
import dotenv
import streamlit as st
from openai import OpenAI

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(cwd)

os.makedirs(name=os.path.join(cwd, 'data'), exist_ok=True)
os.makedirs(name=os.path.join(cwd, 'conversation'), exist_ok=True)

from src.client import ChromaDBClient
from src.utils import save_uploaded_file
from main import get_response, upload

env_path = os.path.join(cwd, '.env')
api_key = dotenv.dotenv_values(env_path)['OPENAI_API_KEY']
client = ChromaDBClient(openai_api_key=api_key)

st.title("Document GPT")

with st.sidebar:
    st.title('Upload File')
    uploaded_files = st.file_uploader(
                label='Choose a PDF file', 
                accept_multiple_files=False
            )
    if uploaded_files is not None:
        file_path = save_uploaded_file(uploaded_files)
        if st.button(label='Upload'):
            with st.spinner(text='Uploading'):
                upload(
                    client=client,
                    file_path=file_path,
                )
            st.success(body='Data Uploaded', icon='✅')
            os.remove(file_path)
        else:
            pass
    else:
        pass

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
        response = get_response(client=client, message=msg)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})