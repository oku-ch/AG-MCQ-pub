#############IMPORT PACKAGES##############
import urllib.error
from time import sleep
from multiprocessing import Queue,Process,Pool,TimeoutError
from deepmerge import always_merger
import pickle
#############IMPORT MY-PACKAGES##############
import config
from get_triples import ANS_NextTriple_DBWiki
from get_redirects import getsameAs

def checkE2LArray(E2LArray,ANS_data,word2vec_model,PREFIXES,PREFIXES_Dic,WORD_data_Dic,ir):
	exist_labels=[ANS_data.redirect]
	for e2larray in E2LArray:
		if e2larray.l1 not in exist_labels:
			word_data=WORD_data_Dic[e2larray.l1]
			resultsO1_a=task_with_retry_a(ANS_data,word_data,'?o',PREFIXES,PREFIXES_Dic)
			resultsS1_a=task_with_retry_a(ANS_data,word_data,'?s',PREFIXES,PREFIXES_Dic)
			E2LArray=ANS_CheckLinks(resultsO1_a,ANS_data,word_data,'-','?o','Max',E2LArray,WORD_data_Dic,PREFIXES)
			E2LArray=ANS_CheckLinks(resultsS1_a,ANS_data,word_data,'-','?s','Max',E2LArray,WORD_data_Dic,PREFIXES)
			exist_labels.append(e2larray.l1)
		if e2larray.l2 not in exist_labels:
			word_data=WORD_data_Dic[e2larray.l2]
			resultsO2_a=task_with_retry_a(ANS_data,word_data,'?o',PREFIXES,PREFIXES_Dic)
			resultsS2_a=task_with_retry_a(ANS_data,word_data,'?s',PREFIXES,PREFIXES_Dic)
			E2LArray=ANS_CheckLinks(resultsO2_a,ANS_data,word_data,'-','?o','Max',E2LArray,WORD_data_Dic,PREFIXES)
			E2LArray=ANS_CheckLinks(resultsS2_a,ANS_data,word_data,'-','?s','Max',E2LArray,WORD_data_Dic,PREFIXES)
			exist_labels.append(e2larray.l2)
	E2LArray=getGraph_minimum(ANS_data,E2LArray,ir)
	return E2LArray,WORD_data_Dic

def task_with_retry_a(ANS_data,WORD_data,flag,PREFIXES,PREFIXES_Dic):
    results_DB=[]
    results_Wiki=[]
    for i in range(1,config.CONNECTION_RETRY+1):
      try:
        results_DBWiki=ANS_NextTriple_DBWiki(ANS_data,WORD_data,flag,PREFIXES,PREFIXES_Dic)
      except Exception as error:
        print('error:{error} retry:{i}/{max}'.format(error=error,i=i,max=config.CONNECTION_RETRY))
        sleep(i*5)
      else:
        return results_DBWiki

def ANS_CheckLinks(resultsX,ANS_data,WORD_data,h,flag,MinorMax,E2LArray,WORD_data_Dic,PREFIXES):
	if len(resultsX)!=0:
		for result in resultsX['results']['bindings']:
			propuri=result['p']['value']
			propvalue=result['p_label']['value']
			if propvalue not in WORD_data_Dic.keys():
				word_data=config.word_data('','','','','','','')
				word_data.redirect=propvalue
				if 'dbpedia' in propuri:
					word_data.uri_dbpedia=propuri
					word_data.sameas=getsameAs(word_data.redirect,word_data.uri_dbpedia,PREFIXES)
				elif 'wikidata' in propuri:
					word_data.uri_wikidata=propuri
					word_data.sameas=getsameAs(word_data.redirect,word_data.uri_wikidata,PREFIXES)
				WORD_data_Dic[word_data.redirect]=word_data
			cal='-'
			exist_flg=False
			for e2larray in E2LArray:
				if (e2larray.l1==WORD_data.redirect and e2larray.l2==ANS_data.redirect) or (e2larray.l1==ANS_data.redirect and e2larray.l2==WORD_data.redirect):
					if propvalue==e2larray.pl or propvalue in WORD_data_Dic[e2larray.pl].sameas or propvalue==e2larray.p:
						exist_flg=True
			if exist_flg==False:
				e2larray_list=config.E2LArray_list('','','','','','','','','','')
				e2larray_list.e1=WORD_data.uri_dbpedia+'||'+WORD_data.uri_wikidata
				e2larray_list.l1=WORD_data.redirect
				e2larray_list.e2=ANS_data.uri_dbpedia+'||'+ANS_data.uri_wikidata
				e2larray_list.l2=ANS_data.redirect
				e2larray_list.p=propuri
				e2larray_list.pl=propvalue
				e2larray_list.h=h
				e2larray_list.flag=flag
				e2larray_list.sim=cal
				e2larray_list.minormax=MinorMax
				E2LArray.append(e2larray_list)
	return E2LArray

def getGraph_minimum(ANS_data,E2LArray,ir):
    retE2LArray=[]
    delE2LArray=[]
    for e2larray in E2LArray:
        l1=e2larray.l1
        l2=e2larray.l2
        h=e2larray.h
        if h!='-':
            retE2LArray.append(e2larray)
        elif l1==ANS_data.redirect or l2==ANS_data.redirect:
            retE2LArray.append(e2larray)
        else:
            delE2LArray.append(e2larray)
    with open('Graphs_deleted_links/'+str(ir)+'_'+ANS_data.redirect+'_deleted_links.csv','w') as delf:
        if len(delE2LArray)!=0:
            for i,e2larray in enumerate(delE2LArray):
                if i==0:
                    delf.write(str(vars(e2larray)))
                else:
                    delf.write('\n'+str(vars(e2larray)))
    return retE2LArray