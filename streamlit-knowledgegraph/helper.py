

def query_to_sparql(query, model):
    if model == "stanfordopenie":
        return """
        SELECT ?s ?p 
        WHERE {
            ?s ?p <http://crypto.org/ORG/Uniswap> .
        }
        """
    return """
        SELECT ?p ?o 
        WHERE {
            <http://crypto.org/PERSON/Ramit_Sawhney> ?p ?o .
        }
    """

    # "below 4107 usd": "CARDINAL",
    # return """
    #     select * where { <http://blazegraph.com/blazegraph> ?p ?o }
    # """
