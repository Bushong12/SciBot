# SciBot
Data Science Fall 2017 project to perform data processing, cleaning, and analysis on Data Science Papers

All output files are stored in the data folder
Initial .txt files about the text are stored in the microsoft folder
Complete text is stored in the text folder
dependencies.sh installs all necessary python libraries in order to run our code

Data Integration and Cleaning:
------------------------------
    python task1.py
	
	Produces CSV with PID,PDFID,title,conf,folder,year,affil,authors,author_ids,keywords
	
	Reads from: microsoft/Authors.txt, microsoft/PaperAuthorAffiliations.txt, microsoft/PaperKeywords.txt, microsoft/index.txt, microsoft/Papers.txt
	Writes to: integrated.csv (stores the cleaned index.txt)

Keyword Extraction:
-------------------
	python keywords.py
	python task2.py
		
	Output:
	
		Collecting words from documents...
		Calculating support for each word...
		Finding Bigrams...
		Counting Bigrams...
		Finding Transactions...
		Preforming Apriori...
		Number of patterns: 34865
		
		Building non-single itemsets with FP-Growth...
		Number of patterns: 30902
		Done.

	task2.py...
	Reads from: microsoft/index.txt, text/*, microsoft/Papers.txt
	Writes to: data/phrase2count.txt (each entity candidate & its count), data/paper2attributes.txt (contains paper id and entity names found in it), data/paper2attributes2label.txt (attributes, paper id, and name of conference)

Entity Typing:
--------------
	python task3.py
	(must run task 2 before task 3 in order to generate phrase2count.txt)

	Reads from: microsoft/index.txt, text/*, data/phrase2count.txt
	Writes to: data/entitytyping.txt (classification of each entity), 

Collaboration Discovery:
------------------------
	python task4.py

	Reads from: microsoft/Authors.txt, microsoft/PaperAuthorAffiliations.txt, 
	Writes to: data/authorcollaborations.txt (Authors collaborations, support)

Problem-Method Association Mining:
----------------------------------
	python task5.py

	Reads from: microsoft/PaperKeywords.txt, microsoft/stopwords.txt, text/*, 
	Writes to: data/our_keywords.txt (keywords we found using the ResponseBot functions), data/keyword_bigrams.txt (bigrams from our keywords), data/keyword_counts.txt (contains results of non-single itemsets), data/onetomany.txt (contains one-to-many association rules)


Problem/Method/Author-to-Conference Association:
------------------------------------------------
	python task6.py
	** task 2 must be run before this task in order to create necessary files **

	Reads from: data/paper2attributes2label.txt, 
	Writes to: data/bestattributes.txt (top entitites)

Paper Clustering:
-----------------
	python task7.py

	Reads from: text/*
	Writes to:

Data Visualization:
-------------------
	python word_cloud_viz.py

	Reads from: data/entitytyping.txt
	Writes to: wordcloud.png
