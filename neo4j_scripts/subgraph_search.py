from neo4j import GraphDatabase

class KnowledgeGraphSearch:
    def __init__(self, uri, user, password):
        # Initialize connection to the Neo4j database
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Close the Neo4j database connection
        self.driver.close()

    def search_subgraph(self, keyword, limit=10, offset=0):
        # Define a method to search for a subgraph based on a keyword with pagination
        with self.driver.session() as session:
            # Execute a Cypher query to match entities and relationships containing the keyword
            result = session.run(
                """
                MATCH (entity)-[relation]-(relatedEntity)
                WHERE entity.rdfs__label CONTAINS $keyword
                RETURN entity, relation, relatedEntity
                SKIP $offset
                LIMIT $limit
                """,
                keyword=keyword, limit=limit, offset=offset
            )
            formatted_results = []  # Initialize a list to store formatted results
            for record in result:
                entity = record["entity"]  # Extract the entity node
                relation = record["relation"].type  # Extract the relationship type
                related_entity = record["relatedEntity"]  # Extract the related entity node

                # Append formatted data to the results list
                formatted_results.append({
                    "Entity Label": entity.get("rdfs__label", "N/A"),  # Retrieve entity label
                    "Entity URI": entity.get("uri", "N/A"),  # Retrieve entity URI
                    "Relation": relation,  # Get the relationship type
                    "Related Entity Label": related_entity.get("rdfs__label", "N/A"),  # Retrieve related entity label
                    "Related Entity URI": related_entity.get("uri", "N/A"),  # Retrieve related entity URI
                })
            return formatted_results  # Return the formatted results list
