import spacy
import nltk
from collections import Counter
from nltk.stem import WordNetLemmatizer
from spacy import displacy
from spacy.matcher import Matcher
lemmatizer = WordNetLemmatizer()
class Solution:

    nlp = spacy.load("en_core_web_md")
    matched_sents = []

    def filter_spans(self,spans):
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

    def collect_sents(self,matcher, doc, i, matches):
        match_id, start, end = matches[i]
        span = doc[start:end]  # Matched span
        sent = span.sent  # Sentence containing matched span
        # Append mock entity for match in displaCy style to matched_sents
        # get the match span by ofsetting the start and end of the span with the
        # start and end of the sentence in the doc
        match_ents = [{
            "start": span.start_char - sent.start_char,
            "end": span.end_char - sent.start_char,
            "label": "MATCH",
        }]
        self.matched_sents.append({"text": sent.text, "ents": match_ents})

    def subtree_matcher(doc):
        subjpass = 0

        for i, tok in enumerate(doc):
            # find dependency tag that contains the text "subjpass"
            if tok.dep_.find("subjpass") == True:
                subjpass = 1

        x = ''
        y = ''

        # if subjpass == 1 then sentence is passive
        if subjpass == 1:
            for i, tok in enumerate(doc):
                if tok.dep_.find("subjpass") == True:
                    y = tok.text

                if tok.dep_.endswith("obj") == True:
                    x = tok.text

        # if subjpass == 0 then sentence is not passive
        else:
            for i, tok in enumerate(doc):
                if tok.dep_.endswith("subj") == True:
                    x = tok.text

                if tok.dep_.endswith("obj") == True:
                    y = tok.text

        return x, y
    def extract_currency_relations(self,doc):
        spans = list(doc.ents) + list(doc.noun_chunks)
        spans = self.filter_spans(spans)
        with doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)

        allVerb = [token for token in doc if token.pos_ == "VERB"]
        buyWord = []
        similarWordForBuy = ["buy","acquire"]
        for eachVerb in allVerb:
            for similarWord in similarWordForBuy:
                if self.nlp(eachVerb.lemma_).similarity(self.nlp(similarWord))>0.6:
                    buyWord.append(eachVerb)
        # print(buyWord)
        for eachVerb in buyWord:
            # childs = eachVerb.children
            # print(list(childs))
            subjpass = 0
            for tok in eachVerb.children:
                # find dependency tag that contains the text "subjpass"
                # print(tok.dep_)
                if tok.dep_.find("subjpass") == True:
                    subjpass = 1
            print(subjpass)
            buyer = None
            beBought = None
            money = None
            if subjpass == 0:
                for each in eachVerb.children:
                    if each.dep_=="nsubj":
                        buyer = each
                    elif each.dep_=='dobj':
                        beBought = each
                    elif each.dep_=="prep" and list(each.rights)[0].ent_type_=="MONEY":
                        money = list(each.rights)[0]
                        # print(money)
                print((buyer,beBought,money))
                    # print(eachVerb)
            else:
                # print(list(childs))
                for each in eachVerb.children:
                    # print(each.dep_+"haha")
                    if each.dep_ == "nsubjpass":
                        beBought = each
                    elif each.dep_=="agent":
                        for possible_noun in each.rights:
                            if possible_noun.pos_=="PROPN" or possible_noun.ent_type_=="ORG":
                                buyer = possible_noun
                    elif each.dep_=="prep" and list(each.rights)[0].ent_type_=="MONEY":
                        money = list(each.rights)[0]
                print((buyer, beBought, money))
            # break
        # matcher = Matcher(self.nlp.vocab,validate=True)
        #
        # for tok in doc[:5]:
        #     print(tok.text, "-->", tok.dep_, "-->", tok.pos_,"-->",tok.ent_type_)
        # pattern1 = [{'ENT_TYPE': 'ORG'},
        #            {'LEMMA': {"IN":["buy","acquire","sell"]}},
        #            {'ENT_TYPE': 'ORG'}]

        # pattern2 = [{'ENT_TYPE': 'ORG'},
        #            {'LEMMA': {"IN":["buy","acquire","sell"]}},
        #            {'ENT_TYPE': 'ORG'}]

        # matcher.add("CompanyOwn",self.collect_sents,pattern1)
        #
        # matches = matcher(doc)
        # for match_id, start, end in matches:
        #     string_id = self.nlp.vocab.strings[match_id]  # Get string representation
        #     span = doc[start:end]  # The matched span
        #     print(match_id, string_id, start, end, span.text)

        # wordSet = set()
        # relations = []
        # for word in filter(lambda w: w.pos_=="VERB" or w.pos_=="NOUN", doc):
        #     # print(word)
        #     similarWords = ["acquire","buy","purchase"]
        #     for sigleSimilarWords in similarWords:
        #         # print(word)
        #         if nlp(word.lemma_).similarity(nlp(sigleSimilarWords))>0.7:
        #             wordSet.add(word)
        # print(wordSet)
        # for word in wordSet:
        #     # print(word.head)
        #     childs = word.children
        #     # print(list(childs))
        #     print(childs.__class__)
        #     dobj = []
        #     nsubj = []
        #     for possible in word.children:
        #         print(possible)
        #         if possible.dep_ == "nsubj" and (possible.ent_type_ =="ORG" or possible.pos_=="PRON"):
        #             nsubj.append(possible)
        #         elif possible.dep_=='dobj' and (possible.ent_type_ =="ORG" or possible.pos_=="PRON"):
        #             dobj.append(possible)
        #     for i in dobj:
        #         for j in nsubj:
        #             relations.append((j,word,i))
        # return relations
    def lemmatize(self,tokens):
        lemmaArr = []
        for token in tokens:
            temp = []
            for word in token:
                temp.append(lemmatizer.lemmatize(word))
            lemmaArr.append(temp)
        return lemmaArr;

    def main(self):
        file = open("WikipediaArticles/Amazon_com.txt")
        # file = open("WikipediaArticles/IBM.txt")
        # file = open("WikipediaArticles/AppleInc.txt")
        # file = open("test.txt")

        fl = file.read()
        sentences = nltk.sent_tokenize(fl) # Split the document into sentences
        tokens = [nltk.word_tokenize(sentence) for sentence in sentences] # Tokenize the sentences into words
        lemmaArr = self.lemmatize(tokens)  # Lemmatize the words to extract lemmas as features
        pos_tag = [nltk.pos_tag(token) for token in lemmaArr] # Part-of-speech (POS) tag the words to extract POS tag features

        doc = self.nlp(fl)
        # doc = nlp("Amazon acquired Whole Foods Market for US$13.4 billion.")
        relations = self.extract_currency_relations(doc)

        # print(relations)
        #
        # # labels = [x.label_ for x in doc.ents]
        # # print(Counter(labels))
        html = displacy.render(doc,style='dep',page=True)
        outputfile = open('dep.html',"w",encoding='utf-8')
        outputfile.write(html)
        #
        html2 = displacy.render(doc,style='ent',page=True)
        # html2= displacy.render(self.matched_sents, style="ent", manual=True)
        outputfile2 = open('ent.html',"w",encoding='utf-8')
        outputfile2.write(html2)
if __name__=='__main__':
    s = Solution()
    s.main();