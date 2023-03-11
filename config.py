#############IMPORT PACKAGES##############
import csv
import re
#############CONSTANT DEFINITION##############
##Default path of AnswerList and pre-learning model, BCCWJ-Goi
local='**local files path of AnswerList, PREFIXES and pre-learned model**'
local_graphs='**local files path of Graphs**'

##ENDPOINTs
ENDPOINT_dbpedia='http://ja.dbpedia.org/sparql/'
ENDPOINT_virtuoso='http://localhost:8890/sparql/'
ENDPOINT_graphdb='http://localhost:7200/repositories/MCQ_OWL2-QL_2'

##PREFIX of DBpedia-ja
ANS_O='dbpedia-ja:'

##Default Language of Q-Graph
LANG='ja'

##LIMIT of SPARQL
LIMIT=100

##Infer or Not-Infer
infer_flg="true"
#infer_flg="false"

##CONNECTION RETRY
CONNECTION_RETRY=4

###Q-Graph variable setting
DEPTH=2 ##Maximum number of hops from an Answer node
LenNodes=3 ##Maximum number of nodes in one node

##pre-learning model
model_2='model/wikipedia2Vec/jawiki_20180420_300d.txt'
model_1='model/entity_vector/entity_vector.model.bin'
model_0='model/model_neologd.vec'
model_path=local+model_2
binary_flg=True #Not bin -> False, bin -> True

##Exclude bad uri for genrating Q-Graph
badURI_strings=["<",">","\"","\t","{ ","}","|","\\","^","`"]

##Anwer file name and count number of that
ANS_filepath=local+'/ANS/HISTORY/AnswerList_s.csv'

##PREFIXES file path
PREFIXES_filepath_txt=local+'PREFIXES/PREFIXES.txt'
PREFIXES_filepath_csv=local+'PREFIXES/PRE-NAMESPACE.csv'

##file name of Triples added Rules
Triples_addedRules_path=local+'Triples_addedRules/added_rule_all.csv'

date_pattern=[re.compile('(\d{4})年(\d{1,2})月(\d{1,2})日'),
    re.compile('(\d{1,2})月(\d{1,2})日'),
    re.compile('(\d{4})年'),
    re.compile('(\d{3})年'),
    re.compile('(\d{1,2})月'),
    re.compile('(\d{1})')]

############CLASS DEFINITION##############
class word_data():
    def __init__(self,learning,model,redirect,redirected,sameas,uri_dbpedia,uri_wikidata):
        self.learning=learning
        self.model=model
        self.redirect=redirect
        self.redirected=redirected
        self.sameas=sameas
        self.uri_dbpedia=uri_dbpedia
        self.uri_wikidata=uri_wikidata
class Answer_data():
    def __init__(self,learning,model,redirect,redirected,sameas,ansnum,uri_dbpedia,uri_wikidata):
        self.learning=learning
        self.model=model
        self.redirect=redirect
        self.redirected=redirected
        self.sameas=sameas
        self.ansnum=ansnum
        self.uri_dbpedia=uri_dbpedia
        self.uri_wikidata=uri_wikidata

class E2LArray_list():
    def __init__(self,e1,l1,e2,l2,p,pl,h,flag,sim,minormax):
        self.e1=e1
        self.l1=l1
        self.e2=e2
        self.l2=l2
        self.p=p
        self.pl=pl
        self.h=h
        self.flag=flag
        self.sim=sim
        self.minormax=minormax
############FUNCTION DEFINITION##############
