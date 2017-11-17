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
	stopwords = set()

	# create set of entity candidates
	for key in paper_keywords:
		for word in paper_keywords[key]:
			entity_candidates[word] = 0

	#create set of stopwords
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

	# scan the words in all files to get counts for entity words
	for doc in all_files:
		for line in open(doc):
			temp = tokenizer(line.rstrip())
			for word in temp:
				if word in stopwords or len(word) == 1 or word.isdigit(): continue
				if not word in entity_candidates:
					entity_candidates[word] = 0
				entity_candidates[word] += 1
	print(entity_candidates)


