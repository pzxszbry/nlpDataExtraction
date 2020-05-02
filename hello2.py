import spacy
import neuralcoref

nlp = spacy.load('en')
neuralcoref.add_to_pipe(nlp)


file = open(u"WikipediaArticles/Amazon_com.txt", 'r', encoding='UTF-8')
f = file.read()

doc = nlp(f)
co = doc._.coref_resolved

doc2 = nlp(co)._.coref_resolved

# print(nlp(doc2)._.has_coref)
outputfile2 = open('doc2_coref.txt',"w",encoding='utf-8')
outputfile2.write(doc2)
