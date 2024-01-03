import os
import yaml
import json
from uuid import uuid4
from datetime import datetime

from llama_index.llms.base import ChatMessage
from llama_index.llms.types import MessageRole

from .config import CONFIG_PATH, CONV_DIR


def load_yaml_file(filename):
    try:
        assert type(filename) is str, f"""
        TypeError: Expected filename type as string, received
        {type(filename)}
        """

        with open(filename, 'r') as file:
            data = yaml.safe_load(file)

        return data

    except Exception as e:
        print(e)
        return None


def load_conversation():
    try:
        config = load_yaml_file(filename=CONFIG_PATH)
        top_n = config['TOP_K']
        os.makedirs(CONV_DIR,
                    exist_ok=True)

        data_list = list()
        for filename in os.listdir(CONV_DIR):
            if filename.endswith(".json"):
                file_path = os.path.join(CONV_DIR, filename)
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

        return chat_history

    except Exception as e:
        print(e)
        return None


def conversation_logger(message, role):
    try:
        os.makedirs(CONV_DIR,
                    exist_ok=True)

        assert type(message) is str, f"""
        TypeError: Expected message type as string, received
        {type(message)}
        """

        assert type(role) is str, f"""
        TypeError: Expected role type as string, received
        {type(role)}
        """

        payload = {
                'Id': str(uuid4()),
                'Role': role,
                'Message': message,
                'Timestamp': datetime.isoformat(datetime.now()),
            }

        dst_path = os.path.join(CONV_DIR, f"{payload['Id']}.json")
        with open(dst_path, 'w') as f:
            json.dump(payload, f)

    except Exception as e:
        print(e)
        return None
