# NLP Data Extraction
This is to implement an Information Extraction application using NLP features and techniques.

## **Training**
**Input**
- 30 text articles:
    - 10 articles related to Organizations
    - 10 articles related to Persons
    - 10 articles related to Locations

- Set of information templates:
    - Template #1:  
    *BUY(Buyer, Item, Price, Quantity, Source)*
    - Template #2:  
    *WORK(Person, Organization, Position, Location)*
    - Template #3:  
    *PART(Location, Location)*

## **Testing/Runtime**
**Input**
- Text article  

**Output**
- All instances (i.e. filled) of the above three templates found in the input text article
- Output Format (JSON): TBA

## **Tasks that Need to be Performed**
**Task 1:** Implement a deep NLP pipeline to extract the following NLP based features from the text articles/documents: 
- Split the document into sentences
- Tokenize the sentences into words 
- Lemmatize the words to extract lemmas as features 
- Part-of-speech (POS) tag the words to extract POS tag features 
- Perform dependency parsing or full-syntactic parsing to get parse-tree based patterns as features 
- Using WordNet, extract hypernymns, hyponyms, meronyms, AND holonyms as features 
- Some additional features that you can think of, which may make your representation better 

**Task 2:** Implement a machine-learning, statistical, or heuristic (or a combination) based approach to extract filled information templates from the corpus of text articles:
- Run the above described deeper NLP on the corpus of text articles and extract NLP features
- Extract information templates from the input text document using your information extraction approach implemented in Task 2
- Output a JSON file with extracted/filled information templates from the input text document

## **Performance Evaluation**
The performance of your NLP and Information Extraction system will evaluated on an **unseen** test corpus of text articles.