import os
import streamlit as st

from src.client import ChromaDBClient
from src.utils import save_uploaded_file, is_api_key_valid, load_yaml_file
from src.main import get_response, upload


cwd = os.getcwd()
api_status = is_api_key_valid()
st.write(f'API Key Status : {api_status}')

config = load_yaml_file(
    filename=os.path.join(cwd, 'config.yaml')
    )

client = ChromaDBClient(openai_api_key=os.getenv('OPENAI_API_KEY'),
                        host=os.getenv('HOST'),
                        port=os.getenv('PORT'))


def reset_session():
    for key in st.session_state.keys():
        del st.session_state[key]


st.title("Document GPT")

with st.sidebar:
    st.subheader(body='Database Info')
    if client.get_all_collections() != None:
        col = st.selectbox(
                        label='Select collection',
                        options=client.get_all_collections()
                        )
    else:
        st.write("Create a collection")

    col_name = st.text_input(label='Name of collection')
    col1, col2 = st.columns(2)
    with col1:
        if st.button(label='Delete Collection'):
            client.delete_collection(collection_name=col_name)
            reset_session()
    with col2:
        if st.button(label='Create Collection'):
            client.create_collection(collection_name=col_name)
            reset_session()

    st.title('Upload File')
    uploaded_files = st.file_uploader(
                label='Choose a PDF file',
                accept_multiple_files=False
            )
    if uploaded_files is not None:
        file_path = save_uploaded_file(uploaded_files)
        if st.button(label='Upload'):
            with st.spinner(text='Uploading'):
                upload_time = upload(
                                client=client,
                                collection_name=col,
                                file_path=file_path,
                            )
            st.success(body='Data Uploaded', icon='✅')
            os.remove(file_path)
            reset_session()
        else:
            pass

    else:
        pass


try:
    col_info = client.get_info(collection_name=col)
    st.write(f"Collection Name : **{col}**")
except NameError:
    st.write("Collection Name : **None**")


if client.get_all_collections() != []:
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
            response = get_response(
                                client=client,
                                collection_name=col,
                                message=msg)['response']
            st.markdown(response)

        st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": response
                                        })
else:
    st.header('**← Create an collection to continue**')
