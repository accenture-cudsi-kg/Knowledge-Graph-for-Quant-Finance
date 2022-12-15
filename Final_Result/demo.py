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
from utilities import *

MAP_FILENAME = {
    'Stanford Open IE': "stanfordopenie",
    'AllenNLP': "allennlp",
}

MAP_FOR_TEXT2SPARQL = {
    'Stanford Open IE': "stanford",
    'AllenNLP': "allen",
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


def retrieve_results(sparql_queries, server, entity_onto):
    # given an entity, returns triplets that contain the entity
    def gen_triplets_from_entity(triple_type, entity_uri):
        ans = []
        for i in new_triplets:
            if (triple_type == 's' and str(i[0]) == entity_uri) \
                    or (triple_type == 'o' and str(i[2]) == entity_uri):
                ans.append(i)
        return ans
    query_results = []
    set_of_entities = set(entity_onto.values())
    final_triplets = []  # contains triplets we need
    flag = False
    for query in sparql_queries:
        result = server.query(query)
        for bindings in result['results']['bindings']:
            for rel, val in bindings.items():
                query_results.append({rel: val['value']})

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


def text2sparql(query, ontology):
    try:
        sparql_query_list = []

        template_id, n_entities, query_templates = template_classification(
            query)
        print(query_templates)

        if template_id == 4 or template_id == 2:
            # print(get_single_relation(query,ontology))
            relation, relation_class = get_single_relation(query, ontology)
            print(relation)

            entity, entity_class = get_single_entity(query, ontology)
            query_validity = check_query_validity(entity, relation, ontology)

            if (entity != "Not found" and relation != "Not found"):
                if query_validity == True:
                    for query_template in query_templates:
                        sparql_query_list.append(query_template.replace("ENTITY_CLASS", entity_class.replace(" ", "_")).replace("ENTITY", entity.replace(
                            " ", "_")).replace("RELATION_CLASS", relation_class.replace(" ", "_")).replace("RELATION", relation.replace(" ", "_")))
                else:
                    q = "SELECT DISTINCT ?p ?o WHERE { <http://crypto.org/ENTITY_CLASS/ENTITY> ?p ?o.}"
                    sparql_query_list.append(q.replace("ENTITY_CLASS", entity_class.replace(
                        " ", "_")).replace("ENTITY", entity.replace(" ", "_")))

            else:
                sparql_query_list.append("Not found")

        if template_id == 1:
            print("hello")
            entities, entities_class = get_entities(query, ontology)

            if len(entities) != 0:
                for i, entity in enumerate(entities):
                    entity_class = entities_class[i]
                    #print(entity, entity_class)
                    sparql_query_list.append(query_templates.replace("ENTITY_CLASS", entity_class.replace(
                        " ", "_")).replace("ENTITY", entity.replace(" ", "_")))
            else:
                sparql_query_list.append("Not found")

        if template_id == 5:
            relation, relation_class = get_single_relation(query, ontology)
            entities, entities_class = get_entities(query, ontology)
            aggregation = get_aggregation_method(query)
            # print(aggregation)
            if (relation != "Not found" and relation != "Not found"):
                for i, entity in enumerate(entities):
                    query_validity = check_query_validity(
                        entity, relation, ontology)
                    entity_class = entities_class[i]

                    if query_validity == True:
                        for agg_method in aggregation:
                            # print(agg_method)
                            sparql_query_list.append(query_templates[0].replace("ENTITY_CLASS", entity_class.replace(" ", "_")).replace("ENTITY", entity.replace(" ", "_")).replace(
                                "RELATION_CLASS", relation_class.replace(" ", "_")).replace("RELATION", relation.replace(" ", "_")).replace("AGGREGATION_METHOD", agg_method.replace(" ", "_")))
                    else:
                        q = "SELECT DISTINCT ?p ?o WHERE { <http://crypto.org/ENTITY_CLASS/ENTITY> ?p ?o.}"
                        sparql_query_list.append(q.replace("ENTITY_CLASS", entity_class.replace(
                            " ", "_")).replace("ENTITY", entity.replace(" ", "_")))

            else:
                sparql_query_list.append("Not found")

    except:
        entities, entities_class = get_entities(query, ontology)
        q = "SELECT DISTINCT ?p ?o WHERE { <http://crypto.org/ENTITY_CLASS/ENTITY> ?p ?o.}"

        if len(entities) != 0:
            for i, entity in enumerate(entities):
                entity_class = entities_class[i]
                #print(entity, entity_class)
                sparql_query_list.append(q.replace("ENTITY_CLASS", entity_class.replace(
                    " ", "_")).replace("ENTITY", entity.replace(" ", "_")))
        else:
            sparql_query_list.append("Not found")

    return sparql_query_list
# def text2sparql(query, ontology):

#     # if
#     sparql_query_list = []

#     template_id, n_entities, query_templates = template_classification(query)
#     # print(query_templates)

#     if template_id == 4 or template_id == 2:
#         # print(get_single_relation(query,ontology))
#         relation, relation_class = get_single_relation(query, ontology)
#         # print(relation)

#         entity, entity_class = get_single_entity(query, ontology)
#         query_validity = check_query_validity(entity, relation, ontology)

#         if (entity != "Not found" and relation != "Not found"):
#             if query_validity == True:
#                 for query_template in query_templates:
#                     sparql_query_list.append(query_template.replace("ENTITY_CLASS", entity_class.replace(" ", "_")).replace("ENTITY", entity.replace(
#                         " ", "_")).replace("RELATION_CLASS", relation_class.replace(" ", "_")).replace("RELATION", relation.replace(" ", "_")))
#             else:
#                 q = "SELECT DISTINCT ?p ?o WHERE { <http://crypto.org/ENTITY_CLASS/ENTITY> ?p ?o.}"
#                 sparql_query_list.append(q.replace("ENTITY_CLASS", entity_class.replace(
#                     " ", "_")).replace("ENTITY", entity.replace(" ", "_")))

#         else:
#             sparql_query_list.append("Not found")

#     if template_id == 1:
#         # print("hello")
#         entities, entities_class = get_entities(query, ontology)

#         if len(entities) != 0:
#             for i, entity in enumerate(entities):
#                 entity_class = entities_class[i]
#                 #print(entity, entity_class)
#                 sparql_query_list.append(query_templates.replace("ENTITY_CLASS", entity_class.replace(
#                     " ", "_")).replace("ENTITY", entity.replace(" ", "_")))
#         else:
#             sparql_query_list.append("Not found")

#     if template_id == 5:
#         relation, relation_class = get_single_relation(query, ontology)
#         entities, entities_class = get_entities(query, ontology)
#         aggregation = get_aggregation_method(query)
#         # print(aggregation)
#         if (relation != "Not found" and relation != "Not found"):
#             for i, entity in enumerate(entities):
#                 query_validity = check_query_validity(
#                     entity, relation, ontology)
#                 entity_class = entities_class[i]

#                 if query_validity == True:
#                     for agg_method in aggregation:
#                         # print(agg_method)
#                         sparql_query_list.append(query_templates[0].replace("ENTITY_CLASS", entity_class.replace(" ", "_")).replace("ENTITY", entity.replace(" ", "_")).replace(
#                             "RELATION_CLASS", relation_class.replace(" ", "_")).replace("RELATION", relation.replace(" ", "_")).replace("AGGREGATION_METHOD", agg_method.replace(" ", "_")))
#                 else:
#                     q = "SELECT DISTINCT ?p ?o WHERE { <http://crypto.org/ENTITY_CLASS/ENTITY> ?p ?o.}"
#                     sparql_query_list.append(q.replace("ENTITY_CLASS", entity_class.replace(
#                         " ", "_")).replace("ENTITY", entity.replace(" ", "_")))

#         else:
#             sparql_query_list.append("Not found")

#     return sparql_query_list


def clear_text():
    st.session_state["text_input"] = ""


if __name__ == "__main__":
    with open("alex_ques.json") as in_f:
        d = json.load(in_f)
        with open("alex_results.json", "w") as out_f:
            list_results = []
            questions = d
            for question in questions:
                model_names = ['Stanford Open IE', 'AllenNLP']
                for model_name in model_names:
                    print(model_name)
                    graph, new_triplets, entity_onto = generate_graph(
                        MAP_FILENAME[model_name])

                    server = sparql.SPARQLServer(
                        f'http://localhost:9999/blazegraph/sparql')

                    cwd = os.getcwd()
                    server.update(
                        f'load <file://{cwd}/n3/test_{MAP_FILENAME[model_name]}.n3>')

                    text_input = question
                    res = {}
                    gen_sparqls = text2sparql(
                        text_input, MAP_FOR_TEXT2SPARQL[model_name])
                    if len(gen_sparqls) == 0 or gen_sparqls[0] == "Not found":
                        res["question"] = question
                        res["model"] = model_name
                        res["queries"] = "Not found"
                        list_results.append(res)
                        continue
                    result_dict = retrieve_results(
                        gen_sparqls, server, entity_onto)

                    res["question"] = question
                    res["model"] = model_name
                    res["queries"] = gen_sparqls
                    res["query_results"] = result_dict['result']
                    res["bool_visualization"] = result_dict['type'] == "entity"

                    triplets = result_dict['visualization']
                    subgraph = []
                    for t in triplets:
                        s, p, o = tuple(i.split("/")[-1] for i in t)
                        subgraph.append((s, p, o))
                    if result_dict['type'] == "entity":
                        res["triplets"] = subgraph
                    list_results.append(res)
            json.dump(list_results, out_f)
