import sys
import os

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
	
def tokenizer(text):
	# based on example code given in the ResponseBot Demo
	# this processes text into a form that is simpler to analyze
	ret = []
	for x in [',','.','--','!','?',';','(',')','/','"']:
		text = text.replace(x,' '+x+' ')
	for word in text.split(' '):
		if word == '': continue
		ret.append(word.lower())
	return ret

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
	
	return True
if __name__ == '__main__':
	# csv for PID,PDFID,title,conf,folder,year,affil,authors,author_ids,keywords
	integrated_data = open('data/integrated.csv', 'w+')
	
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
	for line in open('microsoft/stopwords.txt'):
		word = line.strip('\r\n').lower()
		stopwords.add(word)
	
	# CSV header
	integrated_data.write("PID,PDFID,title,conf,folder,year,affil,authors,author_ids,keywords\n")
	
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

		
	################################## MOVE TO NEW FILE ######################################
	# file for storing all the keywords that we generate
	new_keywords = open('data/our_keywords.txt', 'w+')
	# file for keyword bigrams
	bigram_file = open('data/keyword_bigrams.txt', 'w+')
	# file for storing bigram transactions
	transaction_file = open('data/keyword_transactions.txt', 'w+')
	# file for result of Apriori
	apriori_file = open('data/keyword_apriori.txt', 'w+')
	# file for result of non-singe itemsets
	nonsingle_file = open('data/keyword_counts.txt', 'w+')
	
	all_files = list()
	# walk through all directories
	print("Collecting words from documents...")
	file_list = list()
	test_files = list()
	num_test = 0
	for root, dirs, files in os.walk("text"):
		for subdir in dirs:
			dir_path = os.path.join(root, subdir)
			#print(file_path)
			for sub_root, sub_dirs, sub_files in os.walk(dir_path):
				for file_name in sub_files:
					file_path = os.path.join(dir_path, file_name)
					#print(file_path)
					file_list.append(file_path)
					if num_test < 10:
						test_files.append(file_path)
						num_test += 1

	# create list of lists of all important words in the documents (ResponseBot 1)
	for doc in file_list:
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
	print("Calculating support for each word...")
	#sys.stdout.write("Calculating support for each word.")
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
		new_keywords.write('{} {}\n'.format(word, support))
		#sys.stdout.write('.')
	#print('\n')
	print("Found {} entity candidates".format(str(len(word2support))))
	# Find bigram for each entity candidate (ResponseBot 3)
	word2count = {}
	print("Finding Bigrams...")
	for words in allwords:
		for word in words:
			if word in stopwords or len(word) == 1 or word.isdigit(): continue
			if not word.isalnum(): continue
			if not word in word2count:
				word2count[word] = 0
			word2count[word] += 1
	bigram2score = {} # bigram's count, first word's count, second word's count, significance score
	L = 0
	print("Counting Bigrams...")
	#sys.stdout.write("Counting Bigrams.")
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
	bigram_file.write('bigram,count-bigram,count-first-word,count-second-word,significance-score\n')
	for [bigram,score] in sorted(bigram2score.items(),key=lambda x:-x[1][3]):
		bigram_file.write('{} {} {} {} {}\n'.format(bigram, score[0], score[1], score[2], score[3]))
		#sys.stdout.write('.')
	print("Found {} bigrams".format(str(len(bigram2score))))

	# find transactions for bigrams (ResponseBot 4)
	print("Finding Transactions...")
	#sys.stdout.write("Finding Transactions")
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
	print("Found {} transactions".format(str(len(transactions))))
	# output
	for transaction in transactions:
		if not transaction: continue
		t = ','.join(transaction)
		if check_string_guality(t) is False: continue
		t = t.replace('#', '')
		t = t.replace('*', '')
		transaction_file.write('{}\n'.format(t))
		#sys.stdout.write('.')

	print("Preforming Apriori...")
	# Apriori (ResponseBot 5)
	# http://www.borgelt.net/pyfim.html	
	from fim import apriori, fpgrowth
	patterns = apriori(transactions,supp=-1000) # +: percentage -: absolute number
	#print(type(patterns)) -> patterns is a list
	# output
	for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
		#print(type(pattern)) -> pattern is a tuple
		if len(set(pattern)) <= 1: continue
		p = ','.join(pattern)
		apriori_file.write('{} {} \n'.format(p, str(support)))
	apriori_file.write('Number of patterns: {}\n'.format(len(patterns)))
	print('Number of patterns: {}\n'.format(len(patterns)))

	#FP-Growth (ResponseBot 6)
	# patterns = fpgrowth(transactions,supp=-3)
	#output
	# fp_file.write('-------- FP-Growth --------\n')
	# for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
		# fp_file.write('{} {}\n'.format(pattern, support)
	# fp_file.write('Number of patterns: {}'.format(len(patterns)))

	#Closed Non-Single Itemsets (ResponseBot 7)
	print("Building non-single itemsets with FP-Growth...")
	patterns = fpgrowth(transactions,target='c',supp=-1000,zmin=2)
	#output
	for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
		p = ','.join(pattern)
		nonsingle_file.write('{} {} \n'.format(p, str(support)))
	print 'Number of patterns:',len(patterns)


	#One-to-Many Association Rules (ResponseBot 8)
	# rules = apriori(transactions,target='r',supp=-2,conf=70,report='sc')
	#output
	# print '-------- One-to-Many Association Rules --------'
	# for (ruleleft,ruleright,support,confidence) in sorted(rules,key=lambda x:x[0]):
		# print ruleleft,'-->',ruleright,support,confidence
	# print 'Number of rules:',len(rules)
	
	print("Done.")