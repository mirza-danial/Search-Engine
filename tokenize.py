from os import listdir, path
from argparse import ArgumentParser
import re
import sys
sys.setrecursionlimit(10000)

termsDict = {}  # contains term_ids for each stem
doc_ids = [] # contains doc_ids
doc_index = [] # contains list of tuples <term_id, doc_id,position>


def getStopWords():
    file = open('stoplist.txt', 'r')
    return set(file.read().split())  # set having no duplicate elements


def tokenize(direc, stopWords):
    global termsDict, doc_ids, doc_index

    # termsDict -> ids for terms
    # terms -> all positions for single term in current file

    terms = {}
    for ID, name in enumerate(listdir(direc), start=1):
        terms.clear()  # clearing terms for next file

        file = open(path.join(direc, name), encoding="ISO-8859-1")
        print(str(ID) + " :  " +name);
        text = getFileText(file.read())

        # Stemming for current file
        saveStems(re.finditer("[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+", text.strip(), flags=re.IGNORECASE), stopWords, terms)

        # Saving the tokens' ids and positions for current file
        for termid, pos_list in sorted(terms.items()):
            tmp = [[termid,ID,i] for i in pos_list]
            doc_index.extend(tmp)
            
        doc_ids.append('%d\t%s' % (ID, name))  # DocID + fileName        
        file.close()


def saveStems(iterator, stopWords, terms):
    global termsDict, doc_ids, doc_index

    token_id = len(termsDict) + 1  # if termsDic contains terms already
    position = 0
    stems = {}

    from nltk.stem import PorterStemmer as Stemmer
    stemmer = Stemmer()
    for i in iterator:
        position = position + 1
        token = i.group()
        if token is not None and token not in stopWords:  # if !StopWord
            token = token.lower()
            stem = stemmer.stem(token)

            if stem in stems:  # checking if already in stems
                stemid = termsDict[stem]
                tmp = terms[stemid]  # positions in rest of document
                tmp.append(position)  # add new position
                terms[stemid] = tmp
            else:
                stems[stem] = token_id
                positions = []
                positions.append(position)
                if stem not in termsDict:
                    termsDict[stem] = token_id
                    terms[token_id] = positions
                    token_id = token_id + 1  # for new token
                else:
                    terms[termsDict[stem]] = positions


def getFileText(html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html,"html.parser") # create a new bs4 object from the html data loaded
    html = str(soup.find('body'))
    text = ''
    if html is not None and html != '':
        from bs4 import UnicodeDammit
        import lxml.html.clean
        import lxml.html
        doc = UnicodeDammit(html, is_html=True)  # converting to utf-8
        # cleaning html data and getting Text
        tree = lxml.html.document_fromstring(html, parser=lxml.html.HTMLParser(encoding=doc.original_encoding))
        tree = lxml.html.clean.Cleaner(style=True).clean_html(tree)
        text = tree.text_content()
    return " ".join(text.split())   


def saveFiles():
    from operator import itemgetter
    global doc_ids, doc_index, termsDict

    # getting term_ids tuple from term dictionary for each term
    term_ids = ['%d\t%s' % (tId, term) for term, tId in sorted(termsDict.items(), key=itemgetter(1))]

    writeFile('docids.txt', '\n'.join(doc_ids))
    writeFile('termids.txt', '\n'.join(term_ids))


def writeFile(direct, data):    
    file = open(direct, 'w',encoding = 'utf-8')
    file.write(str(data))
    file.close()

# Step 2: 

# ************************************* Without HashMAps *******************************************

def writeInvertedIndex_sorted(inverted_index):
    def getTermFreq(term_list):
        termFreq = 0
        for value_list in term_list[1]:       # calculate term frequency
            termFreq = termFreq + len(value_list[1])
        return termFreq

    def getDocFreq(term_list):
        return len(term_list[1])

    term_index = open('term_index_without_hashmap.txt', 'w')

    for term_list in inverted_index:
        line = str(term_list[0]) + " " + str(getTermFreq(term_list)) + " " + str(getDocFreq(term_list)) + " "
        doc = term_list[1]
        for doc_list in doc :
            doc_id = doc_list[0]
            doc_positions = doc_list[1]
            for id, position in enumerate(doc_positions):
                if id > 0:
                    doc_id = 0
                
                line = line + str(doc_id) +"," +str(position) + " "

        term_index.write(line + "\n")
                       
    
    term_index.close()

def deltaEncode_sorted(terms):
    delta_list = []
    for termList in terms:
        delta_term = [termList[0]]
        delta_docs = []
        
        term = termList[0]
        docs = termList[1]
        
        docFlag = False
        prevDocId = -1
        for doclist in docs:
            delta_doclist = []
            
            if docFlag:
                temp = doclist[0]
                #doclist[0] = 
                delta_doclist.append(doclist[0] - prevDocId)
                prevDocId = temp
            else:
                prevDocId = doclist[0]
                delta_doclist.append(doclist[0])
                docFlag = True
                
            positionFlag = False
            positionList = []
            prevPosition = -1
            
            for position in doclist[1]:
                if positionFlag:
                    temp = position
                    positionList.append(position - prevPosition)
                    prevPosition = temp
                else:
                    prevPosition = position
                    positionList.append(position)
                    positionFlag = True
                    
            delta_doclist.append( positionList)
            delta_docs.append(delta_doclist)
        delta_term.append(delta_docs)
        delta_list.append(delta_term)
    
    return delta_list

def createInvertedIndex_sorted():
    from operator import itemgetter
    doc_index_sorted = sorted(doc_index, key = itemgetter(2)) # sort on basis of position  
    doc_index_sorted = sorted(doc_index_sorted, key = itemgetter(1)) # sort on basis of doc_id
    doc_index_sorted = sorted(doc_index_sorted, key = itemgetter(0)) # sort on basis of term_id

    inverted_index = []        #list that contains inverted index
    prev_list_item = [-1,-1,-1]
    term_list = []
    docs = []
    doc_list = []
    posting_list = []

    for list_item in doc_index_sorted:

        if prev_list_item[0] != list_item [0]:
            doc_list.append(posting_list)
            docs.append(doc_list)
            term_list.append(docs)
            inverted_index.append(term_list)
            term_list = [list_item[0]]
            docs = []
            doc_list = [list_item[1]]
            posting_list = []
        elif prev_list_item[1] != list_item[1]:
            doc_list.append(posting_list)
            docs.append(doc_list)
            doc_list = [list_item[1]]
            posting_list = []
        posting_list.append(list_item[2])
        prev_list_item = list_item

    return inverted_index[1:]

# ************************************* With HashMAps *******************************************

def writeInvertedIndex_hashmap(invertedIndex):
    def getTermFreq(termid):
        termFreq = 0
        for doc in invertedIndex[termid]:       # calculate term frequency
            termFreq = termFreq + len(invertedIndex[termid][doc])
        return termFreq
    def getDocFreq(termid):
        return len(invertedIndex[termid])

    term_index = open('term_index_hashmap.txt', 'w')
    for termid in invertedIndex:
        term_index.write('%d %d %d %s\n' %(termid,getTermFreq(termid),getDocFreq(termid),getdocposString(invertedIndex[termid]) ))
        
        
    term_index.close()

def getdocposString(doc_dict):
    retval = ""
    prev_doc = 0
    for doc in doc_dict:
        positions = doc_dict[doc]
        temp = doc
        doc = doc - prev_doc
        prev_pos = 0
        for id,pos in enumerate(positions):
            if id > 0:
                doc = 0
            tmp = pos
            pos = pos - prev_pos
            retval += str(doc) + ',' + str(pos) +' '
            prev_pos = tmp

        prev_doc = temp

    return retval

def createInvertedIndex_hashmap():
    #create inverted index by dictionary
    term_list = {}
    for i in doc_index:
        term_id = i[0]
        doc_id = i[1]
        position = i[2]
        
        if term_id not in term_list:
            term_list[term_id] = {doc_id:[position]}

        else:
            if doc_id not in term_list[term_id]:
                term_list[term_id][doc_id] = [position]
            else:
                term_list[term_id][doc_id].append(position)

    return term_list

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--folder')
    args = parser.parse_args()
    tokenize(args.folder, getStopWords())
    saveFiles()
    
    writeInvertedIndex_sorted(deltaEncode_sorted(createInvertedIndex_sorted()))
    
    writeInvertedIndex_hashmap(createInvertedIndex_hashmap())
