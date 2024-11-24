from neo4j import GraphDatabase

# Database credentials
NEO4J_URI = "bolt://localhost:7687"  # Default Neo4j URI
NEO4J_USER = "neo4j"                 # Neo4j username
NEO4J_PASSWORD = "12345678"     # Replace with your Neo4j password

# Path to the Turtle file
TTL_FILE_PATH = "file:///C:/Users/coota/Documents/WSU Grad School/WSU Fall 2024/CPT_s 415/Milestone 3/yago-facts.ttl"  # Replace with the path to your Turtle file

# Initialize the Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def load_ttl_file(tx, ttl_file_path):
    """
    Executes the n10s.rdf.import.fetch Cypher query to load a Turtle file.
    """
    query = """
    CALL n10s.rdf.import.fetch($filePath, 'Turtle')
    """
    tx.run(query, filePath=ttl_file_path)

def main():
    with driver.session() as session:
        try:
            print(f"Loading Turtle file: {TTL_FILE_PATH} into Neo4j...")
            session.write_transaction(load_ttl_file, TTL_FILE_PATH)
            print("Turtle file successfully loaded into Neo4j!")
        except Exception as e:
            print(f"Error during Turtle file ingestion: {e}")
        finally:
            driver.close()

if __name__ == "__main__":
    main()
