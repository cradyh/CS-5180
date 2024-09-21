# -------------------------------------------------------------------------
# AUTHOR: Chanrady Ho
# FILENAME: indexing.py
# SPECIFICATION: Calculate tf-idf of 3 documents and display the document-term matrix
# FOR: CS 5180- Assignment #1
# TIME SPENT: 1 hour
# -----------------------------------------------------------*/

# Importing some Python libraries
import csv
import math

documents = []

# Reading the data in a csv file
with open('collection.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i > 0:  # skipping the header
            documents.append(row[0])

# Conducting stopword removal for pronouns/conjunctions. Hint: use a set to define your stopwords.
# --> add your Python code here
stopWords = {'i', 'and', 'she', 'her', 'they', 'their'}

# Conducting stemming. Hint: use a dictionary to map word variations to their stem.
# --> add your Python code here
stemming = {'loves': 'love', 'dogs': 'dog', 'cats': 'cat'}

# Identifying the index terms.
# --> add your Python code here
terms = []
for doc in documents:
    texts = doc.split()
    for word in texts:
        if word.lower() not in stopWords:
            stemmed_word = stemming.get(word.lower(), word.lower())
            terms.append(stemmed_word)

# Calculate df for each term
df = {term: 0 for term in terms}
for doc in documents:
    doc_words = doc.split()
    stemmed_doc_words = [stemming.get(word.lower(), word.lower()) for word in doc_words]
    for word in set(terms):
        if word in stemmed_doc_words:
            df[word] += 1

# Building the document-term matrix by using the tf-idf weights.
# --> add your Python code here
docTermMatrix = []
for doc in documents:
    doc_words = doc.split()
    stemmed_doc_words = [stemming.get(word.lower(), word.lower()) for word in doc_words]
    tfidf_list = []
    for word in set(terms):
        tf = stemmed_doc_words.count(word)/len(doc_words)
        idf = math.log10(len(documents)/df[word])
        tfidf = round(tf * idf, 4)
        tfidf_list.append(tfidf)
    docTermMatrix.append(tfidf_list)

# Printing the document-term matrix.
# --> add your Python code here
documents_col = ['Document 1', 'Document 2', 'Document 3']
header = "              " + " | ".join(set(terms))
print(header)
for i, row in enumerate(docTermMatrix):
    result = f"{documents_col[i]} " + " | ".join([f"{value:.4f}" for value in row])
    print(result)
