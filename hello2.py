import spacy
import neuralcoref
import re
import os

nlp = spacy.load('en_core_web_md')
neuralcoref.add_to_pipe(nlp, greedyness=0.5, max_dist=10, blacklist=False, store_scores=True)


def article_to_paraList(filePath):
    p = re.compile("\n\n", re.S)
    article = open(filePath, 'r', encoding='UTF-8-sig').read()
    return p.split(article) # return the paraList



####################################################################

root_path = 'WikipediaArticles'
files= os.listdir(root_path)
# file_path = 'WikipediaArticles\AppleInc.txt'

para_coref_list = list()
for file in files[18:]:
    if os.path.isfile(os.path.join(root_path, file)):
        file_path = os.path.join(root_path, file)
        file_name = os.path.splitext(file)[0]
        para_list = article_to_paraList(file_path)
        para_coref_list.clear()
        for para in para_list:
            para_coref_list.append(nlp(para)._.coref_resolved)
        out_path = os.path.join('WikipediaArticles_coref', file_name + '_coref.txt')
        out = open(out_path,"w",encoding='utf-8')
        out.write('\n\n'.join(para_coref_list))
        out.close()



# para_list = article_to_paraList(file_path)

# para_coref_list = list()

# for para in para_list:
#     doc = nlp(para)
    # print(para)
    # print(doc._.coref_resolved)
    # doc = nlp(doc._.coref_resolved)
    # for sent in doc.sents:
    #     print(sent)
#     para_coref_list.append(doc._.coref_resolved)

# out = open('AppleInc_coref.txt',"w",encoding='utf-8')
# out.write('\n\n'.join(para_coref_list))