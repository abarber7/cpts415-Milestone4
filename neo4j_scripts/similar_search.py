from neo4j import GraphDatabase

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
                entity_uri=entity_uri,  # Pass the entity URI
                limit=limit  # Pass the limit parameter
            )
            return [
                {
                    "URI": record["uri"],  # Extract URI of the similar entity
                    "Label": record.get("label", "N/A"),  # Extract label or return "N/A"
                }
                for record in result
            ]

    def relationship_specific_search(self, start_uri, relationship_type, depth=2):
        # Search entities connected by a specific relationship type up to a certain depth
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH path = (start:Resource {{uri: $start_uri}})-[:{relationship_type}*1..{depth}]-(end)
                RETURN DISTINCT end.uri AS uri, length(path) AS depth
                """,
                start_uri=start_uri  # Pass the starting URI
            )
            return [
                {
                    "End URI": record["uri"],  # Extract URI of the connected entity
                    "Traversal Depth": record["depth"],  # Extract the depth of traversal
                }
                for record in result
            ]

    def explore_multi_hop(self, start_uri, max_hops=3, limit=50):
        # Explore multi-hop connections for a given entity
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH path = (start:Resource {{uri: $start_uri}})-[*1..{max_hops}]-(end)
                RETURN DISTINCT end.uri AS uri, length(path) AS depth
                LIMIT $limit
                """,
                start_uri=start_uri,  # Pass the starting URI
                limit=limit,  # Limit the number of results
            )
            return [
                {
                    "Connected Entity": record["uri"],  # Extract URI of the connected entity
                    "Hops": record["depth"],  # Extract the number of hops
                }
                for record in result
            ]

# Neo4j Database Connection Details
NEO4J_URI = "neo4j://localhost:7687"  # Neo4j connection URI
NEO4J_USER = "neo4j"  # Neo4j username
NEO4J_PASSWORD = "12345678"  # Neo4j password

if __name__ == "__main__":
    # Initialize the Advanced Knowledge Search Engine
    search_engine = AdvancedKnowledgeSearch(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        # Define the reference URI
        reference_uri = "http://yago-knowledge.org/resource/Albert_Einstein"

        # Find similar entities based on shared awards
        print("Finding similar entities...")
        similar_entities = search_engine.find_similar_entities(reference_uri)
        for entity in similar_entities:
            print(entity)

        # Search specific relationships with a defined depth
        print("\nSearching specific relationship...")
        relationship_results = search_engine.relationship_specific_search(reference_uri, "sch__award", depth=2)
        for result in relationship_results:
            print(result)

        # Explore multi-hop connections for the reference entity
        print("\nExploring multi-hop connections...")
        multi_hop_results = search_engine.explore_multi_hop(reference_uri, max_hops=3)
        for connection in multi_hop_results:
            print(connection)
    finally:
        # Close the Neo4j connection
        search_engine.close()
