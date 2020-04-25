import nltk
from nltk.stem import WordNetLemmatizer
import re
from nltk.sem.relextract import extract_rels, rtuple
lemmatizer = WordNetLemmatizer()


def lemmatize(tokens):
    lemmaArr = []
    for token in tokens:
        temp = []
        for word in token:
            temp.append(lemmatizer.lemmatize(word))
        lemmaArr.append(temp)
    return lemmaArr;

# file = open("WikipediaArticles/Amazon_com.txt")
file = open("test.txt")

fl = file.read()
sentences = nltk.sent_tokenize(fl) # Split the document into sentences
tokens = [nltk.word_tokenize(sentence) for sentence in sentences] # Tokenize the sentences into words
lemmaArr = lemmatize(tokens)  # Lemmatize the words to extract lemmas as features
pos_tag = [nltk.pos_tag(token) for token in lemmaArr] # Part-of-speech (POS) tag the words to extract POS tag features
# print(pos_tag[0])
# word_tag_pairs = nltk.bigrams(pos_tag[0])
# print(list(word_tag_pairs)[0])
#
# grammar = r"""
#
#     NP: {<DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN
#   PP: {<IN><NP>}               # Chunk prepositions followed by NP
#   VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments
#   CLAUSE: {<NP><VP>}           # Chunk NP, VP
#   """
#
# cp = nltk.RegexpParser(grammar)
# # cp.evaluate(pos_tag[0])
# chuck = cp.parse(pos_tag[0])
# chuck.draw()

# print(chuck)
print(nltk.ne_chunk(pos_tag[0]))
#
# OF = re.compile(r'.*\bat\b.*')
# # OF2 = re.compile(r'.*\bof\b.*')
# rels2 = extract_rels('GPE', 'GPE', nameEntity, corpus='ace', pattern=OF, window=10)
# rels = extract_rels('ORGANIZATION', 'GPE', nameEntity, corpus='ace', pattern=OF2, window=10)
# print(rels)
# print(rels2)
# for each in pos_tag:
#     nameEntity = nltk.ne_chunk(each)
# #     # print(nameEntity)
# #
# #     OF = re.compile(r'.*\bat\b.*')
# #     OF2 = re.compile(r'.*\bof\b.*')
#     rels = extract_rels('LOCATION', 'GPE', nameEntity, corpus='ace', pattern=OF, window=10)
#     rels2 = extract_rels('LOCATION', 'GPE', nameEntity, corpus='ace', pattern=OF2, window=10)
#     if rels or rels2:
#         print(nameEntity)
#
#     print(rels)
#     print(rels2)

# nameEntity.draw()
# IN = re.compile(r'.*\bin\b(?!\b.+ing)')
# res = nltk.sem.extract_rels('ORG', 'LOC', pos_tag[1],corpus='ieer', pattern = IN)
# print(res)
# print(tokens)
# pos_tag = [nltk.pos_tag(token) for token in tokens]
# for each in pos_tag:
#
    # break


# import nltk
# nltk.download('ieer')
# from nltk.corpus import ieer
#
# # file = open("WikipediaArticles/Amazon_com.txt")
# docs = ieer.parsed_docs('NYT_19980315')
# tree = docs[1].text
# print(tree)