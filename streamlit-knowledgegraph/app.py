import os
import json
import streamlit as st
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, XSD
from pymantic import sparql
from streamlit_agraph import agraph, Config
from streamlit_agraph.node import Node
from streamlit_agraph.edge import Edge
from helper import query_to_sparql

MAP_FILENAME = {
    'Stanford Open IE': "stanfordopenie",
    'AllenNLP': "allennlp",
}


def generate_graph(model):
    with open(f"json/{model}_filter.json") as f:
        triplets = json.load(f)

    with open(f'json/{model}_ontology.json') as f:
        allKeys = json.load(f)
        entityOnto = allKeys['entities']
        relationOnto = allKeys['relation']

    cryptoBaseUri = "http://crypto.org/"
    allNameSpace = {}
    new_triplets = []
    graph = Graph()
    nm = graph.namespace_manager

    for s, p, o in triplets:
        subjClass = entityOnto[s]
        predClass = relationOnto[p]
        predClass = "_".join(predClass.split()) if len(
            predClass.split()) > 1 else predClass
        objClass = entityOnto[o]
        subjUri = cryptoBaseUri+subjClass+"/"
        predUri = cryptoBaseUri+predClass+"/"
        objUri = cryptoBaseUri+objClass+"/"
        if subjUri not in allNameSpace:
            allNameSpace[subjUri] = Namespace(subjUri)
            prefixSub = subjClass
            nm.bind(prefixSub, allNameSpace[subjUri])

        if objUri not in allNameSpace:
            allNameSpace[objUri] = Namespace(objUri)
            prefixObj = objClass
            nm.bind(prefixObj, allNameSpace[objUri])

        if predUri not in allNameSpace:
            allNameSpace[predUri] = Namespace(predUri)
            prefixPred = predClass
            nm.bind(prefixPred, allNameSpace[predUri])

        if len(s.split()) > 1:
            s = "_".join(s.split())
        if len(o.split()) > 1:
            o = "_".join(o.split())
        if len(p.split()) > 1:
            p = "_".join(p.split())
        s = allNameSpace[subjUri][s]
        o = allNameSpace[objUri][o]
        p = allNameSpace[predUri][p]
        new_triplets.append([s, p, o])
        graph.add((s, p, o))
        graph.add((s, RDF.type, (Literal(subjClass, datatype=XSD.string))))
        graph.add((p, RDF.type, (Literal(predClass, datatype=XSD.string))))
        graph.add((o, RDF.type, (Literal(objClass, datatype=XSD.string))))
    return graph, new_triplets, entityOnto


def retrieve_results(sparql_query, server, entity_onto):
    result = server.query(sparql_query)

    # given an entity, returns triplets that contain the entity
    def gen_triplets_from_entity(triple_type, entity_uri):
        ans = []
        for i in new_triplets:
            if (triple_type == 's' and str(i[0]) == entity_uri) \
                    or (triple_type == 'o' and str(i[2]) == entity_uri):
                ans.append(i)
        return ans

    query_results = []
    for bindings in result['results']['bindings']:
        for rel, val in bindings.items():
            query_results.append({rel: val['value']})

    set_of_entities = set(entity_onto.values())
    final_triplets = []  # contains triplets we need
    flag = False
    for bindings in result['results']['bindings']:
        for rel, val in bindings.items():
            if 's' == rel or 'o' == rel:
                flag = True
                entity_uri = val['value']
                if len(entity_uri.split("/")) == 5:
                    entity_type = entity_uri.split("/")[-2]
                    # final_triplets.extend(
                    #     gen_triplets_from_entity(rel, entity_uri))
                    if entity_type in set_of_entities:
                        final_triplets.extend(
                            gen_triplets_from_entity(rel, entity_uri))

    # def allTrip(val):
    #     ans = []
    #     for i in new_triplets:
    #         if str(i[0]) == val or str(i[2]) == val:
    #             if not str(i[0]) == str(i[2]):
    #                 ans.append(i)
    #     return ans
    # allEnt = list(set(list(entity_onto.values())))
    # finalTrip = []  # contains triplets we need
    # for b in result['results']['bindings']:
    #     if 's' in b.keys() or 'o' in b.keys():
    #         flag = True
    #         for ele in list(b.values()):
    #             temp = ele['value']
    #             if len(temp.split("/")) == 5:
    #                 newTemp = temp.split("/")[-2]
    #                 if newTemp in allEnt:
    #                     finalTrip.extend(allTrip(temp))

    final_dict = {}
    final_dict['result'] = query_results
    final_dict['visualization'] = final_triplets
    if flag:
        final_dict['type'] = "entity"
    else:
        final_dict['type'] = "relation"
    return final_dict


def gen_nodes_edges(subgraph):
    nodes, edges = [], []
    nodes_set, edges_set = set(), set()
    for count, (subj, pred, obj) in enumerate(subgraph):
        src = Node(id=str(subj), label=str(subj))
        trg = Node(id=str(obj), label=str(obj))
        edge = Edge(id=count, source=src.id,
                    target=trg.id, title=pred, label=pred)
        if src.id not in nodes_set:
            nodes_set.add(src.id)
            nodes.append(src)
        if trg.id not in nodes_set:
            nodes_set.add(trg.id)
            nodes.append(trg)
        if edge.id not in edges_set:
            edges_set.add(edge.id)
            edges.append(edge)
    return nodes, edges


def clear_text():
    st.session_state["text"] = ""


if __name__ == "__main__":
    st.set_page_config(page_title="KG", page_icon=":tada:", layout="wide")
    st.subheader("Columbia DSI and Accenture")
    st.title("Knowledge Graph for Crypto Papers")
    st.write("----")
    st.subheader("Model Selection")
    model_name = st.radio(
        "Which model do you want to use?",
        ('Stanford Open IE', 'AllenNLP'), on_change=clear_text)
    if model_name:
        # TODO: Change here to run only once - don't have to load graph everytime.
        # Generate graph based on .json files
        graph, new_triplets, entity_onto = generate_graph(
            MAP_FILENAME[model_name])

        # Generate n3 file from RDF graph (one-time)
        # res = graph.serialize(format='n3')
        # n3_out_path = f"n3/test_{MAP_FILENAME[model_name]}.n3"
        # os.makedirs(os.path.dirname(n3_out_path), exist_ok=True)
        # with open(n3_out_path, mode='w') as f:
        #     f.write(res)

        # Set up connection with blazegraph server
        server = sparql.SPARQLServer(
            f'http://localhost:9999/blazegraph/sparql')

        # Load n3 file into blazegraph (one-time)
        cwd = os.getcwd()
        server.update(
            f'load <file://{cwd}/n3/test_{MAP_FILENAME[model_name]}.n3>')

        st.subheader("Query")
        text_input = st.text_input(
            "Enter some text 👇", placeholder="What is Uniswap?", key="text_input")
        if text_input:
            with st.spinner('Converting...'):
                # will be a list of queries
                gen_sparql = query_to_sparql(
                    text_input, MAP_FILENAME[model_name])
            st.success('Done!')
            st.write(f"Converted:\n{gen_sparql}")

            st.write("##")

            # Extract subgraph with the SPARQL query
            result_dict = retrieve_results(gen_sparql, server, entity_onto)

            st.subheader("Answers")
            st.write(result_dict['result'])

            triplets = result_dict['visualization']
            subgraph = []
            for t in triplets:
                s, p, o = tuple(i.split("/")[-1] for i in t)
                subgraph.append((s, p, o))
            if result_dict['type'] == "entity":
                st.subheader("Visualized Graph")
                nodes, edges = gen_nodes_edges(subgraph)
                config = Config(width=500, height=500)
                return_value = agraph(nodes=nodes,
                                      edges=edges,
                                      config=config)
