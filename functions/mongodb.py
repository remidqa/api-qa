from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongodb_srv = os.environ.get("MONGODB_SRV")

def get_mongo_collection(collection):
    client = MongoClient(mongodb_srv)
    db = client["executions"]
    collection = db[collection]
    return collection

def find_one_document(collection_name, query):
    collection = get_mongo_collection(collection_name)
    document = collection.find_one(query)
    return document

def find_documents(collection_name, query):
    collection = get_mongo_collection(collection_name)
    documents = collection.find(query)
    docs =[]
    for doc in documents:
        docs.append(doc)
    return docs

def insert_document(collection_name, metadata, executions):
    collection = get_mongo_collection(collection_name)
    inserted_document = collection.insert_one({"metadata": metadata, "executions":executions})
    return inserted_document

def delete_decuments(collection_name, query):
    collection = get_mongo_collection(collection_name)
    deleted_documents = collection.delete_many(query)
    return f"{deleted_documents.deleted_count} documents deleted"
