import os
import sys
from numpy import log2
import random

def SimpleEntityExtraction():
    paperid_path = []
    fr = open('microsoft/index.txt','rb')
    for line in fr:
        arr = line.strip('\r\n').split('\t')
        paperid = arr[2]
        path = 'text/'+arr[0]+'/'+arr[1]+'.txt'
        paperid_path.append([paperid,path])
    fr.close()
    phrase2count = {}
    for [paperid,path] in paperid_path:
        fr = open(path,'rb')
        for line in fr:
            arr = line.strip('\r\n').split(' ')
            n = len(arr)
            if n < 5: continue
            for i in range(0,n-2):
                if arr[i] == '(' and arr[i+2] == ')':
                    abbr = arr[i+1]
                    l = len(abbr)
                    if l > 1 and abbr.isalpha():
                        if i >= l and abbr.isupper():
                            isvalid = True
                            for j in range(0,l):
                                if not abbr[l-1-j].lower() == arr[i-1-j][0].lower():
                                    isvalid = False
                            if isvalid:
                                phrase = ''
                                for j in range(0,l):
                                    phrase = arr[i-1-j]+' '+phrase
                                phrase = phrase[0:-1].lower()
                                if not phrase in phrase2count:
                                    phrase2count[phrase] = 0
                                phrase2count[phrase] += 1
                        if i >= l-1 and abbr[-1] == 's' and arr[i-1][-1] == 's' and abbr[0:-1].isupper():
                            isvalid = True
                            for j in range(1,l):
                                if not abbr[l-1-j].lower() == arr[i-j][0].lower():
                                    isvalid = False
                            if isvalid:
                                phrase = ''
                                for j in range(1,l):
                                    phrase = arr[i-j]+' '+phrase
                                phrase = phrase[0:-1].lower()
                                if not phrase in phrase2count:
                                    phrase2count[phrase] = 0
                                phrase2count[phrase] += 1
        fr.close()
    fw = open('data/phrase2count.txt','w')
    num_entities = 0
    for [phrase,count] in sorted(phrase2count.items(),key=lambda x:-x[1]):
        fw.write(phrase+'\t'+str(count)+'\n')
        num_entities += 1
    fw.close()
    print('Number of entities: {}'.format(str(num_entities)))

def SimpleAttributeExtraction():
    paperid_path = []
    fr = open('microsoft/index.txt','rb')
    for line in fr:
        arr = line.strip('\r\n').split('\t')
        paperid = arr[2]
        path = 'text/'+arr[0]+'/'+arr[1]+'.txt'
        paperid_path.append([paperid,path])
    fr.close()
    index,nindex = [{}],1 # phrase's index
    fr = open('data/phrase2count.txt','rb')
    for line in fr:
        arr = line.strip('\r\n').split('\t')
        phrase = arr[0]
        words = phrase.split(' ')
        n = len(words)
        if n > nindex:
            for i in range(nindex,n):
                index.append({})
            nindex = n
        temp = index[n-1]
        if n > 1:
            for i in range(0,n-1):
                word = words[i]
                if not word in temp:
                    temp[word] = {}
                temp = temp[word]
            word = words[n-1]
        else:
            word = words[0]
        temp[word] = phrase
    fr.close()
    fw = open('data/paper2attributes.txt','w')
    for [paperid,path] in paperid_path:
        attributeset = set()
        fr = open(path,'rb')
        for line in fr:
            words = line.strip('\r\n').split(' ')
            wordslower = line.strip('\r\n').lower().split(' ')
            l = len(words)
            i = 0
            while i < l:
                isvalid = False
                for j in range(min(nindex,l-i),0,-1):
                    temp = index[j-1]
                    k = 0
                    while k < j and i+k < l:
                        tempword = wordslower[i+k]
                        if not tempword in temp: break
                        temp = temp[tempword]
                        k += 1
                    if k == j:
                        phrase = temp
                        attributeset.add(phrase)
                        isvalid = True
                        break
                if isvalid:
                    i += j
                    continue
                i += 1
        fr.close()
        if len(attributeset) == 0: continue
        s = ''
        for attribute in sorted(attributeset):
            s += ','+attribute
        fw.write(paperid+'\t'+s[1:]+'\n')
    fw.close()

def SimpleLabelExtraction():
    paperid2conf = {}
    fr = open('microsoft/Papers.txt','rb')
    for line in fr:
        arr = line.strip('\r\n').split('\t')
        paperid,conf = arr[0],arr[7]
        paperid2conf[paperid] = conf
    fr.close()
    fw = open('data/paper2attributes2label.txt','w')
    fr = open('data/paper2attributes.txt','rb')
    for line in fr:
        arr = line.strip('\r\n').split('\t')
        paperid = arr[0]
        if not paperid in paperid2conf: continue
        conf = paperid2conf[paperid]
        fw.write(arr[0]+'\t'+conf+'\t'+arr[1]+'\n')
    fr.close()
    fw.close()
def Entropy(n,values):
    ret = 0.0
    for value in values:
        p_i = 1.0*value/n
        if not p_i == 0:
            ret += -1.0*p_i*log2(p_i)
    p_i = 1.0*(n-sum(values))/n
    if not p_i == 0:
        ret += -1.0*p_i*log2(p_i)
    return ret

def Gini(n,values):
    ret = 1.0
    for value in values:
        p_i = 1.0*value/n
        ret -= p_i*p_i
    p_i = 1.0*(n-sum(values))/n
    ret -= p_i*p_i
    return ret

def Output(entry):
    print entry[0],0.001*int(1000.0*entry[1][0]),0.001*int(1000.0*entry[1][1]),entry[2], \
        0.001*int(1000.0*entry[2][0]/(entry[2][0]+entry[2][1])), \
        0.001*int(1000.0*entry[2][2]/(entry[2][2]+entry[2][3]))

def OutputStr(entry):
    print entry[0],entry[1][0],entry[1][1],entry[2]


if __name__ == '__main__':
    # Task 2: Entity Mining - Name Detection (paperclassification.py functions)
    SimpleEntityExtraction()
    SimpleAttributeExtraction()
    SimpleLabelExtraction()


