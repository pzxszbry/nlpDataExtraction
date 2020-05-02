import spacy
import neuralcoref
import re

nlp = spacy.load('en_core_web_md')
neuralcoref.add_to_pipe(nlp, greedyness=0.5, max_dist=10, blacklist=False, store_scores=True)


def article_to_paraList(filePath):
    p = re.compile("\n\n", re.S)
    article = open(filePath, 'r', encoding='UTF-8-sig').read()
    return p.split(article) # return the paraList



####################################################################

file_path = 'test2.txt'

para_list = article_to_paraList(file_path)

para_coref_list = list()

for para in para_list:
    doc = nlp(para)
    print(para)
    # print(doc._.coref_resolved)
    doc = nlp(doc._.coref_resolved)
    for sent in doc.sents:
        print(sent)