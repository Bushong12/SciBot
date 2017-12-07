import sys
import os
from fim import apriori

def init_author_dict():
    # maps AID to author name
    names = dict()
    for line in open('microsoft/Authors.txt'):
        data = line.rstrip().split('\t')
        AID = data[0]
        name = data[1]
        names[AID] = name
    return names

def init_paper_author_dict():
    # maps PID to list of authors that are a pair of (author_id, affiliation)
    d = dict()
    for line in open('microsoft/PaperAuthorAffiliations.txt'):
        data = line.rstrip().split('\t')
        PID = data[0]
        AID = data[1]
        aff = data[4]
        seq_num = data[5]
        author_obj = [AID, aff]
        if PID not in d:
            d[PID] = list()
        d[PID].append(author_obj)
    return d     

def check_string_guality(str):
    # ckeck if a string has any undesired characters
    if '<' in str:
        return False
    if '>' in str:
        return False
    if '[' in str:
        return False
    if ']' in str:
        return False
    if '{' in str:
        return False
    if '}' in str:
        return False
    if '=' in str:
        return False
    if '+' in str:
        return False
    if ':' in str:
        return False
    if '-' in str:
        return False
    if '\\' in str:
        return False
    
    return True   

if __name__ == '__main__':
    author_names = init_author_dict()
    paper_author = init_paper_author_dict()
    output_file = open('data/authorcollaborations.txt', 'w+')

    # Task 4: Finding two-four authors that often collaborate
    # basically we'll do a similar thing we already did with the keywords with the author data
    author_lists = [] # list of lists of authors on each paper
    aid_lists = [] # list of lists of author id's on each paper
    for key in paper_author:
        author_list = []
        aid_list = []
        for each in paper_author[key]:
            aid_list.append(each[0])
            name = author_names[each[0]]
            author_list.append(name)
        #print author_list
        #print aid_list
        author_lists.append(author_list)
        aid_lists.append(aid_list)

    # find the support for each entity candidate (ResponseBot 2)
    author2support = {}
    for words in author_lists:
        for word in words:
            #if word in stopwords or len(word) == 1 or word.isdigit() or len(word) > 25: continue
            #if not word.isalnum(): continue
            if not word in author2support:
                author2support[word] = 0
            author2support[word] += 1
    # output
    #for [word,support] in sorted(author2support.items(),key=lambda x:-x[1]):
    #   if support == 1: break
    #   print word,support

    # Find bigram for each entity candidate (ResponseBot 3)
    author2count = {}
    for words in author_lists:
        for word in words:
            #if word in stopwords or len(word) == 1 or word.isdigit() or len(word) > 25: continue
            #if not word.isalnum(): continue
            if not word in author2count:
                author2count[word] = 0
            author2count[word] += 1

    abigram2score = {} # bigram's count, first word's count, second word's count, significance score
    L = 0
    for words in author_lists:
        n = len(words)
        L += n
        for i in range(0, n-1):
            if words[i] in author2count and words[i+1] in author2count:
                bigram = words[i] + '_' + words[i+1]
                if not bigram in abigram2score:
                    abigram2score[bigram] = [0,author2count[words[i]],author2count[words[i+1]],0.0]
                abigram2score[bigram][0] += 1
    for bigram in abigram2score:
        abigram2score[bigram][3] = (1.0*abigram2score[bigram][0]-1.0*abigram2score[bigram][1]*abigram2score[bigram][2]/L)/((1.0*abigram2score[bigram][0])**0.5)
    # output
    #print 'bigram', 'count-bigram', 'count-first-word','count-second-word','significance-score'
    #for [bigram,score] in sorted(abigram2score.items(),key=lambda x:-x[1][3]):
    #   print bigram,score[0],score[1],score[2],score[3]

    # find transactions for bigrams (ResponseBot 4)
    abigramdict = {}
    for bigram in abigram2score:
        if abigram2score[bigram][0] > 1:
            #[firstword,secondword] = bigram.split('_')
            firstword = bigram.split('_')[0]
            secondword = bigram.split('_')[0]
            #print bigram.split('_')
            if not firstword in abigramdict:
                abigramdict[firstword] = set()
            abigramdict[firstword].add(secondword)

    author_transactions = [] # response
    for words in author_lists:
        transaction = set() # set of words/bigrams
        n = len(words)
        i = 0
        while i < n:
            if words[i] in abigramdict and i+1 < n and words[i+1] in abigramdict[words[i]]:
                transaction.add(words[i]+'_'+words[i+1])
                i += 2
                continue
            #if words[i] in stopwords or len(words[i]) == 1 or words[i].isdigit() or not words[i].isalnum() or len(words[i]) > 25:
            #   i += 1
            #   continue
            if not check_string_guality(words[i]):
                i += 1
                continue
            transaction.add(words[i])
            i += 1
        if not transaction: continue
        author_transactions.append(list(transaction))
    # output
    #for transaction in author_transactions:
    #   print transaction

    print "Done with author transactions"


    #patterns = apriori(author_lists, supp=-12)
    patterns = apriori(author_transactions, supp=-10)
    print '-------- Author Affiliation Apriori --------'
    #for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
     #   if len(pattern) <= 1: continue
      #  print pattern,support
    for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
        #pattern is a tuple
        if len(pattern) <= 1: continue
        output_file.write('{} {} \n'.format(pattern, str(support)))
    print 'Number of patterns:',len(patterns)


