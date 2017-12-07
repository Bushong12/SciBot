from integrate import Paper
import os
import sys
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics

from sklearn.cluster import KMeans, MiniBatchKMeans

#################### TASK 7: PAPER CLUSTERING ####################

#eventually change to read in a file that has list of good entities
# entities = ['artificial intelligence', 
			# 'data mining', 
			# 'machine learning', 
			# 'search engine', 
			# 'semantic web', 
			# 'world wide web', 
			# 'social networks', 
			# 'information retrieval',
			# 'support vector machines',
			# 'decision trees',
			# 'matrix factorization',
			# 'anomaly detection',
			# 'nearest neighbor',
			# 'log likelihood',
			# 'euclidean distance',
			# 'cosine similarity']
entities = ['kdd', 'icdm', 'www', 'wsdm']

def build_file_list():
	test = False
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
					if num_test < 20:
						test_files.append(file_path)
						num_test += 1
	if test:
		return test_files
	#print("Collected {} files".format(str(len(file_list))))
	return file_list

def file_to_entities(filepath):
	# scan through paper and add entities as they appear to a set
	words = set()
	for line in open(filepath):
		for entity in entities:
			line = line.lower().rstrip()
			if entity in line:
				words.add(entity)
	return words

def vectorize(filepath):
	# vector representation of paper where each entry is either a 1 or 0 for if the entity is present in the paper or not
	# get set of entities in that file
	words = file_to_entities(filepath)
	#print(words)
	# determine if each entity is in the paper
	paper_vector = []
	for i, entity in enumerate(entities):
		if entity in words:
			paper_vector.append(1)
		else:
			paper_vector.append(0)
	return paper_vector

if __name__ == '__main__':
	dataset = build_file_list()
	data = list()
	for file in dataset:
		for line in open(file):
			data.append(line)
	vector_list = []
	for paper in dataset:
		# extract features from text via vector encoding of entities
		paper_vec = vectorize(paper)
		vector_list.append(paper_vec)
	# print(vector_list)
	
	vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,
								 min_df=2, stop_words='english',
								 use_idf=False)
	# fit transform expects a list of strings
	X = vectorizer.fit_transform(data)
	print("n_samples: %d, n_features: %d" % X.shape)
	print('')
	
	# Do the actual clustering
	true_k=4
	km = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1,
				verbose=True)
	print("Clustering sparse data with %s" % km)
	km.fit(X)
	
	print("Top terms per cluster:")
	order_centroids = km.cluster_centers_.argsort()[:, ::-1]
	terms = vectorizer.get_feature_names()
	for i in range(true_k):
		sys.stdout.write("Cluster {}: ".format(i))
		for ind in order_centroids[i, :15]:
			try:
				sys.stdout.write('{} '.format(terms[ind]))
			except UnicodeEncodeError as e:
				continue
		print('')
	
	print(' ')
	print('KMeans with vector encoding:')
	Y = np.array(vector_list)
	kmeans = KMeans(n_clusters=true_k, random_state=0).fit(Y)
	print(kmeans.labels_)
	
	# solutions:
		# vector encoding of entities- represent document as vector of encodings where 1 means it is present and 0 for not
		# what are the entities?  (various keywords?)
		# this makes it difficult to find distance- dont use Eucliedean, maybe hamming