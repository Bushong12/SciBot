import sys
import os

def init_author_dict():
	# maps AID to author name
	names = dict()
	for line in open('Authors.txt'):
		data = line.rstrip().split('\t')
		AID = data[0]
		name = data[1]
		names[AID] = name
	return names
		
def init_paper_author_dict():
	# maps PID to list of authors that are a pair of (author_id, affiliation)
	d = dict()
	for line in open('PaperAuthorAffiliations.txt'):
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
	for line in open('PaperKeywords.txt'):
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
	for line in open('index.txt'):
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
	for x in [',','.','--','!','?',';','(',')','/','"']:
		text = text.replace(x,' '+x+' ')
	for word in text.split(' '):
		if word == '': continue
		ret.append(word.lower())
	return ret
	
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
	# initialize the dictionaries 
	author_names = init_author_dict()
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
	for line in open('stopwords.txt'):
		word = line.strip('\r\n').lower()
		stopwords.add(word)
	
	# CSV header
	print("PID,PDFID,title,conf,folder,year,affil,authors,author_ids,keywords")
	
	# process Papers
	for line in open('Papers.txt'):
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
		paper_data = "{},{},{},{},{},{},{},{},{},{}".format(paper.PID, 
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
		#print(paper_data)

	all_files = list()
	# walk through all directories
	for root, dirs, files in os.walk("../text"):
		for subdir in dirs:
			path = os.path.join(root, subdir)
			for subroot, subdirs, subfiles in os.walk(path):
				for file_name in subfiles:
					file_path = os.path.join(path, file_name)
					all_files.append(file_path)

	# create list of lists of all important words in the documents (ResponseBot 1)
	for doc in all_files:
		for line in open(doc):
			words = tokenizer(line.rstrip())
			allwords.append(words)
	#for words in allwords: print words
	

	'''
	# scan the words in all files to get support counts for entity words
	for doc in all_files:
		for line in open(doc):
			temp = tokenizer(line.rstrip())
			for word in temp:
				if word in stopwords or len(word) == 1 or word.isdigit(): continue
				if not word in entity_candidates:
					entity_candidates[word] = 0
				entity_candidates[word] += 1
	print(entity_candidates)
	#output
	for [word,support] in sorted(entity_candidates.items(), key=lambda x:-x[1]):
		if support == 1: break
		print word,support
	'''

	# find the support for each entity candidate (ResponseBot 2)
	word2support = {}
	for words in allwords:
		for word in set(words):
			if word in stopwords or len(word) == 1 or word.isdigit(): continue
			if not word.isalnum(): continue
			if not word in word2support:
				word2support[word] = 0
			word2support[word] += 1
	# output
	for [word,support] in sorted(word2support.items(),key=lambda x:-x[1]):
		if support == 1: break
		print word,support

	# Find bigram for each entity candidate (ResponseBot 3)
	word2count = {}
	for words in allwords:
		for word in words:
			if word in stopwords or len(word) == 1 or word.isdigit(): continue
			if not word.isalnum(): continue
			if not word in word2count:
				word2count[word] = 0
			word2count[word] += 1
	bigram2score = {} # bigram's count, first word's count, second word's count, significance score
	L = 0
	for words in allwords:
		n = len(words)
		L += n
		for i in range(0, n-1):
			if words[i] in word2count and words[i+1] in word2count:
				bigram = words[i] + '_' + words[i+1]
				if not bigram in bigram2score:
					bigram2score[bigram] = [0,word2count[words[i]],word2count[words[i+1]],0.0]
				bigram2score[bigram][0] += 1
	for bigram in bigram2score:
		bigram2score[bigram][3] = (1.0*bigram2score[bigram][0]-1.0*bigram2score[bigram][1]*bigram2score[bigram][2]/L)/((1.0*bigram2score[bigram][0])**0.5)
	# output
	print 'bigram', 'count-bigram', 'count-first-word','count-second-word','significance-score'
	for [bigram,score] in sorted(bigram2score.items(),key=lambda x:-x[1][3]):
		print bigram,score[0],score[1],score[2],score[3]



	# find transactions for bigrams (ResponseBot 4)
	bigramdict = {}
	for bigram in bigram2score:
		if bigram2score[bigram][0] > 1:
			#[firstword,secondword] = bigram.split('_')
			firstword = bigram.split('_')[0]
			secondword = bigram.split('_')[0]
			#print bigram.split('_')
			if not firstword in bigramdict:
				bigramdict[firstword] = set()
			bigramdict[firstword].add(secondword)
	transactions = [] # response
	for words in allwords:
		transaction = set() # set of words/bigrams
		n = len(words)
		i = 0
		while i < n:
			if words[i] in bigramdict and i+1 < n and words[i+1] in bigramdict[words[i]]:
				transaction.add(words[i]+'_'+words[i+1])
				i += 2
				continue
			if words[i] in stopwords or len(words[i]) == 1 or words[i].isdigit():
				i += 1
				continue
			transaction.add(words[i])
			i += 1
		transactions.append(list(transaction))
	# output
	for transaction in transactions:
		print transaction


	# Apriori (ResponseBot 5)
	# http://www.borgelt.net/pyfim.html	
	from fim import apriori, fpgrowth
	patterns = apriori(transactions,supp=-3) # +: percentage -: absolute number
	# output
	print '-------- Apriori --------'
	for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
		print pattern,support
	print 'Number of patterns:',len(patterns)

	# FP-Growth (ResponseBot 6)
	patterns = fpgrowth(transactions,supp=-3)
	# output
	print '-------- FP-Growth --------'
	for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
		print pattern,support
	print 'Number of patterns:',len(patterns)

	# Closed Non-Single Itemsets (ResponseBot 7)
	patterns = fpgrowth(transactions,target='c',supp=-2,zmin=2)
	# output
	print '-------- Closed Non-single Itemsets --------'
	for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
		print pattern,support
	print 'Number of patterns:',len(patterns)


	# One-to-Many Association Rules (ResponseBot 8)
	rules = apriori(transactions,target='r',supp=-2,conf=70,report='sc')
	# output
	print '-------- One-to-Many Association Rules --------'
	for (ruleleft,ruleright,support,confidence) in sorted(rules,key=lambda x:x[0]):
		print ruleleft,'-->',ruleright,support,confidence
	print 'Number of rules:',len(rules)








