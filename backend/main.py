from fastapi import FastAPI, Query, HTTPException

from source.client import (
                        delete_collection,
                        create_collection,
                        list_collections,
                        upload,
                        response
                        )

app = FastAPI()


@app.get('/collections')
def list_collections_endpoint():
    collections = list_collections()
    return collections


@app.post('/collection/{collection_name}')
def create_collection_endpoint(collection_name: str):
    try:
        collection = create_collection(
                        collection_name=collection_name
                    )
        return collection
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete('/collection/{collection_name}')
def delete_collection_endpoint(collection_name: str):
    try:
        delete_collection(collection_name=collection_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/upload")
async def upload_endpoint(
            collection_name: str = Query(None),
            text: str = Query(None)):
    try:
        data = {
                "collection_name": collection_name,
                "text": text
                }

        # Call your modified upload function
        result = upload(
                    collection_name=data['collection_name'],
                    text=data['text']
                )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/response")
async def response_endpoint(
            collection_name: str = Query(None),
            message: str = Query(None)):
    try:
        data = {
                "collection_name": collection_name,
                "message": message
                }

        # Call your modified upload function
        assistant_resp = response(
                            collection_name=data['collection_name'],
                            message=data['message']
                        )
        return assistant_resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
