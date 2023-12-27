from flask import Flask, request, jsonify

import chromadb

from source.config import DB_DIR
from source.client import ChromaDBClient
from source.utils import upsert, get_response


app = Flask(__name__)
client = ChromaDBClient()


@app.route('/collections', methods=['GET'])
def get_all_collections():
    collections = client.get_all_collections()
    return collections


@app.route('/collection', methods=['POST'])
def create_new_collection():
    data = request.json
    collection_name = data.get('collection_name')
    if collection_name:
        client.create_collection(collection_name=collection_name)
        return jsonify({
            'message': f'Collection {collection_name} created successfully'
            }), 201
    else:
        return jsonify({'error': 'Collection name is required'}), 400


@app.route('/collection/delete', methods=['DELETE'])
def delete_collection():
    collection_name = request.args.get('collection_name')
    client.delete_collection(collection_name=collection_name)
    return jsonify({
        'message': f'Collection {collection_name} deleted successfully'
        })


@app.route('/collection/info', methods=['GET'])
def get_collection_info():
    collection_name = request.args.get('collection_name')
    n = request.args.get('n', default=10, type=int)
    info = client.get_info(collection_name=collection_name, n=n)
    return jsonify(info)


@app.route('/collection/response', methods=['POST'])
def get_collection_response():
    data = request.json
    message = data['message']
    collection_name = data['collection_name']
    response = get_response(client, message, collection_name)
    return jsonify(response)


@app.route('/collection/upload', methods=['POST'])
def upload_collection():
    data = request.json
    collection_name = data['collection_name']
    file_path = data['file_path']

    collection = client.get_collection(collection_name)
    nodes = client.load(file_path)
    upsert(collection=collection, nodes=nodes)

    chromadb.PersistentClient(path=DB_DIR)
    return jsonify({
        'message': f"""
                    File uploaded to
                    collection {collection_name}
                    successfully"""
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
