from integrate import Paper
import os
import sys
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

#################### TASK 7: PAPER CLUSTERING ####################
# Sample pipeline for text feature extraction and evaluation
# http://scikit-learn.org/stable/auto_examples/model_selection/grid_search_text_feature_extraction.html#sphx-glr-auto-examples-model-selection-grid-search-text-feature-extraction-py

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
					if num_test < 10:
						test_files.append(file_path)
						num_test += 1
	if test:
		return test_files
	#print("Collected {} files".format(str(len(file_list))))
	return file_list

if __name__ == '__main__':
	allfiles = build_file_list()
	for paper in allfiles:
		# extract features from text
		# http://scikit-learn.org/stable/modules/classes.html#module-sklearn.feature_extraction
		
		# do k-means
		# http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
	