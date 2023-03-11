#############IMPORT PACKAGES##############
from SPARQLWrapper import SPARQLWrapper
#############IMPORT MY-PACKAGES##############
import config
from get_wikidata_uri import getWikiURI


def NextTriple_DBWiki(ANS_data,WORD_data,flag,resultsAllDic,PREFIXES,PREFIXES_Dic):
    results=[]
    triple_line=''
    if flag=='?o':
        triple_line='''
            ?target_uri rdfs:label \"'''+WORD_data.redirect+'''\"@ja .
            ?target_uri ?p ?o .
            '''
    elif flag=='?s':
        triple_line='''
            ?target_uri rdfs:label \"'''+WORD_data.redirect+'''\"@ja .
            ?s ?p ?target_uri .
            '''
    sparql=SPARQLWrapper(endpoint=config.ENDPOINT_graphdb,returnFormat='json')     
    sparql.setQuery('''     
        '''+PREFIXES+'''
        SELECT DISTINCT '''+flag+''' ?label ?p ?p_label ?target_uri WHERE{
           '''+triple_line+'''
           '''+flag+''' rdfs:label ?label .
           OPTIONAL{
                ?p rdfs:label ?p_label .
           }
           OPTIONAL{
                ?p_ wikibase:directClaim ?p .
                ?p_ rdfs:label ?p_label .
           }  
            FILTER (?p!=<http://dbpedia.org/ontology/wikiPageWikiLink>)
            FILTER (?p!=<http://dbpedia.org/ontology/wikiPageRedirects>)
            FILTER (?p!=<http://www.w3.org/2002/07/owl#sameAs>)
            FILTER (?p!=<http://dbpedia.org/ontology/wikiPageDisambiguates>)
            FILTER(lang(?label)='ja').
            FILTER(lang(?p_label)='ja').
        }
    ''')
    sparql.addParameter("infer",config.infer_flg)
    #try:
    results=sparql.query().convert()
    resultsAllDic=appendResultsAll(ANS_data,results,WORD_data.redirect,flag,resultsAllDic)
    #except Exception as error:
    #    print('NextTriple_DBWiki:word='+WORD_data.redirect)
    #    print('error:{error}'.format(error=error))
    return results,resultsAllDic

def appendResultsAll(ANS_data,results,word,flag,resultsAllDic):
    if flag+','+word not in resultsAllDic.keys():
        resultsAllDic[flag+','+word]=results
        #########################################
        #Option)write triples_infer.csv
        with open('triples_infer/triples_infer_'+ANS_data.redirect+'.csv','a') as tf:
            for result in results['results']['bindings']:
                if flag=='?s':
                    tf.write(result[flag.replace('?','')]['value']+','+result['p']['value']+','+result['target_uri']['value']+'\n')
                elif flag=='?o':
                    tf.write(result['target_uri']['value']+','+result['p']['value']+','+result[flag.replace('?','')]['value']+'\n')
        #########################################
    return resultsAllDic

def ANS_NextTriple_DBWiki(ANS_data,WORD_data,flag,PREFIXES,PREFIXES_Dic):
    results=[]
    triple_line=''
    if flag=='?o':
        triple_line='''
            ?target_uri_word rdfs:label \"'''+WORD_data.redirect+'''\"@ja .
            ?target_uri_ans rdfs:label \"'''+ANS_data.redirect+'''\"@ja .
            ?target_uri_word ?p ?target_uri_ans .
            '''
    elif flag=='?s':
        triple_line='''
            ?target_uri_word rdfs:label \"'''+WORD_data.redirect+'''\"@ja .
            ?target_uri_ans rdfs:label \"'''+ANS_data.redirect+'''\"@ja .
            ?target_uri_ans ?p ?target_uri_word .
            '''
    sparql=SPARQLWrapper(endpoint=config.ENDPOINT_graphdb,returnFormat='json')     
    sparql.setQuery('''     
        '''+PREFIXES+'''
        SELECT DISTINCT ?p ?p_label WHERE{
           '''+triple_line+'''
           OPTIONAL{
                ?p rdfs:label ?p_label .
           }
           OPTIONAL{
                ?p_ wikibase:directClaim ?p .
                ?p_ rdfs:label ?p_label .
           }  
            FILTER (?p!=<http://dbpedia.org/ontology/wikiPageWikiLink>)
            FILTER (?p!=<http://dbpedia.org/ontology/wikiPageRedirects>)
            FILTER (?p!=<http://www.w3.org/2002/07/owl#sameAs>)
            FILTER (?p!=<http://dbpedia.org/ontology/wikiPageDisambiguates>)
            FILTER(lang(?p_label)='ja').
        }
    ''')
    sparql.addParameter("infer",config.infer_flg)
    #try:
    results=sparql.query().convert()
    #except Exception as error:
    #    print('ANS_NextTriple_DBWiki:word='+WORD_data.redirect)
    #    print('error:{error}'.format(error=error))
    return results

