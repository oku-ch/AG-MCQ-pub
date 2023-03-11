#############IMPORT PACKAGES##############
import MeCab
#############IMPORT MY-PACKAGES##############
import config

def check_word2vec(word_1,word_2,simDic_All,word2vec_model):
    sim=-1
    if word_1+'&&'+word_2 not in simDic_All.keys():
        if word_2+'&&'+word_1 not in simDic_All.keys():
            try:
                sim=1-word2vec_model.similarity(word_1,word_2)
            except:          
                pass
            simDic_All[word_2+'&&'+word_1]=sim
        return simDic_All[word_2+'&&'+word_1],simDic_All
    return simDic_All[word_1+'&&'+word_2],simDic_All

def dist_word2vec(word_data_1,word_data_2,simDic_All,word2vec_model):
    sim=-1
    if word_data_1.redirect+'&&'+word_data_2.redirect not in simDic_All.keys():
        if word_data_2.redirect+'&&'+word_data_1.redirect not in simDic_All.keys():
            try:
                sim=1-word2vec_model.similarity(word_data_1.model,word_data_2.model)
            except:          
                pass
            if sim==-1:
                try:
                    sim=1-sentence_similarity(word_data_1.model,word_data_2.model)
                except:
                    pass
            simDic_All[word_data_2.redirect+'&&'+word_data_1.redirect]=sim
        return simDic_All[word_data_2.redirect+'&&'+word_data_1.redirect],simDic_All
    return simDic_All[word_data_1.redirect+'&&'+word_data_2.redirect],simDic_All

def avg_feature_vector(sentence, model, num_features):
    words = mecab.parse(sentence).replace(' \n', '').split()
    feature_vec = np.zeros((num_features,), dtype="float32")
    for word in words:
        feature_vec = np.add(feature_vec, model[word])
    if len(words) > 0:
        feature_vec = np.divide(feature_vec, len(words))
    return feature_vec

def sentence_similarity(sentence_1, sentence_2):
    num_features=200
    sentence_1_avg_vector = avg_feature_vector(sentence_1, word2vec_model, num_features)
    sentence_2_avg_vector = avg_feature_vector(sentence_2, word2vec_model, num_features)
    return 1 - spatial.distance.cosine(sentence_1_avg_vector, sentence_2_avg_vector)

def check_dist_sentences(sentence_1):
    try:
        dist_w=sentence_similarity(sentence_1,sentence_1)
        return True
    except:
        return False

def extract_date(strings):
    i=0
    for pattern in config.date_pattern:
        result=pattern.search(strings)
        if result:
            i+=1
    if i>0:
        return False
    else:
        return True
