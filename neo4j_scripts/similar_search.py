from flask import Flask, request, jsonify
from neo4j import GraphDatabase

# Flask app initialization
app = Flask(__name__)

class AdvancedKnowledgeSearch:
    def __init__(self, uri, user, password):
        # Initialize the Neo4j connection
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Close the Neo4j database connection
        self.driver.close()

    def find_similar_entities(self, entity_uri, limit=10):
        # Find entities similar to a given entity based on shared awards
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (e:Resource {uri: $entity_uri})-[:sch__award]->(award)<-[:sch__award]-(similar:Resource)
                WHERE e <> similar
                RETURN similar.uri AS uri, similar.rdfs__label AS label
                LIMIT $limit
                """,
                entity_uri=entity_uri,
                limit=limit
            )
            return [
                {
                    "URI": record["uri"],
                    "Label": record.get("label", "N/A"),
                }
                for record in result
            ]

    def relationship_specific_search(self, start_uri, relationship_type, depth=2, offset=0, limit=10):
        # Search entities connected by a specific relationship type up to a certain depth
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH path = (start:Resource {{uri: $start_uri}})-[:{relationship_type}*1..{depth}]-(end)
                RETURN DISTINCT end.uri AS uri, length(path) AS depth
                SKIP $offset LIMIT $limit
                """,
                start_uri=start_uri,
                offset=offset,
                limit=limit
            )
            return [
                {
                    "End URI": record["uri"],
                    "Traversal Depth": record["depth"],
                }
                for record in result
            ]

    def explore_multi_hop(self, start_uri, max_hops=3, offset=0, limit=10):
        # Explore multi-hop connections for a given entity
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH path = (start:Resource {{uri: $start_uri}})-[*1..{max_hops}]-(end)
                RETURN DISTINCT end.uri AS uri, length(path) AS depth
                SKIP $offset LIMIT $limit
                """,
                start_uri=start_uri,
                offset=offset,
                limit=limit
            )
            return [
                {
                    "Connected Entity": record["uri"],
                    "Hops": record["depth"],
                }
                for record in result
            ]

# Neo4j Database Connection Details
NEO4J_URI = "neo4j://localhost:7687"  # Neo4j connection URI
NEO4J_USER = "neo4j"  # Neo4j username
NEO4J_PASSWORD = "12345678"  # Neo4j password

# Initialize Neo4j connection
search_engine = AdvancedKnowledgeSearch(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

@app.route('/find_similar_entities', methods=['POST'])
def find_similar_entities():
    try:
        data = request.json
        entity_uri = data.get("entity_uri")
        limit = data.get("limit", 10)  # Default limit is 10

        if not entity_uri:
            return jsonify({"error": "Entity URI is required."}), 400

        # Fetch similar entities
        similar_entities = search_engine.find_similar_entities(entity_uri, limit)

        # Fetch specific relationships
        relationship_results = search_engine.relationship_specific_search(entity_uri, "sch__award", depth=2)

        # Fetch multi-hop connections
        multi_hop_results = search_engine.explore_multi_hop(entity_uri, max_hops=3)

        return jsonify({
            "similar_entities": similar_entities,
            "relationship_results": relationship_results,
            "multi_hop_results": multi_hop_results,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    search_engine.close()
    return "Neo4j connection closed."

if __name__ == "__main__":
    app.run(debug=True)
