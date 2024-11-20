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
            # Execute a Cypher query to match entities and relationships containing the keyword (case-insensitive)
            result = session.run(
                """
                MATCH (entity)-[relation]-(relatedEntity)
                WHERE entity.rdfs__label =~ '(?i).*' + $keyword + '.*'
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

    def get_entity_subgraph(self, entity_uri, limit=10):
        # Fetch the subgraph related to the selected entity for visualization, including all related nodes and edges
        with self.driver.session() as session:
            # Step 1: Get all nodes connected to the initial entity (depth 1)
            result = session.run(
                """
                MATCH (entity {uri: $entity_uri})-[relation]-(relatedEntity)
                RETURN entity, relation, relatedEntity
                LIMIT $limit
                """,
                entity_uri=entity_uri, limit=limit
            )
            
            nodes = {}  # Use a dictionary to store unique nodes
            links = []  # List to store relationships
            existing_links = set()  # Set to store unique relationships

            for record in result:
                entity = record["entity"]
                related_entity = record["relatedEntity"]
                relation = record["relation"]

                entity_id = entity.element_id
                related_entity_id = related_entity.element_id

                # Add nodes to the dictionary to ensure uniqueness
                nodes[entity_id] = {
                    "id": entity_id,
                    "label": entity.get("rdfs__label", "N/A"),
                    "uri": entity.get("uri", "N/A")
                }
                nodes[related_entity_id] = {
                    "id": related_entity_id,
                    "label": related_entity.get("rdfs__label", "N/A"),
                    "uri": related_entity.get("uri", "N/A")
                }

                # Add the relationship to the links list if not already present
                link_key = (entity_id, related_entity_id, relation.type)
                if link_key not in existing_links:
                    links.append({
                        "source": entity_id,
                        "target": related_entity_id,
                        "type": relation.type
                    })
                    existing_links.add(link_key)

            # Step 2: Get all relationships between the nodes in the current subgraph (depth 2 relationships)
            # This ensures that relationships between related nodes are also captured
            node_ids = list(nodes.keys())
            result = session.run(
                """
                MATCH (n)-[r]->(m)
                WHERE elementId(n) IN $node_ids AND elementId(m) IN $node_ids
                RETURN n, r, m
                """,
                node_ids=node_ids
            )

            for record in result:
                source = record["n"]
                target = record["m"]
                relation = record["r"]

                source_id = source.element_id
                target_id = target.element_id

                # Add any additional relationships found between existing nodes without redundancy
                link_key = (source_id, target_id, relation.type)
                if link_key not in existing_links:
                    links.append({
                        "source": source_id,
                        "target": target_id,
                        "type": relation.type
                    })
                    existing_links.add(link_key)

            # Convert nodes to a list for easier front-end use
            return {"nodes": list(nodes.values()), "links": links}  
