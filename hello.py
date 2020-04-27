import spacy
import nltk
from collections import Counter
from nltk.stem import WordNetLemmatizer
from spacy import displacy
from nltk.chunk import conlltags2tree, tree2conlltags

import re
from nltk.sem.relextract import extract_rels, rtuple
lemmatizer = WordNetLemmatizer()

def filter_spans(spans):
    # Filter a sequence of spans so they don't contain overlaps
    # For spaCy 2.1.4+: this function is available as spacy.util.filter_spans()
    get_sort_key = lambda span: (span.end - span.start, -span.start)
    sorted_spans = sorted(spans, key=get_sort_key, reverse=True)
    result = []
    seen_tokens = set()
    for span in sorted_spans:
        # Check for end - 1 here because boundaries are inclusive
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
        seen_tokens.update(range(span.start, span.end))
    result = sorted(result, key=lambda span: span.start)
    return result
#     return relations
def extract_currency_relations(doc):
    spans = list(doc.ents) + list(doc.noun_chunks)
    spans = filter_spans(spans)
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)
    wordSet = set()
    relations = []
    for word in filter(lambda w: w.pos_=="VERB" or w.pos_=="NOUN", doc):
        # print(word)
        similarWords = ["acquire","buy","purchase"]
        for sigleSimilarWords in similarWords:
            # print(word)
            if nlp(word.lemma_).similarity(nlp(sigleSimilarWords))>0.7:
                wordSet.add(word)
    print(wordSet)
    for word in wordSet:
        # print(word.head)
        childs = word.children
        # print(list(childs))
        print(childs.__class__)
        dobj = []
        nsubj = []
        for possible in word.children:
            print(possible)
            if possible.dep_ == "nsubj" and (possible.ent_type_ =="ORG" or possible.pos_=="PRON"):
                nsubj.append(possible)
            elif possible.dep_=='dobj' and (possible.ent_type_ =="ORG" or possible.pos_=="PRON"):
                dobj.append(possible)
        for i in dobj:
            for j in nsubj:
                relations.append((j,word,i))
    return relations
def lemmatize(tokens):
    lemmaArr = []
    for token in tokens:
        temp = []
        for word in token:
            temp.append(lemmatizer.lemmatize(word))
        lemmaArr.append(temp)
    return lemmaArr;

file = open("WikipediaArticles/Amazon_com.txt")
# file = open("WikipediaArticles/IBM.txt")
# file = open("WikipediaArticles/AppleInc.txt")
# file = open("test.txt")

fl = file.read()
sentences = nltk.sent_tokenize(fl) # Split the document into sentences
tokens = [nltk.word_tokenize(sentence) for sentence in sentences] # Tokenize the sentences into words
lemmaArr = lemmatize(tokens)  # Lemmatize the words to extract lemmas as features
pos_tag = [nltk.pos_tag(token) for token in lemmaArr] # Part-of-speech (POS) tag the words to extract POS tag features

nlp = spacy.load("en_core_web_md")
doc = nlp(fl)

relations = extract_currency_relations(doc)
print(relations)
for r1, r2 ,r3 in relations:
    print("\t{}\t{}\t{}".format(r1.text, r2.text,r3.text))
# labels = [x.label_ for x in doc.ents]
# print(Counter(labels))
html = displacy.render(doc,style='dep',page=True)
outputfile = open('dep.html',"w",encoding='utf-8')
outputfile.write(html)

html2 = displacy.render(doc,style='ent',page=True)
outputfile2 = open('ent.html',"w",encoding='utf-8')
outputfile2.write(html2)
