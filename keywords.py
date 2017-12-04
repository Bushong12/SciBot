import os
import sys
from fim import apriori, fpgrowth

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

def init_sets_from_file():
	# initialize set of keywords and stop words
	keywords = set()
	stopwords = set()
	for line in open('microsoft/PaperKeywords.txt'):
		data = line.split('\t')
		keyword = data[1].rstrip()
		keywords.add(keyword)
		
	for line in open('microsoft/stopwords.txt'):
		word = line.strip('\r\n').lower()
		stopwords.add(word)
	
	return ((keywords, stopwords))

def build_file_list():
	#test = False
	print("Collecting files...")
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
	#if test:
		#return test_files
	print("Collected {} files".format(str(len(file_list))))
	return file_list

def calc_support(allwords):
	# find the support for each entity candidate
	word2support = {}
	print("Calculating support for each word...")
	for words in allwords:
		for word in set(words):
			if word in stopwords or len(word) == 1 or word.isdigit(): continue
			if not word.isalnum(): continue
			if not word in word2support:
				word2support[word] = 0
			word2support[word] += 1
	# output
	#for [word,support] in sorted(word2support.items(),key=lambda x:-x[1]):
	#	if support == 1: break
	#	output_file.write('{} {}\n'.format(word, support))
	print("Found {} entity candidates".format(str(len(word2support))))
	return word2support

def make_bigrams(allwords):
	# Find bigram for each entity candidate
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
	#bigram_file.write('bigram,count-bigram,count-first-word,count-second-word,significance-score\n')
	#for [bigram,score] in sorted(bigram2score.items(),key=lambda x:-x[1][3]):
	#	bigram_file.write('{} {} {} {} {}\n'.format(bigram, score[0], score[1], score[2], score[3]))
	print("Found {} bigrams".format(str(len(bigram2score))))
	return bigram2score

def make_transactions(bigram2score):
	# find transactions for bigrams
	print("Finding Transactions...")
	bigramdict = {}
	for bigram in bigram2score:
		if bigram2score[bigram][0] > 1:
			[firstword,secondword] = bigram.split('_')
			#firstword = bigram.split('_')[0]
			#secondword = bigram.split('_')[0]
			#print bigram.split('_')
			if not firstword in bigramdict:
				bigramdict[firstword] = set()
			bigramdict[firstword].add(secondword)
	transactions = [] 
	ret = []
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
	return transactions
	# output
	for transaction in transactions:
		if not transaction: continue
		t = ','.join(transaction)
		if check_string_guality(t) is False: continue
		t = t.replace('#', '')
		t = t.replace('*', '')
		ret.append(transaction)
		#transaction_file.write('{}\n'.format(t))
	
	return transactions

def do_apriori(transactions, output_file):
	print("Preforming Apriori...")
	# http://www.borgelt.net/pyfim.html	
	patterns = apriori(transactions,supp=-1000) # +: percentage -: absolute number
	for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
		#pattern is a tuple
		if len(set(pattern)) <= 1: continue
		p = ','.join(pattern)
		output_file.write('{} {} \n'.format(p, str(support)))
	print('Number of patterns: {}'.format(len(patterns)))

def get_nonsingle_itemsets(transactions, output_file):
	#Closed Non-Single Itemsets (ResponseBot 7)
	print("Building non-single itemsets with FP-Growth...")
	patterns = fpgrowth(transactions,target='c',supp=-1000,zmin=2)
	#output
	for (pattern,support) in sorted(patterns,key=lambda x:-x[1]):
		p = ','.join(pattern)
		output_file.write('{} {} \n'.format(p, str(support)))
	print 'Number of patterns:',len(patterns)
	
#--------------- Global Variables ---------------#		
# initialize given set of keywords and stopwords
keywords, stopwords = init_sets_from_file()


if __name__ == '__main__':
	#--------------- Create Data Files ---------------#
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
	
	# get list of paper files
	all_files = build_file_list()
	
	# create list of lists of all important words in the documents
	print("Collecting words from documents...")
	allwords = list()
	for doc in all_files:
		for line in open(doc):
			words = tokenizer(line.rstrip())
			allwords.append(words)
	
	word_support = calc_support(allwords)
	bigrams = make_bigrams(allwords)
	transactions = make_transactions(bigrams)
	do_apriori(transactions, apriori_file)
	get_nonsingle_itemsets(transactions, new_keywords)