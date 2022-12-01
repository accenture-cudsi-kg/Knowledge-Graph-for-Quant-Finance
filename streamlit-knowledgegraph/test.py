from utilities import *


def text2sparql(query, ontology):

    # if
    sparql_query_list = []

    template_id, n_entities, query_templates = template_classification(query)
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

    return sparql_query_list


print(text2sparql("How many papers has Ramit Sawhney authored?", "stanford"))


# import sister
# sentence_embedding = sister.MeanEmbedding(lang="en")
# sentence = "I am a dog."
# vector = sentence_embedding(sentence)
