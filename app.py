from flask import Flask, request, render_template, jsonify
from neo4j import GraphDatabase
from neo4j_scripts.node_similarity import NodeSimilarityCalculator
from neo4j_scripts.similar_search import AdvancedKnowledgeSearch
from neo4j_scripts.subgraph_search import KnowledgeGraphSearch
from neo4j_scripts.within_two import ShortestPathTester

app = Flask(__name__)

# Neo4j credentials
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

# Instantiate classes for Neo4j interactions
similarity_calculator = NodeSimilarityCalculator(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
knowledge_search = AdvancedKnowledgeSearch(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
subgraph_search_engine = KnowledgeGraphSearch(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
shortest_path_tester = ShortestPathTester(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

@app.route('/')
def index():
    return render_template('search_barUI.html')

@app.route('/autofill', methods=['GET'])
def autofill():
    query = request.args.get('query', '')
    if query:
        suggestions = subgraph_search_engine.search_subgraph(query)
        suggestions_list = [result['Entity Label'] for result in suggestions]
        return jsonify(suggestions_list)
    else:
        return jsonify([])

@app.route('/find_similarity', methods=['POST'])
def find_similarity():
    data = request.json
    uri1 = data.get('uri1')
    uri2 = data.get('uri2')
    if uri1 and uri2:
        similarity = similarity_calculator.calculate_similarity(uri1, uri2)
        return jsonify({'similarity': similarity})
    else:
        return jsonify({'error': 'URIs required'}), 400

@app.route('/search_subgraph', methods=['POST'])
def search_subgraph():
    data = request.json
    keyword = data.get('keyword')
    offset = data.get('offset', 0)  # Default to 0 if offset is not provided
    if keyword:
        try:
            results = subgraph_search_engine.search_subgraph(keyword, offset=offset)
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Keyword required'}), 400

@app.route('/multi_hop', methods=['POST'])
def multi_hop():
    data = request.json
    start_uri = data.get('start_uri')
    max_hops = data.get('max_hops', 3)
    if start_uri:
        results = knowledge_search.explore_multi_hop(start_uri, max_hops)
        return jsonify(results)
    else:
        return jsonify({'error': 'Start URI required'}), 400

@app.route('/shortest_path', methods=['POST'])
def shortest_path():
    data = request.json
    start_uri = data.get('start_uri')
    end_uri = data.get('end_uri')
    if start_uri and end_uri:
        result = shortest_path_tester.detailed_shortest_path(start_uri, end_uri)
        return jsonify(result)
    else:
        return jsonify({'error': 'Start and end URIs required'}), 400

@app.route('/within_two_hops', methods=['POST'])
def within_two_hops():
    data = request.json
    start_uri = data.get('start_uri')
    if start_uri:
        result = shortest_path_tester.within_two_hops(start_uri)
        return jsonify(result)
    else:
        return jsonify({'error': 'Start URI required'}), 400

@app.route('/advanced_search', methods=['POST'])
def advanced_search():
    data = request.json
    keyword = data.get('keyword')
    if keyword:
        results = knowledge_search.advanced_search(keyword)
        return jsonify(results)
    else:
        return jsonify({'error': 'Keyword required'}), 400

@app.route('/test_db_connection', methods=['GET'])
def test_db_connection():
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            with driver.session() as session:
                result = session.run("RETURN 'Neo4j Connection Successful' AS message")
                message = result.single()["message"]
                return jsonify({"message": message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
