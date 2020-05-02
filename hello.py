import spacy
import nltk
import json
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
    outputjson = None
    file = None
    extraction = []
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

    def collect_sents(self,matcher, doc, i, matches):
        match_id, start, end = matches[i]
        span = doc[start:end]  # Matched span
        sent = span.sent  # Sentence containing matched span
        match_ents = [{
            "start": span.start_char - sent.start_char,
            "end": span.end_char - sent.start_char,
            "label": "POSITION",
        }]
        entity = Span(doc, start, end, label="POSITION")
        doc.ents += (entity,)
        print(entity.text)
        # self.matched_sents.append({"text": sent.text, "ents": match_ents})

    def extract_currency_relations_buy_by_verb(self,doc):
        allVerb = [token for token in doc if token.pos_ == "VERB"]
        similarWordForBuy = ["buy", "acquire","purchase"]
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

            arguments = dict();
            if subjpass == 0:
                for each in eachVerb.children:
                    if each.dep_ == "nsubj":
                        arguments["buyer"] = str(each)
                    elif each.dep_ == 'dobj':
                        # print(list(each.rights)[])
                        if list(each.rights) and list(each.rights)[0].pos_=="SCONJ":
                            beBought = list(list(each.rights)[0].rights)[0]
                            arguments["item"] = str(beBought,beBought.conjuncts)
                        else:
                            arguments["item"] = str(each)

                    elif each.dep_ == "prep" and list(each.rights)[0].ent_type_ == "MONEY":
                        arguments["price"] = str(list(each.rights)[0])
                        # print(money)

                # arguments = {"buyer":str(buyer),"item":str(beBought),"price":str(money)}
                # thisextraction = {"template":'Buy',"sentence":str(eachVerb.sent),"arguments":arguments}
                # self.extraction.append(thisextraction)
            else:
                for each in eachVerb.children:
                    if each.dep_ == "nsubjpass":
                        arguments["item"] = str(each)
                    elif each.dep_ == "agent":
                        for possible_noun in each.rights:
                            if possible_noun.pos_ == "PROPN" or possible_noun.ent_type_ == "ORG":
                                arguments["buyer"] = str(possible_noun)
                    elif each.dep_ == "prep" and list(each.rights)[0].ent_type_ == "MONEY":
                        arguments["price"] = str(list(each.rights)[0])
            thisextraction = {"template":'Buy',"sentence":str(eachVerb.sent),"arguments":arguments}
            self.extraction.append(thisextraction)
    def extract_currency_relations_buy_by_noun(self,doc):
        allNoun = [token for token in doc if token.pos_ == "NOUN"]
        similarWordForAcquisition = ["acquisition"]
        AcquisitionNoun = []
        for eachNoun in allNoun:
            for similarWord in similarWordForAcquisition:
                if self.nlp(eachNoun.lemma_).similarity(self.nlp(similarWord)) > 0.6:
                    AcquisitionNoun.append(eachNoun)
        for eachNoun in AcquisitionNoun:
            mydoc = eachNoun.sent
            # buyer = None
            # beBought = None
            # money = None
            arguments = dict()
            for i in mydoc:
                if i.lemma_=="include":
                    for childs in i.lefts:
                        if childs.dep_=='nsubj':
                            arguments['buyer'] = str(childs)
                    for childs in i.rights:
                        if childs.pos_=="PROPN":
                            arguments['item'] = str(childs)+str(childs.conjuncts)
                elif i.lemma_ == "between":
                    for childs in i.rights:
                        if childs.dep_ == 'pobj':
                            arguments['buyer'] = str(childs)
                            arguments['item'] = str(childs.conjuncts)
            thisextraction = {"template": 'Buy', "sentence": str(eachNoun.sent), "arguments": arguments}
            self.extraction.append(thisextraction)

    def extract_currency_relations_work_verb(self,doc):
        def preprocessPosition():
            matcher = Matcher(self.nlp.vocab)
            pattern = [{'POS': 'ADJ', 'OP': '?'},{'LOWER':  {"IN": ["chief executive officer","the chairman","co-founder","ceo","former ceo","former president","president","chairman","former chairman","Group President","partner","dean"]}}]
            matcher.add("Position",self.collect_sents,pattern)
            # matches = matcher(doc)
            # for match_id, start, end in matches:
            #     string_id = self.nlp.vocab.strings[match_id]  # Get string representation
            #     span = doc[start:end]  # The matched span
        preprocessPosition()

        for eachSen in doc.sents:
            arguments = dict()
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
                        Person = str(token)
                    elif (token.dep_=='pobj' or token.dep_=='attr' or token.dep_=='appos' or token.dep_=='conj') and token.ent_type_=='POSITION':
                        Position.append(str(token))
                    elif token.ent_type_=='GPE':
                        Location.append(str(token))
                    elif token.ent_type_=='ORG':
                        Organization.append(str(token))
            else:
                for token in eachSen:
                    if (token.dep_ =='nsubjpass') and token.ent_type_=='ORG':
                        Organization.append(str(token))
                    elif (token.dep_=='pobj') and token.ent_type_=='PERSON':
                        Person = str(token)
                    elif token.ent_type_=='POSITION':
                        Position.append(str(token))
                    elif token.ent_type_=='GPE':
                        Location.append(str(token))
            if Person:
                arguments['person'] = Person
                arguments['organization'] = ','.join(Organization)
                arguments['Position'] = ','.join(Position)
                arguments['Location'] = ','.join(Location)
                thisextraction = {"template": 'Work', "sentence": str(eachSen), "arguments": arguments}
                self.extraction.append(thisextraction)
        return

    def extract_currency_relations_part_of(self,doc):
        for eachSent in doc.sents:
            smallLoc = []
            bigLoc = []
            arguments = dict()
            leftSub = None
            rightSub = None
            for token in eachSent:
                if token.head.dep_=='ROOT' and token.dep_.find('nsubj')>=0 and (token.ent_type_=="GPE" or token.ent_type_=="LOC"):
                    smallLoc.append(str(token))
                elif token.pos_ == 'PROPN' and token.dep_=='pobj' and (token.ent_type_=="GPE" or token.ent_type_=="ORG" or token.ent_type_=="LOC"):
                    bigLoc.append(str(token))
                elif token.dep_=='punct' and (token.ent_type == 'GPE' or token.ent_type == 'LOC'):
                    bigLoc.append(str(token))
            if smallLoc:
                arguments['smallLoc'] = ','.join(smallLoc)
                arguments['bigLoc'] = ','.join(bigLoc)
                thisextraction = {"template": 'Location', "sentence": str(eachSent), "arguments": arguments}
                self.extraction.append(thisextraction)

            arguments = dict()
            for l in filter(lambda x:(x.pos_=='ADP'),eachSent):
                # print(l)
                if (l.nbor(-1).ent_type_ in ['GPE','LOC'] or l.nbor(-1).pos_=='PROPN') and (l.right_edge.ent_type_ in ['GPE','LOC']):
                    arguments['smallLoc']=str((l.nbor(-1)))
                    arguments['bigLoc'] = str(l.right_edge)
                    thisextraction = {"template": 'Location', "sentence": str(eachSent), "arguments": arguments}
                    self.extraction.append(thisextraction)

            arguments = dict()
            for l in filter(lambda x:(x.dep_=='appos'),eachSent):
                if l.head.ent_type_ in ['GPE','LOC'] and l.ent_type_ in ['GPE','LOC']:
                    arguments['smallLoc']=str((l.head))
                    arguments['bigLoc'] = str(l)
                    thisextraction = {"template": 'Location', "sentence": str(eachSent), "arguments": arguments}
                    self.extraction.append(thisextraction)

        # for eachSent in doc.sents:
        #     smallLoc = []
        #     bigLoc = []
        #     leftSub = None
        #     rightSub = None
        #     for token in eachSent:
        #         if token.head.lemma_=='be' and token.dep_=='advcl':
        #             leftSub = token.subtree
        #         elif token.head.lemma_=='be' and token.dep_.find('nsubj')>=0:
        #             leftSub = token.subtree
        #         elif token.head.lemma_=='be' and token.dep_=='attr':
        #             rightSub = token.subtree
        #     # print(list(leftSub))
        #     # print(list(rightSub))
        #     if leftSub and rightSub:
        #         for token in leftSub:
        #             # print(token)
        #             if token.pos_=='PROPN' and (token.ent_type_=="GPE" or token.ent_type_=="LOC"):
        #                 smallLoc.append(token)
        #                 # print(rightSub)
        #         for token in rightSub:
        #             # print(token)
        #             if token.pos_ == 'PROPN' and token.dep_=='pobj' and (token.ent_type_=="GPE" or token.ent_type_=="ORG" or token.ent_type_=="LOC"):
        #                 bigLoc.append(token)
        #                 for i in token.conjuncts:
        #                     bigLoc.append(i)
        #                 # if smallLoc and bigLoc:
        #     if smallLoc and bigLoc:
        #         print(smallLoc,bigLoc)
        #         print(smallLoc[0].sent)

            # Located at ...





    def extract_currency_relations(self,doc):
        spans = list(doc.ents) + list(doc.noun_chunks)
        spans = self.filter_spans(spans)
        with doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)

        self.extract_currency_relations_buy_by_verb(doc)
        self.extract_currency_relations_buy_by_noun(doc)
        self.extract_currency_relations_work_verb(doc)
        self.extract_currency_relations_part_of(doc)

    def lemmatize(self,tokens):
        lemmaArr = []
        for token in tokens:
            temp = []
            for word in token:
                temp.append(lemmatizer.lemmatize(word))
            lemmaArr.append(temp)
        return lemmaArr;

    def main(self):
        self.file = open("Amazon_com_coref.txt")
        # file = open("WikipediaArticles/IBM.txt")
        # file = open("WikipediaArticles/AppleInc.txt")
        # self.file = open("WikipediaArticles/Dallas.txt")
        self.outputjson = open("outputjson.json","w")
        # file = open("test.txt")

        fl = self.file.read()
        sentences = nltk.sent_tokenize(fl) # Split the document into sentences
        tokens = [nltk.word_tokenize(sentence) for sentence in sentences] # Tokenize the sentences into words
        lemmaArr = self.lemmatize(tokens)  # Lemmatize the words to extract lemmas as features
        pos_tag = [nltk.pos_tag(token) for token in lemmaArr] # Part-of-speech (POS) tag the words to extract POS tag features

        doc = self.nlp(fl)
        relations = self.extract_currency_relations(doc)

        html = displacy.render(doc,style='dep',page=True)
        outputfile = open('dep.html',"w",encoding='utf-8')
        outputfile.write(html)

        html2 = displacy.render(doc,style='ent',page=True)

        outputfile2 = open('ent.html',"w",encoding='utf-8')
        outputfile2.write(html2)

        mydict = {"document":self.file.name,"extraction":self.extraction}
        self.outputjson.write(json.dumps(mydict))
if __name__=='__main__':
    s = Solution()
    s.main();