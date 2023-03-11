#############IMPORT PACKAGES##############
from SPARQLWrapper import SPARQLWrapper
from time import sleep
from multiprocessing import Queue,Process,Pool,TimeoutError
#############IMPORT MY-PACKAGES##############
import config

def getWikiURI(e,PREFIXES):
    return task_with_retry_wikiuri(e,PREFIXES)

def prog_getWikiURI(e,PREFIXES):
    wiki_uri=''      
    sparql=SPARQLWrapper(endpoint=config.ENDPOINT_graphdb,returnFormat='json')         
    sparql.setQuery('''
        '''+PREFIXES+'''
        SELECT DISTINCT ?wd WHERE{
            ?wd owl:sameAs <'''+e+'''> .
        }
    ''')
    try:
        results=sparql.query().convert()
        for result in results['results']['bindings']:
            try:
                uri=result['wd']['value']
                if 'http://wikidata.dbpedia.org/resource/' in uri:
                    wiki_uri=uri.replace('http://wikidata.dbpedia.org/resource/','http://www.wikidata.org/entity/')
                    break
            except:
                pass
    except Exception as error:
        print('prog_getWikiURI')
        print('error:{error}'.format(error=error))
    return wiki_uri

def task_with_retry_wikiuri(e,PREFIXES):
    wiki_uri=''
    for i in range(1,config.CONNECTION_RETRY+1):
          try:
            wiki_uri=prog_getWikiURI(e,PREFIXES)
          except Exception as error:
            print('task_with_retry_wikiuri:uri='+e)
            print('error:{error} retry:{i}/{max}'.format(error=error,i=i,max=config.CONNECTION_RETRY))
            sleep(i*5)
          else:
            return wiki_uri
