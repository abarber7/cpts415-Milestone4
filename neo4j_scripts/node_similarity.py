from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flask import Flask, request, jsonify
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

class NodeSimilarityCalculator:
    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def calculate_similarity(self, uri1, uri2):
        logging.info(f"Calculating similarity between {uri1} and {uri2}")
        with self.driver.session() as session:
            # Generalized query to fetch neighbors regardless of relationship type
            result1 = session.run(
                """
                MATCH (n {uri: $uri})-[r]-(m)
                RETURN collect(m.uri) AS neighbors
                """,
                uri=uri1
            )
            record1 = result1.single()
            neighbors1 = record1['neighbors'] if record1 else []

            result2 = session.run(
                """
                MATCH (n {uri: $uri})-[r]-(m)
                RETURN collect(m.uri) AS neighbors
                """,
                uri=uri2
            )
            record2 = result2.single()
            neighbors2 = record2['neighbors'] if record2 else []

            # Handle the case where no neighbors are found
            if not neighbors1 or not neighbors2:
                return 0  # Default similarity value if either node has no neighbors

            # Create feature vectors and normalize
            all_neighbors = list(set(neighbors1 + neighbors2))
            vector1 = np.array([1 if neighbor in neighbors1 else 0 for neighbor in all_neighbors]).reshape(1, -1)
            vector2 = np.array([1 if neighbor in neighbors2 else 0 for neighbor in all_neighbors]).reshape(1, -1)

            # Calculate cosine similarity
            similarity_metric = cosine_similarity(vector1, vector2)[0][0]
            return similarity_metric

# Neo4j credentials
similarity_calculator = NodeSimilarityCalculator("bolt://localhost:7687", "neo4j", "12345678")

@app.route('/find_similarity', methods=['POST'])
def find_similarity():
    data = request.json
    uri1 = data.get('uri1')
    uri2 = data.get('uri2')
    if uri1 and uri2:
        try:
            similarity = similarity_calculator.calculate_similarity(uri1, uri2)
            return jsonify({'similarity': similarity})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'URIs required'}), 400

if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        similarity_calculator.close()
