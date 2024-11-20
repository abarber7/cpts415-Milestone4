from neo4j import GraphDatabase
from flask import Flask, request, jsonify

app = Flask(__name__)

class AutoFill:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def get_autofill(self, input_text):
        # Updated Cypher query to match nodes by 'rdfs__label'
        with self.driver.session() as session:
            query = """
            MATCH (n:Resource)
            WHERE n.rdfs__label STARTS WITH $input
            RETURN n.rdfs__label AS suggestion
            LIMIT 10
            """
            # Execute query with input_text as the parameter
            result = session.run(query, input=input_text)

            # Extracting the 'suggestion' field from the query result
            return [record["suggestion"] for record in result]

# Neo4j credentials
auto_fill = AutoFill("neo4j://localhost:7687", "neo4j", "12345678")

@app.route('/autofill', methods=['GET'])
def autofill():
    # Getting the query
    query = request.args.get('query', '')
    if query:
        # Fetch suggestions using the AutoFill class
        suggestions = auto_fill.get_autofill(query)
        return jsonify(suggestions)  # JSON response with the list of suggestions
    else:
        return jsonify([])  # JSON response with an empty list

if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        auto_fill.close()
