import os
import re
import spacy
import neuralcoref

nlp = spacy.load('en_core_web_md')
neuralcoref.add_to_pipe(nlp)
# neuralcoref.add_to_pipe(nlp, greedyness=0.5, max_dist=10, blacklist=False, store_scores=True)

def article_to_paraList(filePath):
    p = re.compile("\n\n", re.S)
    print('>> splitting article into paragraphs...')
    with open(filePath, 'r', encoding='utf-8-sig') as file:

        return p.split(file.read()) # return the paraList


def merge_paraList_to_article(paraList):
    print('>> merging paragraphs into article...')
    
    return '\n\n'.join(paraList)


def do_coref_resolved(paraList):
    para_coref_list = list()
    for para in paraList:
        para_coref_list.append(nlp(para)._.coref_resolved)
    
    return para_coref_list


def remove_coref(input_path, output_path):
    
    # para_coref_list = list()
    # files= os.listdir(input_path)

    for file in os.listdir(input_path):
        if os.path.isfile(os.path.join(input_path, file)):
            file_name, file_ext = os.path.splitext(file)
            out_file_name = file_name + '_no_coref' + file_ext
            in_file_path = os.path.join(input_path, file)
            out_file_path = os.path.join(input_path, 'coref_resolved', out_file_name)
            print('input file:\t{}'.format(in_file_path))
            para_list = article_to_paraList(in_file_path)
            para_coref_list = do_coref_resolved(para_list)
            article_coref_solved = merge_paraList_to_article(para_coref_list)
            # para_coref_list.clear()
            # for para in para_list:
            #     para_coref_list.append(nlp(para)._.coref_resolved)
            # write data
            os.makedirs(os.path.join(input_path, 'coref_resolved'), exist_ok=True)
            with open(out_file_path,'w', encoding='utf-8-sig') as o_f:
                # print('output file:\t{}'.format(out_file_path))
                o_f.write(article_coref_solved)


######################################################################

input_path = './input'
output_path = './output'

remove_coref(input_path, output_path)