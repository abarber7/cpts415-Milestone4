from flask import Flask, request, render_template, jsonify
from neo4j import GraphDatabase
from neo4j_scripts.node_similarity import NodeSimilarityCalculator
from neo4j_scripts.similar_search import AdvancedKnowledgeSearch
from neo4j_scripts.subgraph_search import KnowledgeGraphSearch
from neo4j_scripts.within_two import ShortestPathTester
from neo4j_scripts.subgraph_matcher import SubgraphMatcher

# Initialize Flask app
app = Flask(__name__)

# Neo4j credentials for connecting to the database
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

# Instantiate helper classes for Neo4j interactions
similarity_calculator = NodeSimilarityCalculator(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
knowledge_search = AdvancedKnowledgeSearch(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
subgraph_search_engine = KnowledgeGraphSearch(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
shortest_path_tester = ShortestPathTester(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
subgraph_matcher = SubgraphMatcher(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

@app.route('/')
def index():
    # Render the main search bar UI
    return render_template('search_barUI.html')

@app.route('/find_similarity', methods=['POST'])
def find_similarity():
    # Find similarity between two nodes
    data = request.json
    uri1 = data.get('uri1')
    uri2 = data.get('uri2')
    if uri1 and uri2:
        similarity = similarity_calculator.calculate_similarity(uri1, uri2)  # Calculate similarity score
        return jsonify({'similarity': similarity})
    else:
        return jsonify({'error': 'URIs required'}), 400  # Return error if URIs are missing

@app.route('/search_subgraph', methods=['POST'])
def search_subgraph():
    # Search for subgraphs matching a keyword
    data = request.json
    keyword = data.get('keyword')
    offset = data.get('offset', 0)  # Use default offset of 0
    if keyword:
        try:
            results = subgraph_search_engine.search_subgraph(keyword, offset=offset)  # Fetch results
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500  # Return error if search fails
    else:
        return jsonify({'error': 'Keyword required'}), 400  # Return error if keyword is missing

@app.route('/multi_hop', methods=['POST'])
def multi_hop():
    # Fetch multi-hop connections for a node
    data = request.json
    start_uri = data.get('start_uri')
    max_hops = data.get('max_hops', 3)  # Default to 3 hops
    if start_uri:
        results = knowledge_search.explore_multi_hop(start_uri, max_hops)  # Fetch multi-hop results
        return jsonify(results)
    else:
        return jsonify({'error': 'Start URI required'}), 400  # Return error if start URI is missing

@app.route('/shortest_path', methods=['POST'])
def shortest_path():
    # Find the shortest path between two nodes
    data = request.json
    start_uri = data.get('start_uri')
    end_uri = data.get('end_uri')
    if not start_uri or not end_uri:
        return jsonify({'error': 'Start and end URIs are required.'}), 400  # Return error if URIs are missing

    try:
        result = shortest_path_tester.detailed_shortest_path(start_uri, end_uri)  # Fetch shortest path
        if not result:
            return jsonify({'error': 'No shortest path found between the specified nodes.'}), 404  # Handle no path case

        # Format the result for frontend compatibility
        path_nodes = result.get('pathNodes', [])  # Extract path nodes
        nodes = [{'id': str(i + 1), 'label': uri} for i, uri in enumerate(path_nodes)]  # Create node data
        links = [
            {'source': str(i + 1), 'target': str(i + 2), 'type': 'CONNECTED_TO'}  # Create edge data
            for i in range(len(path_nodes) - 1)
        ]

        return jsonify({'nodes': nodes, 'links': links})  # Return formatted graph data
    except Exception as e:
        print(f"Error in shortest_path: {e}")  # Log error for debugging
        return jsonify({'error': str(e)}), 500  # Return error message

@app.route('/test_db_connection', methods=['GET'])
def test_db_connection():
    # Test connection to the Neo4j database
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            with driver.session() as session:
                result = session.run("RETURN 'Neo4j Connection Successful' AS message")  # Test query
                message = result.single()["message"]
                return jsonify({"message": message})  # Return success message
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return error if connection fails

@app.route('/visualize_subgraph', methods=['POST'])
def visualize_subgraph():
    # Fetch and visualize a subgraph for a specific entity
    data = request.json
    entity_uri = data.get('entity_uri')
    if entity_uri:
        try:
            results = subgraph_search_engine.get_entity_subgraph(entity_uri)  # Fetch subgraph
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500  # Return error if subgraph fetch fails
    else:
        return jsonify({'error': 'Entity URI required'}), 400  # Return error if URI is missing

@app.route('/find_similar_entities', methods=['POST'])
def find_similar_entities():
    # Fetch similar entities, relationships, and multi-hop connections
    data = request.json
    entity_uri = data.get('entity_uri')
    offset = data.get('offset', 0)  # Use default offset of 0
    limit = data.get('limit', 10)  # Use default limit of 10

    if entity_uri:
        try:
            similar_entities = knowledge_search.find_similar_entities(entity_uri, limit=limit)  # Fetch similar entities
            relationship_results = knowledge_search.relationship_specific_search(entity_uri, "sch__award", depth=2, offset=offset, limit=limit)  # Fetch relationships
            multi_hop_results = knowledge_search.explore_multi_hop(entity_uri, max_hops=3, offset=offset, limit=limit)  # Fetch multi-hop connections

            return jsonify({
                "similar_entities": similar_entities,
                "relationship_results": relationship_results,
                "multi_hop_results": multi_hop_results
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500  # Return error if fetch fails
    else:
        return jsonify({'error': 'Entity URI required'}), 400  # Return error if URI is missing

@app.route('/within_two_connections', methods=['POST'])
def within_two_connections():
    # Check relationship status and neighbors between two nodes
    data = request.json
    start_uri = data.get('start_uri')
    end_uri = data.get('end_uri')

    if not start_uri or not end_uri:
        return jsonify({'error': 'Both start and end URIs are required'}), 400  # Return error if URIs are missing

    try:
        start_neighbors = shortest_path_tester.get_neighbors_count(start_uri)  # Get neighbors of start URI
        end_neighbors = shortest_path_tester.get_neighbors_count(end_uri)  # Get neighbors of end URI

        if shortest_path_tester.are_neighbors(start_uri, end_uri):
            relationship_status = f"The nodes '{start_uri}' and '{end_uri}' are direct neighbors. Path is shorter than 2."
        elif shortest_path_tester.has_common_neighbors(start_uri, end_uri):
            relationship_status = f"The nodes '{start_uri}' and '{end_uri}' have a common neighbor. Path is shorter than 2."
        else:
            relationship_status = f"The nodes '{start_uri}' and '{end_uri}' are not within 2 connections."

        shortest_path = shortest_path_tester.detailed_shortest_path(start_uri, end_uri)  # Fetch shortest path

        return jsonify({
            'start_neighbors': start_neighbors,
            'end_neighbors': end_neighbors,
            'relationship_status': relationship_status,
            'shortest_path': shortest_path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return error if operation fails
    
@app.route('/subgraph_match', methods=['POST'])
def subgraph_match():
    """Find subgraphs matching a given pattern."""
    data = request.json
    pattern = data.get('pattern')
    
    if not pattern:
        return jsonify({"error": "Pattern is required"}), 400
    
    try:
        matches = subgraph_matcher.match_subgraph(pattern)
        return jsonify({"matches": matches})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)  # Enable debug mode
