import os

# initialize set of keywords
keywords = set()

for line in open('microsoft/PaperKeywords.txt'):
	data = line.split('\t')
	keyword = data[1].rstrip()
	keywords.add(keyword)
	
print(len(keywords))

file_list = list()
for root, dirs, files in os.walk("text"):
	for subdir in dirs:
		dir_path = os.path.join(root, subdir)
		#print(file_path)
		for sub_root, sub_dirs, sub_files in os.walk(dir_path):
			for file_name in sub_files:
				file_path = os.path.join(dir_path, file_name)
				print(file_path)
				file_list.append(file_path)