#############IMPORT PACKAGES##############
from SPARQLWrapper import SPARQLWrapper
import csv
import gensim
import subprocess
import time
#############IMPORT MY-PACKAGES##############
import config
from generating import Generating
from get_redirects import getRedirects,getsameAs,check_Redirects
from get_wikidata_uri import getWikiURI
from check_e2larray import checkE2LArray
#############LOAD PREFIXES##############
##Open list of PREFIXES for using SPARQL
PREFIXES=''
with open(config.PREFIXES_filepath_txt,'r') as txtF:
    PREFIXES=txtF.read()

##Open list of PREFIXES for drawing Q-Graph and make list of PREFIXES
replaced_words=[]                       
replace_words=[]
PREFIXES_Dic={}
with open(config.PREFIXES_filepath_csv,'r') as pnF:
    reader_pn=csv.reader(pnF)           
    for row_pn in reader_pn:            
        replaced_words.append(row_pn[1])
        replace_words.append(' ')
        PREFIXES_Dic[row_pn[0]]=row_pn[1]

#############LOAD PRE-LEARNED MODEL##############
print('Loading \''+config.model_path+'\'...')
word2vec_model=gensim.models.KeyedVectors.load_word2vec_format(config.model_path,binary=config.binary_flg)
#fasttext_model=FastText.load_fasttext_format(local+'wiki/wiki.simple')
print('model Loading Done.')

##Make Dic for choosing words for label
WORD_data_Dic={} #Dic of config.word_data
resultsAllDic={} #Dic of all results of SPARQL in json format
simDic_All={} #Dic of similarity between words (All)
Redirects_Dic={} #Dic of redirects of all words
#############DEFINITION MAIN()##############
def main():
    global WORD_data_Dic
    global resultsAllDic
    global simDic_All
    global Redirects_Dic
    global cnt_csv
    cnt_csv=row_count(config.ANS_filepath)
    with open(config.ANS_filepath,'r') as Ansf:
        with open('error_ansnum.txt','a') as ef:
            reader=csv.reader(Ansf)
            for ir,row in enumerate(reader):
                    E2LArray=[]
                    ##LOAD ANSWER and define config.Answer_data
                    ANS_data=config.Answer_data('','','','','','','','')
                    ANS_data.redirect=row[0]
                    ANS_data.model=row[1]
                    #row[2] is not-used (word contained major-words list)
                    #row[3] is not-used (label of original Answer-word)
                    ANS_data.learning=row[4]
                    #row[5] is not-used (flag of method of generate Answer-word)
                    ANS_data.ansnum=row[6]
                    ANS_data.uri_dbpedia=PREFIXES_Dic[config.ANS_O]+ANS_data.redirect.replace(' ','_').replace('（','_（')
                    ANS_data.uri_wikidata=getWikiURI(ANS_data.uri_dbpedia,PREFIXES)
                    ANS_data.redirected,Redirects_Dic=check_Redirects(ANS_data.redirect,ANS_data.uri_dbpedia,PREFIXES,Redirects_Dic)
                    ANS_data.sameas=getsameAs(ANS_data.redirect,ANS_data.uri_dbpedia,PREFIXES)

                    ##define config.word_data
                    if ANS_data.redirect not in WORD_data_Dic.keys():
                        word_data=config.word_data('','','','','','','')
                        word_data.learning=ANS_data.learning
                        word_data.model=ANS_data.model
                        word_data.redirect=ANS_data.redirect
                        word_data.redirected=ANS_data.redirected
                        word_data.sameas=ANS_data.sameas
                        word_data.uri_dbpedia=ANS_data.uri_dbpedia
                        word_data.uri_wikidata=ANS_data.uri_wikidata
                        WORD_data_Dic[word_data.redirect]=word_data
                    print('|*Progress:'+str(ir)+'/'+str(cnt_csv)+', Answer='+ANS_data.redirect)
                    E2LArray,resultsAllDic,WORD_data_Dic,simDic_All=Generating(ANS_data,word2vec_model,PREFIXES,PREFIXES_Dic,resultsAllDic,WORD_data_Dic,simDic_All,Redirects_Dic)
                    if len(E2LArray)!=0:
                        E2LArray,WORD_data_Dic=checkE2LArray(E2LArray,ANS_data,word2vec_model,PREFIXES,PREFIXES_Dic,WORD_data_Dic,ir)
                    with open('Graphs/org/'+str(ir)+'_'+ANS_data.redirect+'_Nodes.csv','w') as nf:
                        for e2larray in E2LArray:
                            for i,value in enumerate(vars(e2larray).values()):
                                if i==0:
                                    nf.write("\""+str(value)+"\"")
                                else:
                                    nf.write(",\""+str(value)+"\"")
                            nf.write('\n')

def row_count (file_name):
    cnt_csv=0
    with open(file_name,'r') as f:
        reader=csv.reader(f)
        cnt_csv= len([row for row in reader])
    return cnt_csv-1

if __name__ =='__main__':
    main()  
