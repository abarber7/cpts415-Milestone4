from neo4j import GraphDatabase

class ShortestPathTester:
    def __init__(self, uri, user, password):
        # Initialize connection to Neo4j database
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Close the Neo4j database connection
        if self.driver:
            self.driver.close()

    def get_neighbors_count(self, node_uri):
        # Get the count of neighbors for a specific node URI
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n:Resource {uri: $node_uri})-[]-(neighbor:Resource)
                RETURN count(neighbor) AS neighborCount
                """,
                node_uri=node_uri
            )
            # Extract the neighbor count from the query result
            neighbor_count = result.single()["neighborCount"]
            print(f"Neighbors of '{node_uri}': {neighbor_count} neighbors")
            return neighbor_count

    def are_neighbors(self, uri1, uri2):
        # Check if two nodes are direct neighbors
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n1:Resource {uri: $uri1})-[]-(n2:Resource {uri: $uri2})
                RETURN count(n2) > 0 AS areNeighbors
                """,
                uri1=uri1,
                uri2=uri2
            )
            # Return whether nodes are direct neighbors
            return result.single()["areNeighbors"]

    def has_common_neighbors(self, uri1, uri2):
        # Check if two nodes have any common neighbors
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n1:Resource {uri: $uri1})-[]-(neighbor:Resource)-[]-(n2:Resource {uri: $uri2})
                RETURN count(neighbor) > 0 AS hasCommonNeighbors
                """,
                uri1=uri1,
                uri2=uri2
            )
            # Return whether nodes have common neighbors
            return result.single()["hasCommonNeighbors"]

    def detailed_shortest_path(self, start_uri, end_uri):
        # Find the shortest path between two nodes using Neo4j's built-in function
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH p = shortestPath(
                    (start:Resource {uri: $start_uri})-[*]-(end:Resource {uri: $end_uri})
                )
                RETURN length(p) AS pathLength, [node IN nodes(p) | node.uri] AS pathNodes
                """,
                start_uri=start_uri,
                end_uri=end_uri
            )

            # Extract path details and print them if a path is found
            path_record = result.single()
            if path_record:
                path_length = path_record["pathLength"]
                path_nodes = path_record["pathNodes"]
                
                print("\nBuilt-in shortest path:")
                print("Shortest path details:")
                print(f"Path length: {path_length}")
                print("Path nodes (URIs):")
                for node_uri in path_nodes:
                    print(node_uri)
                
                # Return path details as a dictionary
                return {
                    "pathLength": path_length,
                    "pathNodes": path_nodes
                }
            else:
                print(f"No path found between '{start_uri}' and '{end_uri}'.")
                return None

# Usage example
if __name__ == "__main__":
    # Neo4j connection details
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"
    
    # Initialize the ShortestPathTester instance
    tester = ShortestPathTester(uri, user, password)
    
    try:
        # Define start and end URIs for testing
        start_uri = "http://yago-knowledge.org/resource/State_of_Bahrain"
        end_uri = "http://yago-knowledge.org/resource/Order_of_King_Abdulaziz"

        # Get and print neighbor counts for both URIs
        print("Checking neighbor counts...")
        start_neighbors = tester.get_neighbors_count(start_uri)
        end_neighbors = tester.get_neighbors_count(end_uri)

        # Check if URIs are direct neighbors
        if tester.are_neighbors(start_uri, end_uri):
            print(f"\nThe nodes '{start_uri}' and '{end_uri}' are direct neighbors. Path is shorter than 2.")
        else:
            # Check if URIs have common neighbors
            if tester.has_common_neighbors(start_uri, end_uri):
                print(f"\nThe nodes '{start_uri}' and '{end_uri}' have a common neighbor. Path is shorter than 2.")
            else:
                print(f"\nThe nodes '{start_uri}' and '{end_uri}' are not within 2 connections.")

        # Run and display detailed shortest path information
        tester.detailed_shortest_path(start_uri, end_uri)
        
    finally:
        # Close the Neo4j connection
        tester.close()
