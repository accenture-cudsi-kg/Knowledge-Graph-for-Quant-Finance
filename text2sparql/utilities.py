# -*- coding: utf-8 -*-

from finbert_embedding.embedding import FinbertEmbedding
finbert = FinbertEmbedding()
from deeppavlov import build_model
template_matching_model = build_model('query_pr', download=True)
#print("template_matching_uploaded")
import spacy
import numpy as np

nlp = spacy.load("en_core_web_sm")

import re
import csv
import pandas as pd
import requests


import xgboost as xgb
from xgboost.sklearn import XGBClassifier

import string
import re
#import sister
import pickle
import numpy as np
from scipy.spatial.distance import cosine
from fuzzywuzzy import fuzz


#file_name = "/content/gdrive/MyDrive/Capstone/t2s/XGB_template_classifier.pkl"

XGB_classifier_file_name = "XGB_template_classifier.pkl"
XGB_template_classifier = pickle.load(open(XGB_classifier_file_name, "rb"))

with open("allennlp_relations_embeddings.pkl", "rb") as f: # "rb" because we want to read in binary mode
    allennlp_relation_embeddings = pickle.load(f)

with open("allennlp_entities_embeddings.pkl", "rb") as f: # "rb" because we want to read in binary mode
    allennlp_entity_embeddings = pickle.load(f)

import json

# loading ontologies
with open("allennlp_ontology.json", 'r') as f:
  allennlp_ontology = json.load(f)
allennlp_relations=list(allennlp_ontology["relation"].keys())

allennlp_entities_ontology=list(allennlp_ontology["entities"].keys())


with open("stanford_relations_embeddings.pkl", "rb") as f: # "rb" because we want to read in binary mode
    stanford_relation_embeddings = pickle.load(f)

with open("stanford_entities_embeddings.pkl", "rb") as f: # "rb" because we want to read in binary mode
    stanford_entity_embeddings = pickle.load(f)

import json

# loading ontologies
with open("stanfordopenie_ontology.json", 'r') as f:
  stanford_ontology = json.load(f)
stanford_relations=list(stanford_ontology["relation"].keys())
stanford_entities_ontology=list(stanford_ontology["entities"].keys())



bert_template={4:["SELECT (count(*) as? count) WHERE {<http://crypto.org/ENTITY_CLASS/ENTITY><http://crypto.org/RELATION_CLASS/RELATION> ?o.}",
                  "SELECT (count(*) as? count) WHERE {?s <http://crypto.org/RELATION_CLASS/RELATION> <http://crypto.org/ENTITY_CLASS/ENTITY>.}"]
            ,5:""}
XGB_template={2:[1,"SELECT DISTINCT ?o WHERE { <http://crypto.org/ENTITY_CLASS/ENTITY> <http://crypto.org/RELATION_CLASS/RELATION> ?o.}",
                 "SELECT DISTINCT ?s WHERE { ?s <http://crypto.org/RELATION_CLASS/RELATION> <http://crypto.org/ENTITY_CLASS/ENTITY>.}"],
           16:[2,"SELECT DISTINCT ?o WHERE { <http://crypto.org/SUBJECT1_CLASS/SUBJECT1><http://crypto.org/RELATION1_CLASS/RELATION1> ?o. <http://crypto.org/SUBJECT2_CLASS/SUBJECT2><http://crypto.org/RELATION2_CLASS/RELATION2> ?o. }"],
           305:[2,""]}
ner = spacy.load('en_core_web_trf')





# Step 1: Query Template classification

def clean_query(query):
  doc = nlp(query)
  
  #Lemmatization
  lemmatized_query=""
  for token in doc:
    if "'" not in token.text:
      lemmatized_query=lemmatized_query+token.lemma_+" "
    else:
      lemmatized_query=lemmatized_query+token.text+" "

  # Remove punctuations
  cleaned_query=re.sub(r"[^\w\d'\s]+","",lemmatized_query)
  return cleaned_query

def get_ft_vectors(cleaned_query):
  # return embedder(cleaned_query)
  tensor_list= finbert.sentence_vector(cleaned_query)
  vector=[]
  for t in tensor_list:
    vector.append(t.numpy())
  return vector


def template_classification(query):
  #print("here")
  bert_class=int(template_matching_model([query])[0])
  #print(bert_class)
  if bert_class == 4 or bert_class== 5:
    sql_template=bert_template[bert_class]
    return bert_class,1,sql_template

  else:
    # print("out")
    cleaned_query=clean_query(query)
    query_vector=pd.DataFrame(get_ft_vectors(cleaned_query)).T
    #print("got vector")
    label=XGB_template_classifier.predict(query_vector)[0]
    # print(label)
    prob=np.max(XGB_template_classifier.predict_proba(query_vector))
    if prob>=0.75:
     
      n_entities=XGB_template[label][0]
      # print(n_entities)
      sparql_templates=XGB_template[label][1:]
      # print(sparql_templates)
      return label,n_entities, sparql_templates
    else:
      return 1,100,"SELECT DISTINCT ?p ?o WHERE { <http://crypto.org/ENTITY_CLASS/ENTITY> ?p ?o.}"


# Step 2: Relation extraction

def clean_query_for_sim(cleaned_query):
  cleaned_query=cleaned_query.replace("List ","").replace("list ","")
  doc = nlp(cleaned_query)
  hyper_cleaned_query=""

  for token in doc:
    if token.lemma_=="write":
      return "author"
    if token.pos_ == "VERB":
      hyper_cleaned_query=hyper_cleaned_query+token.lemma_+" "

  if hyper_cleaned_query=="":
    for token in doc:
      if token.pos_ == "NOUN":
        hyper_cleaned_query=hyper_cleaned_query+token.lemma_+" "

  return hyper_cleaned_query.strip()

def get_finbert_embeddings(text):
  if len(text.split())>1:
    tensor_list= finbert.sentence_vector(text)
  else :
    tensor_list= finbert.word_vector(text)

  vector=[]
  for t in tensor_list:
    vector.append(t.numpy())
  return vector

def get_single_relation(query,ontology):
    
  if ontology=="allen":
      relation_embeddings=allennlp_relation_embeddings
      relations=allennlp_relations
      ontology=allennlp_ontology
  else:
      relation_embeddings=stanford_relation_embeddings
      relations=stanford_relations
      
      ontology=stanford_ontology

  
  hyper_cleaned_query=clean_query_for_sim(query)
  print(hyper_cleaned_query)
  fuzzy_score=[]
  for relation in relations:
    score=fuzz.token_set_ratio(hyper_cleaned_query,relation)
    fuzzy_score.append(score)
  if max(fuzzy_score)>85:
    #print(relation,hyper_cleaned_query,score)
    relation= relations[fuzzy_score.index(max(fuzzy_score))]
    print(ontology["relation"][relation])
    #print(relation, ontology["relation"][relation])
    return relation,ontology["relation"][relation]


  query_finbert_vector=get_finbert_embeddings(hyper_cleaned_query)
  query_relation_score=[]
  for i,embedding in enumerate(relation_embeddings):
    score=1-cosine(embedding, query_finbert_vector)
    query_relation_score.append(score)
    #print(relations[i],score)

  #print(max(query_relation_score))
  if max(query_relation_score)>0.80:
    relation= relations[query_relation_score.index(max(query_relation_score))]
    
    return relation, ontology["relation"][relation]
  else:
    return "Not found", "Not found"


# Step 3: Entity extraction


def map_entity(extracted_entity,ontology):
  if ontology=="allen":
      entity_embeddings=allennlp_entity_embeddings
      entities_ontology=allennlp_entities_ontology
      ontology=allennlp_ontology
  else:
      entity_embeddings=stanford_entity_embeddings 
      entities_ontology=stanford_entities_ontology
      ontology=stanford_ontology
  
  fuzzy_score=[]
  for onto_entity in entities_ontology:
    score=fuzz.token_set_ratio(onto_entity,extracted_entity)
    fuzzy_score.append(score)
  
  if max(fuzzy_score)>85:
    #print(relation,hyper_cleaned_query,score)
    onto_entity= entities_ontology[fuzzy_score.index(max(fuzzy_score))] 
    return onto_entity,ontology["entities"][onto_entity]
 

  entity_finbert_vector=get_finbert_embeddings(extracted_entity)
  # print(len(entity_finbert_vector))
  entity_onto_score=[]
  for i,embedding in enumerate(entity_embeddings):
    # print(len(embedding))
  #  if len(embedding)==3:
      # print(embedding)
      # print(entities[i])
      score=1-cosine(embedding, entity_finbert_vector)
      entity_onto_score.append(score)
    #print(relations[i],score)

  #print(max(query_relation_score))
  if max(entity_onto_score)>0.80:
    onto_entity= entities_ontology[entity_onto_score.index(max(entity_onto_score))]
    return entity,ontology["entities"][onto_entity]
  else:
    return "Not found", "Not found"

# For templates 2 and 4
def get_single_entity(query,ontology):
  # If NER exists that's the entity - simply try mapping it to a class and entity
  doc=ner(query)
  if len(doc.ents)>0:
    entity=str(doc.ents[0])
  else:
    # extract NNPs/NNs
    entity=""
    for token in doc:
      if token.tag_=="NN" or token.tag_=="NNP":
        entity=entity+token.lemma_+" "
  
  if entity=="":
    return "Not found"
  else:
    #print(entity)
    mapped_entity, mapped_entity_class=map_entity(entity,ontology)
    
  return mapped_entity, mapped_entity_class


# For template 1
def get_entities(query,ontology):
  # If NER exists that's the entity - simply try mapping it to a class and entity
  entities=[]
  doc=ner(query)
  if len(doc.ents)>0:
    for entity in doc.ents:
      entities.append(str(entity))

  else:
    # extract NNPs/NNs
    
    for token in doc:
      if token.tag_=="NN" or token.tag_=="NNP":
        entities.append(token.lemma_)
  if len(entities)==0:
    return "Not found"
  else:
    mapped_entities=[]
    mapped_entities_class=[]
    for entity in entities:
      mapped_entities.append(map_entity(entity,ontology)[0])
      mapped_entities_class.append(map_entity(entity,ontology)[1])
  
  # Deleting entities for which no mapped entity could be found in Ontology
  final_mapped_entities=[]
  final_mapped_entities_classes=[]
  for i,mapped_entity in enumerate(mapped_entities):
    if mapped_entity!="Not found":
      final_mapped_entities.append(mapped_entity)
      final_mapped_entities_classes.append(mapped_entities_class[i])


    
  return final_mapped_entities,final_mapped_entities_classes