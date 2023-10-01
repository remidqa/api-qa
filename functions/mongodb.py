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

def find_documents(collection_name, query, options):
    collection = get_mongo_collection(collection_name)
    sort = options['sort'] if options.get('sort') and options.get('sort', {}).get('value') and options.get('sort', {}).get('direction') else {'value': "_id", "direction": 1}
    limit = options['limit'] if options.get('limit') else 10
    documents = collection.find(query).sort(sort['value'], sort['direction']).limit(limit)
    docs =[]
    for doc in documents:
        docs.append(doc)
    return docs

def insert_document(collection_name, document):
    collection = get_mongo_collection(collection_name)
    inserted_document = collection.insert_one(document)
    return inserted_document

def delete_decuments(collection_name, query):
    collection = get_mongo_collection(collection_name)
    deleted_documents = collection.delete_many(query)
    return f"{deleted_documents.deleted_count} documents deleted"
