#############IMPORT PACKAGES##############
from SPARQLWrapper import SPARQLWrapper
from time import sleep
from multiprocessing import Queue,Process,Pool,TimeoutError
from deepmerge import always_merger
#############IMPORT MY-PACKAGES##############
import config

def getRedirects(word,word_e,PREFIXES):
    return task_with_retry_redirects(word,word_e,PREFIXES)

def task_with_retry_redirects(word,word_e,PREFIXES):
    redirect=''
    redirected_list=[]
    for i in range(1,config.CONNECTION_RETRY+1):
        try:
            redirect,redirected_list=prog_getRedirects(word,word_e,PREFIXES)
        except Exception as error:
            print('task_with_retry_redirects:uri='+word_e)
            print('error:{error} retry:{i}/{max}'.format(error=error,i=i,max=config.CONNECTION_RETRY))
            sleep(i*5)
        else:
            return redirect,redirected_list

def prog_getRedirects(word,word_e,PREFIXES):
    redirect=''
    redirected_list=[]
    sparql=SPARQLWrapper(endpoint=config.ENDPOINT_graphdb,returnFormat='json')
    sparql.setQuery('''
        '''+PREFIXES+'''
        SELECT DISTINCT * WHERE{
            <'''+word_e+'''> dbo:wikiPageRedirects ?redirect_e .
            ?redirect_e rdfs:label ?redirect .
            filter(lang(?redirect)="ja"||lang(?redirect)="en")
            OPTIONAL{
                ?redirected_e dbo:wikiPageRedirects ?redirect_e .
                ?redirected_e rdfs:label ?redirected .
                filter(lang(?redirect)="ja"||lang(?redirect)="en")
            }
        }
    ''')
    try:
        results=sparql.query().convert()
        for result in results['results']['bindings']:
            try:
                redirect=result['redirect']['value']
            except:
                pass
            redirected=''
            try:
                redirected=result['redirected']['value']
                if redirected!='' and redirected not in redirected_list:
                     redirected_list.append(redirected)(result['redirected']['value'])
            except:
                pass
    except Exception as error:
        print('prog_getRedirects')
        print('error:{error}'.format(error=error))
           
    if redirect=='':
        redirect=word
        sparql=SPARQLWrapper(endpoint=config.ENDPOINT_graphdb,returnFormat='json')
        sparql.setQuery('''
        '''+PREFIXES+'''
        SELECT DISTINCT ?redirected WHERE{
            ?redirected_e dbo:wikiPageRedirects <'''+word_e+'''> .
            ?redirected_e rdfs:label ?redirected .
            filter(lang(?redirect)="ja"||lang(?redirect)="en")
            }
        ''')
        try:
            results=sparql.query().convert()
            for result in results['results']['bindings']:
                redirected=''
                try:
                    redirected=result['redirected']['value']
                    if redirected!='' and redirected not in redirected_list:
                        redirected_list.append(redirected)
                except:
                    pass
        except Exception as error:
            print('prog_getRedirects')
            print('error:{error}'.format(error=error))
    return redirect,redirected_list

def getsameAs(word,word_e,PREFIXES):
    return task_with_retry_sameas(word,word_e,PREFIXES)

def task_with_retry_sameas(word,word_e,PREFIXES):
    sameAs_list=[]
    for i in range(1,config.CONNECTION_RETRY+1):
        try:
            sameAs_list=prog_getsameAs(word,word_e,PREFIXES)
        except Exception as error:
            print('task_with_retry_sameas:uri='+word_e)
            print('error:{error} retry:{i}/{max}'.format(error=error,i=i,max=config.CONNECTION_RETRY))
            sleep(i*5)
        else:
            return sameAs_list

def prog_getsameAs(word,word_e,PREFIXES):
    sameAs_list=[]
    prop_flg=True
    if 'http://www.wikidata.org/prop/direct/' in word_e:
        word_e=word_e.replace('http://www.wikidata.org/prop/direct/','http://wikidata.dbpedia.org/resource/')
    elif 'http://www.wikidata.org/entity/' in word_e:
        word_e=word_e.replace('http://www.wikidata.org/entity/','http://wikidata.dbpedia.org/resource/')
        prop_flg=False
    sparql=SPARQLWrapper(endpoint=config.ENDPOINT_graphdb,returnFormat='json')         
    sparql.setQuery('''     
        '''+PREFIXES+'''
        SELECT DISTINCT * WHERE{
            <'''+word_e+'''> owl:sameAs ?sameas .
            OPTIONAL{
                ?sameas rdfs:label ?sameas_label .
                FILTER(lang(?sameas_label)="ja" || lang(?sameas_label)="en")
            }
            OPTIONAL{
                ?sameas_links owl:sameAs ?sameas .
                ?sameas_links rdfs:label ?sameas_links_label .
                FILTER(lang(?sameas_links_label)="ja" || lang(?sameas_links_label)="en")
            }
        }
    ''')
    try:
        results=sparql.query().convert()
        for result in results['results']['bindings']:
            try:
                sameas=result['sameas_label']['value']
                if 'http://www.wikidata.org/prop/direct/' in sameas and prop_flg==True:
                    sameas=sameas.replace('http://wikidata.dbpedia.org/resource/','http://www.wikidata.org/prop/direct/')
                elif 'http://www.wikidata.org/entity/' in sameas and prop_flg==False:
                    sameas=sameas.replace('http://wikidata.dbpedia.org/resource/','http://www.wikidata.org/entity/')
                if sameas not in sameAs_list:
                    sameAs_list.append(sameas)
            except:
                pass
            try:
                sameas_links=results['sameas_links_label']['value']
                if sameas_links not in sameAs_list:
                    sameAs_list.append(same)
            except:
                pass
    except Exception as error:
        print('prog_getsameAs')
        print('error:{error}'.format(error=error))
    return sameAs_list

def check_Redirects(check_word,check_word_e,PREFIXES,Redirects_Dic):
    redirected_list=[]
    if check_word not in Redirects_Dic.keys():
        redirect,redirected_list=prog_getRedirects(check_word,check_word_e,PREFIXES)
        if redirect not in Redirects_Dic.keys():
            Redirects_Dic[redirect]=redirect
        for redirected in redirected_list:
            if redirected not in Redirects_Dic.keys():
                Redirects_Dic[redirected]=redirect
    else:
        for k,v in Redirects_Dic.items():
            if k!=v and v==Redirects_Dic[check_word]:
                redirected_list.append(v)
    return redirected_list,Redirects_Dic
