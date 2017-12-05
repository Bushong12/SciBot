import sys
import os
from numpy import log2
import random
from fim import apriori, fpgrowth

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

def init_paper_keywords_dict():
	# maps PID to set of keywords found in PaperKeywords.txt
	keywords = dict()
	for line in open('microsoft/PaperKeywords.txt'):
		data = line.rstrip().split('\t')
		PID = data[0]
		word = data[1]
		if PID not in keywords:
			keywords[PID] = set()
		keywords[PID].add(word)
	return keywords

def init_index_dict():
	# maps PID to (PDFID, folder)
	index = dict()
	for line in open('microsoft/index.txt'):
		data = line.rstrip().split('\t')
		folder = data[0]
		PDFID = data[1]
		PID = data[2]
		index[PID] = [PDFID, folder]
	return index

def concat_list(li):
	# given a list concatenate it into a string with | as seperators 
	str = ''
	for i, x in enumerate(li):
		if i < len(li)-1:
			str += x
			str += '|'
		else:
			str += x
	return str

def tokenizer(text):
	# based on example code given in the ResponseBot Demo
	# this processes texts into a form that is simpler to analyze
	ret = []
	for x in [',','--','!','?',';','(',')','"', '\\']: # always remove
		text = text.replace(x,' '+x+' ')
	for x in ['.', '/']: # remove only if it's end punctuation
		text = text.replace(x+' ', ' '+x+' ')
	for word in text.split(' '):
		if word == '': continue
		ret.append(word.lower())
	return ret

def check_string_guality(str):
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
	for [phrase,count] in sorted(phrase2count.items(),key=lambda x:-x[1]):
		fw.write(phrase+'\t'+str(count)+'\n')
	fw.close()

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

def DecisionTreeFirstFeature():
	positive = 'kdd' # SIGKDD Conference on Knowledge Discovery and Data Mining
	paper2label,paper2attributes,attribute2papers = {},{},{}
	fr = open('data/paper2attributes2label.txt','rb')
	for line in fr:
		arr = line.strip('\r\n').split('\t')
		paper = arr[0]
		label = (arr[1] == positive)
		paper2label[paper] = label
		attributes = arr[2].split(',')
		paper2attributes[paper] = attributes
		for attribute in attributes:
			if not attribute in attribute2papers:
				attribute2papers[attribute] = []
			attribute2papers[attribute].append(paper)
	fr.close()

	nY,nYpos = 0,0
	for [paper,label] in paper2label.items():
		nY += 1
		if label: nYpos += 1
	print '----- -----'
	print 'All','KDD','NotKDD'
	print nY,nYpos,nY-nYpos,0.001*int(1000.0*nYpos/nY)
	print ''
	HY = Entropy(nY,[nYpos])
	GiniY = Gini(nY,[nYpos])

	attribute_metrics = []
	for [attribute,papers] in attribute2papers.items():
		nXyesY = len(papers)
		nXnoY = nY-nXyesY
		nXyesYpos = 0
		for paper in papers:
			label = paper2label[paper]
			if label: nXyesYpos += 1
		nXnoYpos = nYpos-nXyesYpos
		HXyesY = 1.0*nXyesY/nY * Entropy(nXyesY,[nXyesYpos])
		HXnoY = 1.0*nXnoY/nY * Entropy(nXnoY,[nXnoYpos])
		InfoGain = HY-(HXyesY+HXnoY)

		GiniXyesY = 1.0*nXyesY/nY * Gini(nXyesY,[nXyesYpos])
		GiniXnoY = 1.0*nXnoY/nY * Gini(nXnoY,[nXnoYpos])
		DeltaGini = GiniY-(GiniXyesY+GiniXnoY)
		
		attribute_metrics.append([attribute,[InfoGain,DeltaGini],[nXyesYpos,nXyesY-nXyesYpos,nXnoYpos,nXnoY-nXnoYpos]])

	bestattributeset = set()

	print '----- First Feature to Select in ID3: Information Gain -----'
	OutputStr(['Attribute',['InfoGain','DeltaGini'],['HasWord & KDD','HasWord & NotKDD','NoWord & KDD','NoWord & NotKDD']])
	sorted_attribute_metrics = sorted(attribute_metrics,key=lambda x:-x[1][0])
	for i in range(0,5):
		Output(sorted_attribute_metrics[i])
		bestattributeset.add(sorted_attribute_metrics[i][0])
	print ''

	print '----- First Feature to Select in CART: Delta Gini index -----'
	OutputStr(['Attribute',['InfoGain','DeltaGini'],['HasWord & KDD','HasWord & NotKDD','NoWord & KDD','NoWord & NotKDD']])
	sorted_attribute_metrics = sorted(attribute_metrics,key=lambda x:-x[1][1])
	for i in range(0,5):
		Output(sorted_attribute_metrics[i])
		bestattributeset.add(sorted_attribute_metrics[i][0])
	print ''

	fw = open('data/bestattributes.txt','w')
	for attribute in sorted(bestattributeset):
		fw.write(attribute+'\n')
	fw.close()

def NaiveBayes():
	positive = 'kdd' # SIGKDD Conference on Knowledge Discovery and Data Mining
	bestattributeset = set()
	fr = open('data/bestattributes.txt','rb')
	for line in fr:
		attribute = line.strip('\r\n')
		bestattributeset.add(attribute)
	fr.close()

	paper2label,paper2attributes,attribute2papers = {},{},{}
	fr = open('data/paper2attributes2label.txt','rb')
	for line in fr:
		arr = line.strip('\r\n').split('\t')
		attributeset = set(arr[2].split(','))
		selectedattributeset = bestattributeset & attributeset
		#if len(selectedattributeset) < 2 or len(selectedattributeset) > 4: continue
		paper = arr[0]
		label = (arr[1] == positive)
		paper2label[paper] = label
		paper2attributes[paper] = sorted(selectedattributeset)
		for attribute in selectedattributeset:
			if not attribute in attribute2papers:
				attribute2papers[attribute] = []
			attribute2papers[attribute].append(paper)
	fr.close()

	for [paper,attributes] in paper2attributes.items():
		print paper,attributes

	nY,nYpos = 0,0
	for [paper,label] in paper2label.items():
		nY += 1
		if label: nYpos += 1
	print ''
	print '----- -----'
	print 'All','KDD','NotKDD'
	print nY,nYpos,nY-nYpos,0.001*int(1000.0*nYpos/nY)
	print '----- Prior Probability -----'
	PYesPrior = 1.0*nYpos/nY
	PNoPrior = 1.0*(nY-nYpos)/nY
	print 'P(KDD) = ',0.001*int(1000.0*PYesPrior)
	print 'P(NotKDD) = ',0.001*int(1000.0*PNoPrior)
	print ''

	allpapers = paper2label.keys()
	random.shuffle(allpapers)
	for i in range(0,5):
		paper = allpapers[i]
		print '----- Paper ',i,':',paper,'-->',paper2label[paper],' -----'
		attributes = paper2attributes[paper]
		print '----- Likelihood -----'
		PYesLikelihoodAll = 1.0
		PNoLikelihoodAll = 1.0
		for [attribute,papers] in attribute2papers.items():
			if attribute in attributes:
				# P(word=yes|KDD), P(word=yes|NotKDD)
				nYesLikelihood = 0
				nNoLikelihood = 0
				for [paper,label] in paper2label.items():
					if paper in papers:
						if label: nYesLikelihood += 1
						else: nNoLikelihood += 1
				PYesLikelihood = 1.0*nYesLikelihood/nYpos
				PNoLikelihood = 1.0*nNoLikelihood/(nY-nYpos)
				PYesLikelihoodAll *= PYesLikelihood
				PNoLikelihoodAll *= PNoLikelihood
			else:
				# P(word=no|KDD), P(word=no|NotKDD)
				nYesLikelihood = 0
				nNoLikelihood = 0
				for [paper,label] in paper2label.items():
					if not paper in papers:
						if label: nYesLikelihood += 1
						else: nNoLikelihood += 1
				PYesLikelihood = 1.0*nYesLikelihood/nYpos
				PNoLikelihood = 1.0*nNoLikelihood/(nY-nYpos)
				PYesLikelihoodAll *= PYesLikelihood
				PNoLikelihoodAll *= PNoLikelihood
		print 'P(X|KDD) = ',0.001*int(1000.0*PYesLikelihoodAll)
		print 'P(X|NotKDD) = ',0.001*int(1000.0*PNoLikelihoodAll)
		print '----- Posteriori Probability -----'
		PYesPost = PYesPrior*PYesLikelihoodAll
		PNoPost = PNoPrior*PNoLikelihoodAll
		print 'P(KDD|X) ~ P(X|KDD)P(KDD)',0.0001*int(10000.0*PYesPost)
		print 'P(NotKDD|X) ~ P(X|NotKDD)P(NotKDD)',0.0001*int(10000.0*PNoPost)
		print '--> Prediction:',(PYesPost > PNoPost)
		print ''

def SimpleEntityTyping():
	n_type = 4
	s_method = 'method algorithm model approach framework process scheme implementation procedure strategy architecture'
	s_problem = 'problem technique process system application task evaluation tool paradigm benchmark software'
	s_dataset = 'data dataset database'
	s_metric = 'value score measure metric function parameter'
	types = ['METHOD','PROBLEM','DATASET','METRIC']
	wordsets = [set(s_method.split(' ')),set(s_problem.split(' ')),set(s_dataset.split(' ')),set(s_metric.split(' '))]

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

	# "__ __ __ __ __ support vector machine __ __ __ __ __"
	n_context = 5
	phrase2classifiers = {}
	for [paperid,path] in paperid_path:
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
						if not phrase in phrase2classifiers:
							phrase2classifiers[phrase] = [0,[[0 for t in range(0,n_type)] for c in range(0,n_context)]]
						phrase2classifiers[phrase][0] += 1
						for c in range(0,n_context):
							if i-1-c >= 0:
								trigger = wordslower[i-1-c]
								for t in range(0,n_type):
									if trigger in wordsets[t]:
										phrase2classifiers[phrase][1][c][t] += 1
#										for _c in range(c,n_context):
#											phrase2classifiers[phrase][1][_c][t] += 1
							if i+k+c < l:
								trigger = wordslower[i+k+c]
								for t in range(0,n_type):
									if trigger in wordsets[t]:
										phrase2classifiers[phrase][1][c][t] += 1
#										for _c in range(c,n_context):
#											phrase2classifiers[phrase][1][_c][t] += 1
						isvalid = True
						break
				if isvalid:
					i += j
					continue
				i += 1
		fr.close()
	fw = open('data/entitytyping.txt','w')
	s = 'ENTITY\tCOUNT'
	for c in range(0,n_context): s += '\tWINDOWSIZE'+str(c+1)
	fw.write(s+'\n')
	for [phrase,[count,ctmatrix]] in sorted(phrase2classifiers.items(),key=lambda x:-x[1][0]):
		s = phrase+'\t'+str(count)
		for c in range(0,n_context):
			maxv,maxt = -1,-1
			for t in range(0,n_type):
				v = ctmatrix[c][t]
				if v > maxv:
					maxv = v
					maxt = t
			if maxv == 0:
				s += '\tN/A'
			else:
				s += '\t'+types[maxt]
				for t in range(0,n_type):
					v = ctmatrix[c][t]
					if v == 0: continue
					s += ' '+types[t][0]+types[t][-1]+':'+str(v)
		fw.write(s+'\n')
	fw.close()
	
class Paper(object):
	def __init__(self, pid, title, year, conf):
		self.PID = pid
		self.authors = set()
		self.author_ids = set()
		self.keywords = set()
		self.conf = conf
		self.year = year
		self.title = title
		try:
			self.PDFID = index_dict[self.PID][0]
			self.folder = index_dict[self.PID][1]
		except KeyError:
			self.PDFID = 'na'
			self.folder = 'na'
		self.affil = ''
		
	def make_author_sets(self):
		# paper_author maps PID to (author_id, affiliation)
		author_pairs = paper_author[self.PID]
		for pair in author_pairs:
			id = pair[0]
			self.author_ids.add(id)
		# author_names maps AID to author name
		for id in self.author_ids:
			name = author_names[id]
			self.authors.add(name)
	
	def set_affil(self, affil_dict):
		# uses paper_author dict PID:(AID, affil)
		author_affils = affil_dict[self.PID]
		self.affil = author_affils[0][1]
	
	def make_keyword_set(self):
		try:
			self.keywords = paper_keywords[self.PID]
		except KeyError:
			self.keywords.add('na')
	
if __name__ == '__main__':
	# csv for PID,PDFID,title,conf,folder,year,affil,authors,author_ids,keywords
	integrated_data = open('data/integrated.csv', 'w+')
	
	# initialize the dictionaries 
	author_names = init_author_dict()
	print('Number of authors: {}'.format(str(len(author_names))))
	paper_author = init_paper_author_dict()
	paper_keywords = init_paper_keywords_dict()
	index_dict = init_index_dict()
	entity_candidates = dict()
	allwords = [] # list containing the important words from each document that we'd want to scan through
	stopwords = set()

	# create set of entity candidates
	for key in paper_keywords:
		for word in paper_keywords[key]:
			entity_candidates[word] = 0

	# create set of stopwords - ResponseBot #2
	for line in open('microsoft/stopwords.txt'):
		word = line.strip('\r\n').lower()
		stopwords.add(word)
	
	# CSV header
	integrated_data.write("PID,PDFID,title,conf,folder,year,affil,authors,author_ids,keywords\n")
	num_papers = 0
	# process Papers
	for line in open('microsoft/Papers.txt'):
		data = line.rstrip().split('\t')
		# parse data
		PID = data[0]		
		title = data[2]
		year = int(data[3])
		conf = data[7]
		
		# error checking 
		confs = {'icdm', 'kdd', 'wsdm', 'www'}
		if conf not in confs:
			continue
		if year > 2016 or year < 1994:
			continue
			
		# make new Paper object
		paper = Paper(PID, title, year, conf)
		paper.make_author_sets()
		paper.set_affil(paper_author)
		temp_key = paper.make_keyword_set()
		
		if paper.PDFID == 'na':
			continue
		
		# output all the data 
		paper_data = "{},{},{},{},{},{},{},{},{},{}\n".format(paper.PID, 
													  paper.PDFID, 
													  paper.title, 
													  paper.conf,
													  paper.folder,
													  paper.year,
													  paper.affil,
													  concat_list(paper.authors),
													  concat_list(paper.author_ids),
													  concat_list(paper.keywords)
													)
		integrated_data.write(paper_data)
		num_papers += 1
		
	print('Number of papers: {}'.format(str(num_papers)))
	
	# Task 2: Entity Mining - Name Detection (paperclassification.py functions)
	SimpleEntityExtraction()
	SimpleAttributeExtraction()
	SimpleLabelExtraction()
	DecisionTreeFirstFeature()
	NaiveBayes()

	# Task 3: Entity Typing (entitytyping.py functions)
	#SimpleEntityTyping() # must run SimpleEntityExtraction before this code

	'''
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
	#	if support == 1: break
	#	print word,support

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
	#	print bigram,score[0],score[1],score[2],score[3]

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
			#	i += 1
			#	continue
			transaction.add(words[i])
			i += 1
		if not transaction: continue
		author_transactions.append(list(transaction))
	# output
	#for transaction in author_transactions:
	#	print transaction

	print "Done with author transactions"


	#patterns = apriori(author_lists, supp=-12)
	patterns = apriori(author_transactions, supp=-3)
	print '-------- Author Affiliation Apriori --------'
	for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
		if len(pattern) <= 1: continue
		print pattern,support
	print 'Number of patterns:',len(patterns)
	'''
	print("Done.")