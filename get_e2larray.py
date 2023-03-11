#############IMPORT PACKAGES##############
from tqdm import tqdm
import csv
#############IMPORT MY-PACKAGES##############
import config
from get_redirects import getRedirects,getsameAs,check_Redirects
from calc_dist import check_word2vec,dist_word2vec,extract_date
from get_wikidata_uri import getWikiURI

def appendE2LArray(ret_connection,MinorMax,results,WORD_data,flag,h,ANS_data,E2LArray,WORD_data_Dic,simDic_All,PREFIXES,word2vec_model,Redirects_Dic):
    upCounter=config.LenNodes
    NodeCounter=0
    Fcount=0
    for lep in ret_connection:
        for result in results['results']['bindings']:
            LabelValue=result['label']['value']
            EntityValue=result[flag.replace('?','')]['value']
            PropValue=result['p_label']['value']
            PropURI=result['p']['value']
            if PropValue not in WORD_data_Dic.keys():
                word_data=config.word_data('','','','','','','')
                word_data.redirect=PropValue
                if 'dbpedia' in PropURI:
                    word_data.uri_dbpedia=PropURI
                    word_data.sameas=getsameAs(word_data.redirect,word_data.uri_dbpedia,PREFIXES)
                elif 'wikidata' in PropURI:
                    word_data.uri_wikidata=PropURI
                    word_data.sameas=getsameAs(word_data.redirect,word_data.uri_wikidata,PREFIXES)
                WORD_data_Dic[word_data.redirect]=word_data
            if NodeCounter<upCounter:
                if LabelValue==lep[0] and PropValue==lep[2]:
                    redirected,Redirects_Dic=check_Redirects(LabelValue,EntityValue,PREFIXES,Redirects_Dic)
                    redirect=Redirects_Dic[LabelValue]
                    cal,simDic_All=dist_word2vec(WORD_data,WORD_data_Dic[redirect],simDic_All,word2vec_model)
                    if CompArrays(redirect,ANS_data,E2LArray,WORD_data_Dic):
                        WORD_data_Dic[redirect].sameas=getsameAs(redirect,WORD_data_Dic[redirect].uri_dbpedia,PREFIXES)
                        e2larray_list=config.E2LArray_list('','','','','','','','','','')
                        e2larray_list.e1=WORD_data.uri_dbpedia+'||'+WORD_data.uri_wikidata
                        e2larray_list.l1=WORD_data.redirect
                        e2larray_list.e2=WORD_data_Dic[redirect].uri_dbpedia+'||'+WORD_data_Dic[redirect].uri_wikidata
                        e2larray_list.l2=redirect
                        e2larray_list.p=PropURI
                        e2larray_list.pl=PropValue
                        e2larray_list.h=h
                        e2larray_list.flag=flag
                        e2larray_list.sim=cal
                        e2larray_list.minormax=MinorMax
                        E2LArray.append(e2larray_list)
                        NodeCounter+=1
            else:
                Fcount+=1
    return E2LArray,simDic_All

def G_DictAndLabel(results,WORD_data,flag,h,ANS_data,MinorMax,E2LArray,WORD_data_Dic,simDic_All,word2vec_model,PREFIXES,PREFIXES_Dic,Redirects_Dic):
    simDic={}
    DB_labelList=[]
    Wiki_labelList=[]
    #######################################################
    ##Option) Weights for triples added by rules
    Triples_addedRules_List=[]
    with open(config.Triples_addedRules_path,'r') as triples_f:
        reader=csv.reader(triples_f)
        for row in reader:
            Triples_addedRules_List.append(row)
    #######################################################        
    if results!=[]:
        desc_str=''
        if flag=='?s':
            desc_str='*|h='+str(h)+', triples=\''+flag+' ?p '+WORD_data.redirect+' .\''
        elif flag=='?o':
            desc_str='*|h='+str(h)+', triples=\''+WORD_data.redirect+' ?p '+flag+' .\''
        for result in tqdm(results['results']['bindings'],desc=desc_str):
            flg_rule=False
            label=result['label']['value']
            uri=result[flag.replace('?','')]['value']
            redirected,Redirects_Dic=check_Redirects(label,uri,PREFIXES,Redirects_Dic)
            redirect=Redirects_Dic[label]
            if redirect not in WORD_data_Dic.keys():
                word_data=config.word_data('','','','','','','')
                word_data.redirect=redirect
                word_data.redirected=redirected
                if 'dbpedia' in uri:
                    word_data.uri_dbpedia=uri
                    word_data.uri_wikidata=getWikiURI(uri,PREFIXES)
                elif 'wikidata' in uri:
                    word_data.uri_wikidata=uri
                    word_data.uri_dbpedia=PREFIXES_Dic[config.ANS_O]+redirect.replace(' ','_').replace('（','_（')
                try:
                    cal,simDic_All=check_word2vec(redirect,redirect,simDic_All,word2vec_model)
                    word_data.model=redirect
                except:
                    for redirected_t in redirected:
                        try:
                            cal,simDic_All=check_word2vec(redirected_t,redirected_t,simDic_All,word2vec_model)
                            word_data.model=redirected_t
                        except:
                            pass
                        if word_data.model!='':
                            break
                        else:
                            pass
                WORD_data_Dic[redirect]=word_data
            else:
                pass
            cal,simDic_All=dist_word2vec(WORD_data,WORD_data_Dic[redirect],simDic_All,word2vec_model)
            #######################################################
            ##Option) Weights for triples added by rules\
            propvalue=result['p']['value']
            target_triple=[]
            if flag=='?s':
                target_triple=[WORD_data_Dic[redirect].uri_wikidata,propvalue,WORD_data.uri_wikidata]
            elif flag=='?o':
                target_triple=[WORD_data.uri_wikidata,propvalue,WORD_data_Dic[redirect].uri_wikidata]
            if target_triple in Triples_addedRules_List:
                print('Triples_addedRules_List')
                with open('result_Triples_addedRules_List.csv','a') as rt:
                    rt.write(ANS_data.redirect+':'+','.join(map(str, target_triple))+'\n')
                cal+=1
                flg_rule=True
            if flg_rule:
                simDic[redirect]=cal
            else:
                #######################################################
                if h>1:
                    cal_1,simDic_All=dist_word2vec(ANS_data,WORD_data,simDic_All,word2vec_model)
                    cal_2,simDic_All=dist_word2vec(ANS_data,WORD_data_Dic[redirect],simDic_All,word2vec_model)
                    if cal_1<cal_2:
                        simDic[redirect]=cal
                else:
                    simDic[redirect]=cal
    if MinorMax=='Max':
        ret_connection,simDic_All=distMax(results,flag,E2LArray,h,simDic,simDic_All,word2vec_model)
        E2LArray,simDic_All=appendE2LArray(ret_connection,'Max',results,WORD_data,flag,h,ANS_data,E2LArray,WORD_data_Dic,simDic_All,PREFIXES,word2vec_model,Redirects_Dic)
    elif MinorMax=='Min':
        pass
        #ret_connection,simDic_All=distMin(results,flag,E2LArray,h,simDic,simDic_All,word2vec_model)
        #E2LArray,simDic_All=appendE2LArray(ret_connection,'Max',results,WORD_data,flag,h,ANS_data,E2LArray,WORD_data_Dic,simDic_All,PREFIXES,word2vec_model)
    elif MinorMax=='None':
        pass
        #ret_connection,simDic_All=distMax(results,flag,E2LArray,h,simDic,simDic_All,word2vec_model)
        #ret_connection,simDic_All=distMin(results,flag,E2LArray,h,simDic,simDic_All,word2vec_model)
        #E2LArray,simDic_All=appendE2LArray(ret_connection,'Max',results,WORD_data,flag,h,ANS_data,E2LArray,WORD_data_Dic,simDic_All,PREFIXES,word2vec_model)
    return E2LArray,WORD_data_Dic,simDic_All

def distMax(results,flag,E2LArray,h,simDic,simDic_All,word2vec_model):
    simWords_sorted=[]                      
    simWords_lep=[]
    simDic_sorted=sorted(simDic.items(),key=lambda x: x[1], reverse=True)               
    for k,v in simDic_sorted:
        if v!=-1 and extract_date(k):
            simWords_sorted.append(str(k))
    for simword in simWords_sorted:           
        for result in results['results']['bindings']:
            labelvalue=result['label']['value']
            entityvalue=result[flag.replace('?','')]['value']
            propvalue=result['p_label']['value']
            if labelvalue==simword:  
                simWords_lep.append([simword,entityvalue,propvalue])
    ret_connection,simDic_All=compWidthNodes(simWords_lep,E2LArray,h,simDic_All,word2vec_model)
    return ret_connection,simDic_All

def compWidthNodes(simWords_lep,E2LArray,h,simDic_All,word2vec_model):                 
    prelList=[]
    retList=[]
    comDict={}                             
    for e2larray in E2LArray:        
        l2_=e2larray.l2                
        h_=e2larray.h               
        minormax_=e2larray.minormax       
        if h_==h and l2_ not in prelList:
            prelList.append(l2_)
    for lep in simWords_lep:
        cal=0
        for prel in prelList:
            cal_,simDic_All=check_word2vec(prel,lep[0],simDic_All,word2vec_model)
            cal+=cal_
        key=','.join(map(str,lep))
        comDict[key]=cal
    comDict_sorted=sorted(comDict.items(),reverse=True)
    for k,v in comDict_sorted:
        retList.append(k.split(','))
    return retList,simDic_All

def CompArrays(word,ANS_data,E2LArray,WORD_data_Dic):
    if (ANS_data.redirect in word) or (word in ANS_data.redirect):
        return False
    for e2larray in E2LArray:
        l1=e2larray.l1
        l2=e2larray.l2
        if word==l1 or word==l2 or (word in WORD_data_Dic[l1].redirected) or (word in WORD_data_Dic[l2].redirected) or (word in WORD_data_Dic[l1].sameas) or (word in WORD_data_Dic[l2].sameas) or (ANS_data.redirect in word) or (word in ANS_data.redirect):
            return False
    return True
