from timeit import default_timer 
from argparse import ArgumentParser
from nltk.stem import PorterStemmer as Stemmer
import tokenize

def readIndex():
    term_index = open('term_index_hashmap.txt','rU',encoding = 'utf-8')
    info = {}
    for line in term_index.readlines():
        indexes = line.strip().split(' ')
        term_freq = indexes[1]
        doc_freq = indexes[2]
        info[int(indexes[0])] = (term_freq, doc_freq)
    
    term_index.close()
    return info


def getTermID(term):
    term_ids_file = open('termids.txt', 'rU',encoding = 'utf-8')
    
    for line in term_ids_file.readlines():
        indexes = line.strip().split('\t')
        if term == indexes[1]:
            term_ids_file.close()
            return int(indexes[0])
    
    term_ids_file.close()
    return 0



if __name__ == '__main__':
    start = default_timer()
    parser = ArgumentParser()
    parser.add_argument('--term')
    args = parser.parse_args()
    info = readIndex()
    stemmer = Stemmer()   
    if args.term:
        termID = getTermID(stemmer.stem(args.term))
        if termID:
            freq = info[termID]
            print ('Listing for term: %s' %(args.term))
            print ('TERMID: %d' %(termID))
            print ('Number of documents containing term: %s' %(freq[1]))
            print ('Term frequency in corpus: %s' %(freq[0]))
        else:
            print ('No such term exists in Corpus')
        
    