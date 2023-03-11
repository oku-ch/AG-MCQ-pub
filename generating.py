#############IMPORT PACKAGES##############
import urllib.error
from time import sleep
from multiprocessing import Queue,Process,Pool,TimeoutError
from deepmerge import always_merger
import pickle
#############IMPORT MY-PACKAGES##############
import config
from get_triples import NextTriple_DBWiki
from get_e2larray import G_DictAndLabel

def Generating(ANS_data,word2vec_model,PREFIXES,PREFIXES_Dic,resultsAllDic,WORD_data_Dic,simDic_All,Redirects_Dic):
    E2LArray=[]
    h=1
    try:
        word_data=ANS_data
        resultsO,resultsAllDic=task_with_retry_n(ANS_data,ANS_data,'?o',resultsAllDic,PREFIXES,PREFIXES_Dic)
        resultsS,resultsAllDic=task_with_retry_n(ANS_data,ANS_data,'?s',resultsAllDic,PREFIXES,PREFIXES_Dic)
        E2LArray,WORD_data_Dic,simDic_All=G_DictAndLabel(resultsO,word_data,'?o',h,ANS_data,'Max',E2LArray,WORD_data_Dic,simDic_All,word2vec_model,PREFIXES,PREFIXES_Dic,Redirects_Dic)
        E2LArray,WORD_data_Dic,simDic_All=G_DictAndLabel(resultsS,word_data,'?s',h,ANS_data,'Max',E2LArray,WORD_data_Dic,simDic_All,word2vec_model,PREFIXES,PREFIXES_Dic,Redirects_Dic)
        h+=1
        for num in range(config.DEPTH-1):
            for e2larray in E2LArray:
                if e2larray.h==h-1:
                    word_data=WORD_data_Dic[e2larray.l2]
                    resultsO,resultsAllDic=task_with_retry_n(ANS_data,word_data,'?o',resultsAllDic,PREFIXES,PREFIXES_Dic)
                    resultsS,resultsAllDic=task_with_retry_n(ANS_data,word_data,'?s',resultsAllDic,PREFIXES,PREFIXES_Dic)
                    E2LArray,WORD_data_Dic,simDic_All=G_DictAndLabel(resultsO,word_data,'?o',h,ANS_data,'Max',E2LArray,WORD_data_Dic,simDic_All,word2vec_model,PREFIXES,PREFIXES_Dic,Redirects_Dic)
                    E2LArray,WORD_data_Dic,simDic_All=G_DictAndLabel(resultsS,word_data,'?s',h,ANS_data,'Max',E2LArray,WORD_data_Dic,simDic_All,word2vec_model,PREFIXES,PREFIXES_Dic,Redirects_Dic)
            h+=1
        return E2LArray,resultsAllDic,WORD_data_Dic,simDic_All
    except urllib.error.HTTPError as error:
        print(error.code)
        print(error.read())
        return E2LArray,resultsAllDic,WORD_data_Dic,simDic_All

def task_with_retry_n(ANS_data,WORD_data,flag,resultsAllDic,PREFIXES,PREFIXES_Dic):
    results_DB=[]
    results_Wiki=[]
    if flag+','+WORD_data.redirect not in resultsAllDic.keys():
        for i in range(1,config.CONNECTION_RETRY+1):
          try:
            results_DBWiki,resultsAllDic=NextTriple_DBWiki(ANS_data,WORD_data,flag,resultsAllDic,PREFIXES,PREFIXES_Dic)
          except Exception as error:
            print('error:{error} retry:{i}/{max}'.format(error=error,i=i,max=config.CONNECTION_RETRY))
            sleep(i*5)
          else:
            resultsAllDic[flag+','+WORD_data.redirect]=results_DBWiki
            return results_DBWiki,resultsAllDic
    else:
        return resultsAllDic[flag+','+WORD_data.redirect],resultsAllDic
