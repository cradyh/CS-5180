# -------------------------------------------------------------------------
# AUTHOR: Chanrady Ho
# FILENAME: document_ranking
# SPECIFICATION: Index terms from documents to MongoDB and rank the documents by a given query
# FOR: CS 5180- Assignment #4
# TIME SPENT: 3 hours
# -----------------------------------------------------------*/

from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity


def connect_database():
    DB_NAME = "CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except Exception as e:
        print("Database not connected successfully:", e)
        return None


def create_document_entry(col, doc_name, content):
    query = {
        'document': doc_name,
        'content': content
    }
    col.insert_one(query)


def create_index_entry(col, term, pos, doc_name, tfidf_score):
    query = {
        'term': term,
        'position': pos,
        'docs': [{
            'document': doc_name,
            'tfidf': tfidf_score
        }]
    }
    col.insert_one(query)


def update_index_entry(col, term, doc_name, tfidf_score):
    query = {'term': term}
    update = {
        "$push": {
            "docs": {
                'document': doc_name,
                'tfidf': tfidf_score
            }
        }
    }
    col.update_one(query, update)


def preprocess_documents(documents):
    count_vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 3), stop_words=None)
    count_vectorizer.fit(documents)
    training_v = count_vectorizer.transform(documents)
    count_tokens = count_vectorizer.get_feature_names_out()
    tfidf_training = TfidfTransformer()
    tfidf_training_matrix = tfidf_training.fit_transform(training_v)
    return count_vectorizer, count_tokens, tfidf_training_matrix


def create_inverted_index(db, count_tokens, tfidf_training_matrix):
    indexes_db = db['indexes']
    indexed_terms = set()

    for i, doc_tfidf in enumerate(tfidf_training_matrix.toarray()):
        for j, term_tfidf in enumerate(doc_tfidf):
            if term_tfidf != 0:
                document = f'doc{i + 1}'
                position = j
                term = count_tokens[position]

                if term not in indexed_terms:
                    indexed_terms.add(term)
                    create_index_entry(indexes_db, term, position, document, term_tfidf)
                else:
                    update_index_entry(indexes_db, term, document, term_tfidf)


def rank_documents(db, queries, count_vectorizer):
    documents_db = db['documents']

    doc_tfidf_transformer = TfidfTransformer()
    doc_term_matrix = count_vectorizer.transform(documents)
    doc_tfidf_matrix = doc_tfidf_transformer.fit_transform(doc_term_matrix)
    doc_vectors = doc_tfidf_matrix.toarray()

    for query in queries:
        print(f"Docs TF-IDF scores for query: {query}")

        query_vectorized = count_vectorizer.transform([query])
        query_vector = query_vectorized.toarray()

        cos_sim = cosine_similarity(query_vector, doc_vectors)[0]

        doc_scores = [(f"doc{i + 1}", cos_sim[i]) for i in range(len(cos_sim))]

        for i in range(len(doc_scores)):
            for j in range(i + 1, len(doc_scores)):
                if doc_scores[i][1] < doc_scores[j][1]:
                    doc_scores[i], doc_scores[j] = doc_scores[j], doc_scores[i]

        for doc_id, score in doc_scores:
            doc_entry = documents_db.find_one({'document': doc_id})
            if doc_entry and score > 0:
                print(f'"{doc_entry["content"]}", {round(score, 2)}')
        print()


if __name__ == "__main__":
    db = connect_database()
    doc1 = "After the medication, headache and nausea were reported by the patient."
    doc2 = "The patient reported nausea and dizziness caused by the medication."
    doc3 = "Headache and dizziness are common effects of this medication."
    doc4 = "The medication caused a headache and nausea, but no dizziness was reported."
    documents = [doc1, doc2, doc3, doc4]

    query1 = "nausea and dizziness"
    query2 = "effects"
    query3 = "nausea was reported"
    query4 = "dizziness"
    query5 = "the medication"
    queries = [query1, query2, query3, query4, query5]

    documents_db = db['documents']
    # for i, doc_content in enumerate(documents):
    #     create_document_entry(documents_db, f'doc{i + 1}', doc_content)

    count_vectorizer, count_tokens, tfidf_training_matrix = preprocess_documents(documents)
    # create_inverted_index(db, count_tokens, tfidf_training_matrix)
    rank_documents(db, queries, count_vectorizer)
