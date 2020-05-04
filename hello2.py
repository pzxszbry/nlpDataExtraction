import os
import re
import spacy
import neuralcoref

nlp = spacy.load('en_core_web_md')
neuralcoref.add_to_pipe(nlp, greedyness=0.5, max_dist=10, blacklist=False, store_scores=True)


def article_to_paraList(file):
    p = re.compile("\n\n", re.S)
    with open(os.path.join('output', file), 'r', encoding='utf-8-sig') as file:
        article = file.read()
        return p.split(article) # return the paraList
    



####################################################################

root_path = 'input'
files= os.listdir(root_path)
para_coref_list = list()

for file in files:
    if os.path.isfile(os.path.join(root_path, file)):
        file_path = os.path.join(root_path, file)
        file_name, file_ext = os.path.splitext(file)
        para_list = article_to_paraList(file_path)
        para_coref_list.clear()
        for para in para_list:
            para_coref_list.append(nlp(para)._.coref_resolved)
        out_path = os.path.join('output', file_name + '_coref.txt')
        out = open(out_path,"w",encoding='utf-8')
        out.write('\n\n'.join(para_coref_list))
        out.close()