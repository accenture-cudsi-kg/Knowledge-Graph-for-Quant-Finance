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
  $ pip install -r requirements.txt
  ```
- Run streamlit app (port:8501)
  ```bash
  $ streamlit run app.py
  ```
  
  
