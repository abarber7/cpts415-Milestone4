# cpts415-Milestone4
# Project Milestone 4 - Knowledge-Based Search Engine

## Team: Big Lens Massive Solutions

## Overview
This milestone focuses on creating a prototype of an end-to-end application with a graphical user interface (GUI). Our application integrates a GUI with a Neo4j NoSQL database and utilizes Hadoop/Spark for scalable data processing. This document provides a comprehensive overview of the prototype, its functionality, and the technologies used.

## User Interface and Data Visualization
The user interface (UI) of our application allows users to interact with the knowledge graph database. It is designed to be intuitive and interactive, supporting both input from users and dynamic data visualization.

The following are the key components of the UI:

1. **Knowledge-Based Subgraph Search**:
   - This section allows users to enter a keyword and perform a search in the Neo4j knowledge graph database.
   - Results are displayed in a paginated list, showing relevant entities, relationships, and related entities.
   - Users can click on a result to visualize the subgraph, which provides a graphical representation of the connections between entities.

2. **Find Similar Entities**:
   - Users can input an entity URI to find similar entities based on shared relationships.
   - The output includes a list of entities that share similar characteristics or relationships, helping users explore connected nodes within the graph.

3. **Find Similarity Between Two Entities**:
   - Users can input two entity URIs to find the similarity between them.
   - The similarity score is calculated using cosine similarity based on shared neighbors or relationships.

4. **Graph Visualization**:
   - Upon selecting an entity, users can visualize the connections between nodes in an interactive graph view.
   - The visualization is limited to 100 nodes to ensure performance efficiency and clarity.

## User Queries and Results
The following are the primary user queries supported by our application and the corresponding results:

1. **Subgraph Search**:
   - Input: A keyword.
   - Output: A list of entities and relationships that match the keyword, displayed in a paginated format.

2. **Find Similar Entities**:
   - Input: A reference entity URI.
   - Output: A list of similar entities, showing the relationships shared with the reference entity.

3. **Entity Similarity Calculation**:
   - Input: Two entity URIs.
   - Output: A similarity score between the two entities, indicating the degree of relationship based on shared connections.

4. **Graph Exploration**:
   - Users can interactively explore a visual representation of the graph, limited to a specified number of nodes for optimal performance.

## Source Code
The source code for the application prototype, including the GUI, data ingestion, data query, and analytics algorithms, is provided in a separate Zip file. The Zip file includes:

- **app.py**: The main application logic connecting the Flask web server with Neo4j interactions.
- **HTML/JavaScript**: Frontend code for rendering the user interface and visualizing graph data.
- **Neo4j Scripts**:
  - `node_similarity.py`: For calculating similarity scores between nodes.
  - `similar_search.py`: For advanced similarity searches.
  - `subgraph_search.py`: For searching subgraphs based on keywords.
  - `within_two.py`: For multi-hop exploration of the graph.

## Installation and Usage
1. **Requirements**:
   - Python 3.x
   - Flask 3.0.3
   - Neo4j Python Driver
   - Neo4j Database (Local or Cloud)
   - Hadoop/Spark framework

2. **Setup**:
   - Install the required Python packages using `pip install -r requirements.txt`.
   - Update the `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` values in `app.py` with your Neo4j instance credentials.
   - Run the application: `python app.py`.
   - Access the application at `http://localhost:5000`.

3. **Usage**:
   - Use the UI to perform searches, calculate entity similarities, and visualize the graph data.
   - Navigate between search results using pagination controls.

