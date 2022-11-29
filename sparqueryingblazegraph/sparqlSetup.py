#!/usr/bin/env python
# coding: utf-8

# In[38]:


get_ipython().system('pip install rdflib')
get_ipython().system('pip install pymantic')
get_ipython().system('pip install SPARQLWrapper')


# In[39]:


from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import FOAF , XSD, RDF
import json
from pymantic import sparql

data_onto = './stanfordopenie_ontology.json'
data_triples = './stanfordOpenIE_allfilters.json'


# In[41]:


with open (data_triples) as f:
    triplets = json.load(f)

with open(data_onto) as f:
  allKeys = json.load(f)
  entityOnto = allKeys['entities']
  relationOnto = allKeys['relation']


# In[42]:


cryptoBaseUri = "http://crypto.org/"
allNameSpace = {}
g = Graph()
nm = g.namespace_manager
newTriplets = []

for s, p, o in triplets:
  subjClass = entityOnto[s]
  predClass = relationOnto[p]
  predClass = "_".join(predClass.split()) if len(predClass.split()) > 1 else predClass
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
  g.add((s, p, o))
  newTriplets.append([s,p,o])
  g.add((s, RDF.type, (Literal(subjClass, datatype=XSD.string))))
  g.add((p, RDF.type, (Literal(predClass, datatype=XSD.string))))
  g.add((o, RDF.type, (Literal(objClass, datatype=XSD.string))))


# In[95]:


# JUST PRINTING SOME OF THE CLASSES

# for s, p, o in triplets:
#     subjClass = entityOnto[s]
#     predClass = relationOnto[p]
#     predClass = "_".join(predClass.split()) if len(predClass.split()) > 1 else predClass
#     objClass = entityOnto[o]
#     if "cryptocurrency Bit" in s: 
#         print(s,";", p,";", o,";")
#         print(subjClass,";", predClass,";", objClass,";")


# In[46]:


res = g.serialize(format='n3')
with open('./stanfordopenie.n3', mode = 'w') as f:
  f.write(res)


# In[54]:


# Make the server connection to the local blazegraph
# input: sparql endpoint (this input is fixed)
server = sparql.SPARQLServer('http://localhost:9999/blazegraph/sparql') 

# Update the blazegraph with new triplets saved as stanfordopenie.n3
# input: file path
server.update('load <file:/Users/ridwanolawin/Downloads/stanfordopenie.n3>') 


# In[50]:


# Main function needed
def retrieveResults(sparqlQuery, server = server):
    result = server.query(sparqlQuery)
    def allTrip(val):
        ans = []
        for i in newTriplets:
            if str(i[0]) == val or str(i[2]) == val:
                ans.append(i)
        return ans


    finalAns = []
    for b in result['results']['bindings']:
        for rel, val in b.items():
            finalAns.append(val['value'])

    allEnt = list(set(list(entityOnto.values())))
    finalTrip = [] #contains triplets we need
    flag = False
    for b in result['results']['bindings']:
        if 's' in b.keys() or 'o' in b.keys():
            flag = True
            for ele in list(b.values()):
                temp = ele['value']
                if len(temp.split("/")) == 5:
                    newTemp = temp.split("/")[-2]
                    if newTemp in allEnt:
                        finalTrip.extend(allTrip(temp))

    finalDict = {}
    finalDict['result'] = finalAns
    finalDict['visualization'] = finalTrip
    if flag:
        finalDict['type'] = "entity"
    else:
        finalDict['type'] = "relation"
    return finalDict


# In[ ]:


# list of queries coming from Arnav
for query in listOfQuer:
    finalDictVal = retrieveResults(query, server = server)


# In[ ]:


# Testing on queries from Arnav

# quer = 'select * where {?s CRYPTO:structure_of ?o }'
# quer1 = 'SELECT ?o ?p WHERE {<http://crypto.org/ORG/Dániel_Kondor> ?p ?o.}'
# quer = 'SELECT ?o WHERE {<http://crypto.org/ORG/Dániel_Kondor> ?p ?o.}'
# listOfQuer = [quer, quer1]
# quer = 'SELECT (count(*) as ?count) WHERE {<http://crypto.org/ORG/Dániel_Kondor> <http://crypto.org/IS_AUTHOR_OF/is_author_of> ?o.}'


# quer = 'SELECT (count(?o) as ?count) WHERE {<http://crypto.org/PERSON/Ramit_Sawhney> <http://crypto.org/YIELD/propose> ?o.}'
# result = server.query(quer)

# for b in result['results']['bindings']:
#     print(b)

