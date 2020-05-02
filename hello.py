import spacy
import nltk
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from spacy import displacy
from spacy.matcher import Matcher
lemmatizer = WordNetLemmatizer()
from spacy.tokens import Span
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
            "label": "POSITION",
        }]
        entity = Span(doc, start, end, label="POSITION")
        doc.ents += (entity,)
        print(entity.text)
        # self.matched_sents.append({"text": sent.text, "ents": match_ents})

    def extract_currency_relations_by_verb(self,doc):
        allVerb = [token for token in doc if token.pos_ == "VERB"]
        similarWordForBuy = ["buy", "acquire","purchase"]
        # wn.synset('buy.v.01').lemma_names()
        buyWord = set()
        for eachVerb in allVerb:
            for similarWord in similarWordForBuy:
                if self.nlp(eachVerb.lemma_).similarity(self.nlp(similarWord)) > 0.8:
                    buyWord.add(eachVerb)
        for eachVerb in buyWord:
            subjpass = 0
            for tok in eachVerb.children:
                # find dependency tag that contains the text "subjpass"
                if tok.dep_.find("subjpass") == True:
                    subjpass = 1
            buyer = None
            beBought = None
            money = None
            if subjpass == 0:
                for each in eachVerb.children:
                    if each.dep_ == "nsubj":
                        buyer = each
                    elif each.dep_ == 'dobj':
                        # print(list(each.rights)[])
                        if list(each.rights) and list(each.rights)[0].pos_=="SCONJ":
                            beBought = list(list(each.rights)[0].rights)[0]
                            beBought = (beBought,beBought.conjuncts)
                        else:
                            beBought = each
                    elif each.dep_ == "prep" and list(each.rights)[0].ent_type_ == "MONEY":
                        money = list(each.rights)[0]
                        # print(money)
                print((buyer, beBought, money))
                print(eachVerb.sent)
            else:
                # print(list(childs))
                for each in eachVerb.children:
                    # print(each.dep_+"haha")
                    if each.dep_ == "nsubjpass":
                        beBought = each
                    elif each.dep_ == "agent":
                        for possible_noun in each.rights:
                            if possible_noun.pos_ == "PROPN" or possible_noun.ent_type_ == "ORG":
                                buyer = possible_noun
                    elif each.dep_ == "prep" and list(each.rights)[0].ent_type_ == "MONEY":
                        money = list(each.rights)[0]
                print((buyer, beBought, money))
                print(eachVerb.sent)
                # print(doc[buyer.start_char:money.end_char+1])
    def extract_currency_relations_by_noun(self,doc):
        allNoun = [token for token in doc if token.pos_ == "NOUN"]
        similarWordForAcquisition = ["acquisition"]
        AcquisitionNoun = []
        for eachNoun in allNoun:
            for similarWord in similarWordForAcquisition:
                if self.nlp(eachNoun.lemma_).similarity(self.nlp(similarWord)) > 0.6:
                    AcquisitionNoun.append(eachNoun)
        # print(AcquisitionNoun)
        for eachNoun in AcquisitionNoun:
            mydoc = eachNoun.sent
            # print(mydoc)
            buyer = None
            beBought = None
            money = None
            for i in mydoc:
                if i.lemma_=="include":
                    for childs in i.lefts:
                        if childs.dep_=='nsubj':
                            buyer = childs
                    for childs in i.rights:
                        if childs.pos_=="PROPN":
                            beBought = (childs,childs.conjuncts)
                            print((buyer,beBought,money))
                            print(mydoc)
                elif i.lemma_ == "between":

                    for childs in i.rights:
                        if childs.dep_ == 'pobj':
                            buyer = childs
                            beBought = childs.conjuncts
                            print((buyer,beBought,money))
                            print(mydoc)

    def extract_currency_relations_work_verb(self,doc):
        def preprocessPosition():
            matcher = Matcher(self.nlp.vocab)
            #
            # for tok in doc[:5]:
            #     print(tok.text, "-->", tok.dep_, "-->", tok.pos_,"-->",tok.ent_type_)
            pattern = [{'POS': 'ADJ', 'OP': '?'},{'LOWER':  {"IN": ["chief executive officer","the chairman","co-founder","ceo","former ceo","former president","president","chairman","former chairman","Group President","partner","dean"]}}]
            # try to figure out better way to do it later.

            matcher.add("Position",self.collect_sents,pattern)
            matches = matcher(doc)
            for match_id, start, end in matches:
                string_id = self.nlp.vocab.strings[match_id]  # Get string representation
                span = doc[start:end]  # The matched span
        preprocessPosition()

        for eachSen in doc.sents:
            Person = None
            Position = []
            Location = []
            Organization = []
            subjpass = 0
            for tok in eachSen:
                # find dependency tag that contains the text "subjpass"
                if tok.dep_.find("subjpass") == True:
                    subjpass = 1
            if subjpass ==0:
                for token in eachSen:
                    if (token.dep_ =='nsubj' or token.dep_ =='ROOT') and token.ent_type_=='PERSON':
                        Person = token
                    elif (token.dep_=='pobj' or token.dep_=='attr' or token.dep_=='appos' or token.dep_=='conj') and token.ent_type_=='POSITION':
                        Position.append(token)
                    elif token.ent_type_=='GPE':
                        Location.append(token)
                    elif token.ent_type_=='ORG':
                        Organization.append(token)
            else:
                for token in eachSen:
                    if (token.dep_ =='nsubjpass') and token.ent_type_=='ORG':
                        Organization.append(token)
                    elif (token.dep_=='pobj') and token.ent_type_=='PERSON':
                        Person = token
                    elif token.ent_type_=='POSITION':
                        Position.append(token)
                    elif token.ent_type_=='GPE':
                        Location.append(token)
            if Person:
                print((Person,Position,Location,Organization))
        # for person in filter(lambda w: w.ent_type_ == "PERSON", doc):
        #     if person.dep_ in ("nsubj"):
        #         print(person.sent)
        #         print(list(person.head.rights))
        #         if person.head.lemma_=='be':
        #             subject = [w for w in person.head.rights if w.pos_ == "NOUN"]# w.ent_type =="POSITION"
        #             print(subject)
        #             Person_Position_relations.append((person,subject))
        #         elif person.head.pos_=="VERB" and person.head.lemma_=="work":
        #             prop = [w for w in person.head.rights if w.pos_=="SCONJ" and w.dep_=="prep"]
        #             print(prop)
        #             if prop:
        #                 prop = prop[0]
        #                 position = [p for p in prop.rights if p.dep_=="pobj"]
        #                 Person_Position_relations.append((person,position))
        #                 # print(list(position))
        # print(Person_Position_relations)

        Person_Organization_relations = []

            #     if subject:
            #         subject = subject[0]
            #         relations.append((subject, money))
            # elif money.dep_ == "pobj" and money.head.dep_ == "prep":
            #     relations.append((money.head.head, money))
        return

    def extract_currency_relations_part_of(self,doc):
        for eachSent in doc.sents:
            smallLoc = []
            bigLoc = []
            leftSub = None
            rightSub = None
            for token in eachSent:
                if token.head.lemma_=='be' and token.dep_=='advcl':
                    leftSub = token.subtree
                elif token.head.lemma_=='be' and token.dep_=='nsubj':
                    leftSub = token.subtree
                elif token.head.lemma_=='be' and token.dep_=='attr':
                    rightSub = token.subtree
            # print(list(leftSub))
            # print(list(rightSub))
            if leftSub and rightSub:
                for token in leftSub:
                    # print(token)
                    if token.pos_=='PROPN' and (token.ent_type_=="GPE" or token.ent_type_=="LOC"):
                        smallLoc.append(token)
                        # print(rightSub)
                for token in rightSub:
                    # print(token)
                    if token.pos_ == 'PROPN' and token.dep_=='pobj' and (token.ent_type_=="GPE" or token.ent_type_=="ORG" or token.ent_type_=="LOC"):
                        bigLoc.append(token)
                        for i in token.conjuncts:
                            bigLoc.append(i)
                        # if smallLoc and bigLoc:
            if smallLoc and bigLoc:
                print(smallLoc,bigLoc)
                print(smallLoc[0].sent)

            # Located at ...





    def extract_currency_relations(self,doc):
        spans = list(doc.ents) + list(doc.noun_chunks)
        spans = self.filter_spans(spans)
        with doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)

        # self.extract_currency_relations_by_verb(doc)
        # self.extract_currency_relations_by_noun(doc)
        # self.extract_currency_relations_work_verb(doc)
        self.extract_currency_relations_part_of(doc)


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
        # file = open("WikipediaArticles/Amazon_com.txt")
        # file = open("WikipediaArticles/IBM.txt")
        # file = open("WikipediaArticles/AppleInc.txt")
        # file = open("WikipediaArticles/Dallas.txt")
        file = open("test.txt")

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