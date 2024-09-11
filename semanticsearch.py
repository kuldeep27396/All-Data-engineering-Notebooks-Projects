import pymongo
from sentence_transformers import SentenceTransformer
import sys
import re

MONGO_URI = "mongodb+srv://youranotherdataguy:qROdoddELnuhCNcG@sematic.wv0b1.mongodb.net/"

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def connect_to_mongodb():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client.sample_mflix
        collection = db.movies
        return client, collection
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(f"Error: Unable to connect to MongoDB. Please check your connection string and network connection.")
        print(f"Details: {e}")
        sys.exit(1)

def generate_embedding(text: str) -> list[float]:
    embedding = model.encode([text], convert_to_tensor=False)[0]
    return embedding.tolist()

# def add_embeddings_to_movies(collection):
#     movies_without_embedding = collection.find({"plot": {"$exists": True}, "plot_embedding_hf": {"$exists": False}})
#     total_movies = collection.count_documents({"plot": {"$exists": True}, "plot_embedding_hf": {"$exists": False}})
#
#     print(f"Adding embeddings to {total_movies} movies...")
#
#     for i, movie in enumerate(movies_without_embedding, 1):
#         if 'plot' in movie and movie['plot']:
#             embedding = generate_embedding(movie['plot'])
#             collection.update_one({"_id": movie["_id"]}, {"$set": {"plot_embedding_hf": embedding}})
#
#         if i % 10000 == 0:
#             print(f"Processed {i}/{total_movies} movies")

def create_vector_index(collection):
    index_name = "PlotSemanticSearch"

    # Check if the index already exists
    existing_indexes = collection.list_indexes()
    if any(index['name'] == index_name for index in existing_indexes):
        print(f"Index '{index_name}' already exists.")
        return

    print(f"Creating vector search index '{index_name}'...")
    collection.create_index(
        [("plot_embedding_hf", "PlotSemanticSerach")],
        name=index_name,
        vectorSearchOptions={
            "kind": "cosine",
            "numDimensions": 384  # Dimension of all-MiniLM-L6-v2 embeddings
        }
    )
    print(f"Vector search index '{index_name}' created successfully.")

def vector_search_movies(collection, query: str, limit: int = 4):
    query_embedding = generate_embedding(query)
    try:
        results = collection.aggregate([
            {"$vectorSearch": {
                "queryVector": query_embedding,
                "path": "plot_embedding_hf",
                "numCandidates": 100,
                "limit": limit,
                "index": "PlotSemanticSerach",
            }}
        ])
        return list(results)
    except pymongo.errors.OperationFailure as e:
        print(f"Error: Unable to perform vector search. Details: {e}")
        return []

def text_search_movies(collection, query: str, limit: int = 4):
    regex = re.compile(query, re.IGNORECASE)
    results = collection.find({"$or": [
        {"title": regex},
        {"plot": regex}
    ]}).limit(limit)
    return list(results)

def main():
    client, collection = connect_to_mongodb()

    # Step 1: Add embeddings (commented out as embeddings already exist)
    # add_embeddings_to_movies(collection)

    # Step 2: Create vector index (if it doesn't exist)
    # create_vector_index(collection)

    # Step 3: Perform searches
    queries = ["Movies from India", "move where Alia is there", "indian bollywood", "marvel movies"]

    for query in queries:
        print(f"\nSearching for: '{query}'")

        vector_results = vector_search_movies(collection, query)
        text_results = text_search_movies(collection, query)

        print(f"Vector Search Results ({len(vector_results)}):")
        for movie in vector_results:
            print(f"- {movie['title']}")

        print(f"\nText Search Results ({len(text_results)}):")
        for movie in text_results:
            print(f"- {movie['title']}")

        print("\nFirst vector search result details:")
        if vector_results:
            first_result = vector_results[0]
            print(f"Title: {first_result['title']}")
            print(f"Plot: {first_result['plot'][:200]}...")
            print(f"Embedding present: {'plot_embedding_hf' in first_result}")
        else:
            print("No vector search results.")

    client.close()
    print("Process completed successfully.")

if __name__ == "__main__":
    main()
