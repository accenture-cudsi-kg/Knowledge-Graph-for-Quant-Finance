# streamlit-knowledgegraph
## 🚀 Set up
- Prerequisites
  - Download blazegraph.jar file from [the official blazegraph release 2.1.6](https://github.com/blazegraph/database/releases/tag/BLAZEGRAPH_2_1_6_RC).
  - Install java 9+

- Run a Blazegraph server locally (port:9999)
  
  Go to the folder that has blazegraph.jar. We load a RDF graph into Blazegraph DB so first you need to start java blazegraph server with the following command:
  ```bash
  $ java -server -Xmx4g -jar blazegraph.jar
  ```
- Install python dependencies

  Go to the cloned repo and run this command:
  ```bash
  $ python3 -m venv venv
  $ . venv/bin/activate
  $ pip3 install -r requirements.txt
  ```

- Create `resources` folder
  Download resources for text2sparql.
  ```
  resources
  ├── XGB_template_classifier.pkl
  ├── allennlp_entities_embeddings.pkl
  ├── allennlp_furtherfilter.json
  ├── allennlp_ontology.json
  ├── allennlp_relations_embeddings.pkl
  ├── allennlp_triples.json
  ├── stanfordOpenIE_allfilters.json
  ├── stanford_entities_embeddings.pkl
  ├── stanford_relations_embeddings.pkl
  ├── stanford_triples.json
  ├── stanfordopenie_ontology.json
  └── templates.json
  ```

- Run streamlit app (port:8501)
  ```bash
  $ streamlit run app.py
  ```
  
  
