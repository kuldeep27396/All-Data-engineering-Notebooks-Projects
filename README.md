# Semantic-Search
# Semantic Search for Movies

This project implements a semantic search system for a movie database using MongoDB Atlas and sentence transformers. It allows for both vector-based semantic search and traditional text-based search on movie plots and titles.

## Features

- Connect to MongoDB Atlas cluster
- Generate embeddings for movie plots using the 'all-MiniLM-L6-v2' model
- Create a vector search index in MongoDB
- Perform vector-based semantic search on movie plots
- Perform text-based search on movie titles and plots
- Compare results from both search methods

## Prerequisites

- Python 3.9+
- MongoDB Atlas account with a cluster set up
- `pymongo` library
- `sentence_transformers` library

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```
   pip install pymongo sentence_transformers
   ```

3. Set up your MongoDB Atlas cluster and obtain the connection string.

4. Replace the `MONGO_URI` in the script with your MongoDB Atlas connection string.

## Usage

Run the script with:

```
python semanticsearch.py
```

The script will:
1. Connect to your MongoDB Atlas cluster
2. Create a vector search index (if it doesn't exist)
3. Perform searches using predefined queries
4. Display results from both vector-based and text-based searches

## Configuration

- Modify the `queries` list in the `main()` function to change the search queries.
- Adjust the `limit` parameter in `vector_search_movies()` and `text_search_movies()` to change the number of results returned.

## Notes

- The script assumes that movie plot embeddings have already been generated and stored in the database. If you need to generate embeddings, uncomment the `add_embeddings_to_movies()` function call in `main()`.
- The vector search index creation is commented out by default. Uncomment the `create_vector_index()` function call in `main()` if you need to create the index.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
