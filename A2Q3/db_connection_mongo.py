#-------------------------------------------------------------------------
# AUTHOR: Chanrady Ho
# FILENAME: db_connection_mongo.py
# SPECIFICATION: Backend for user menu for document database management and input it to a database using MongoDB
# FOR: CS 5180- Assignment #2
# TIME SPENT: 1 hour
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
# --> add your Python code here
from pymongo import MongoClient
import datetime


def connectDataBase():

    # Create a database connection object using pymongo
    # --> add your Python code here
    DB_NAME = "CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")


def createDocument(col, docId, docText, docTitle, docDate, docCat):

    # create a dictionary (document) to count how many times each term appears in the document.
    # Use space " " as the delimiter character for terms and remember to lowercase them.
    # --> add your Python code here
    document = {"_id": docId,
                "text": docText,
                "title": docTitle,
                "date": datetime.datetime.strptime(docDate, "%Y-%m-%d"),
                "category": docCat
                }
    col.insert_one(document)


    # create a list of dictionaries (documents) with each entry including a term, its occurrences, and its num_chars. Ex: [{term, count, num_char}]
    # --> add your Python code here
    punctuation = ['.', ',', '!', '?', '"', "'"]
    for p in punctuation:
        docText = docText.replace(p, '')

    words = docText.split()
    tf = {}
    for word in words:
        word = word.lower()
        if word in tf:
            tf[word] += 1
        else:
            tf[word] = 1

    for term in tf:
        terms = {"$push": {"terms": {
            "term": term,
            "count": tf[term],
            "num_chars": len(term)
        }}}
        # Insert the document
        # --> add your Python code here
        col.update_one({"_id": docId}, terms)


def deleteDocument(col, docId):

    # Delete the document from the database
    # --> add your Python code here
    col.delete_one({"_id": docId})


def updateDocument(col, docId, docText, docTitle, docDate, docCat):

    # Delete the document
    # --> add your Python code here
    deleteDocument(col, docId)

    # Create the document with the same id
    # --> add your Python code here
    createDocument(col, docId, docText, docTitle, docDate, docCat)


def getIndex(col):

    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3', ...}
    # We are simulating an inverted index here in memory.
    # --> add your Python code here
    term_dict = {}
    if col.count_documents({}) != 0:
        pipeline = [
            {"$unwind": {"path": "$terms"}},
            {"$project": {
                "_id": 0,
                "term": "$terms.term",
                "title": "$title",
                "count": "$terms.count"
            }},
            {"$sort": {"term": 1}}
        ]

        inverted_index = col.aggregate(pipeline)

        for i in inverted_index:
            term = i['term']
            title = i['title']
            count = i['count']
            if term in term_dict:
                term_dict[term] += f", {title}:{count}"
            else:
                term_dict[term] = f"{title}:{count}"
    return term_dict

