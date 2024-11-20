from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SubgraphMatcher:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def match_subgraph(self, pattern):
        with self.driver.session() as session:
            # Execute the subgraph pattern matching query
            result = session.run(
                pattern
            )
            
            # Collect matching subgraphs
            matches_list = []
            for record in result:
                matches_list.append(record.data())
                
            return matches_list

# Usage example
if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"

    subgraph_matcher = SubgraphMatcher(uri, user, password)
    try:
        # Define a new subgraph pattern for matching
        # This pattern starts by locating a node with the label 'Resource' and the specified URI ('United_States').
        # It then finds all nodes connected to this node through a relationship labeled 'RELATION'.
        # The query returns the URI of the original node, the URI of the related nodes, and the type of the relationship.
        pattern = """
        MATCH (n:Resource {uri: 'http://yago-knowledge.org/resource/Belgium'})
        MATCH (n)-[r:RELATION]-(m)
        RETURN n.uri AS node, m.uri AS related_node, type(r) AS relationship
        LIMIT 5
        """

        # Match and retrieve the subgraph
        subgraph_matches = subgraph_matcher.match_subgraph(pattern)
        print("Matching Subgraph:")
        for match in subgraph_matches:
            print(match)

    finally:
        subgraph_matcher.close()
