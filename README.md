# SciBot
Data Science Fall 2017 project to perform data processing, cleaning, and analysis on Data Science Papers

Data Integration and Cleaning:
------------------------------
    python integrate.py
	
	Produces CSV with PID,PDFID,title,conf,folder,year,affil,authors,author_ids,keywords
	
	We end up with 5854 papers, stored in microsoft/integrated.csv.

Keyword Extraction:
-------------------
	python keywords.py
	
	We extracted keywords by doing frequent pattern mining:
		-	First we tokenized all the papers by separating any punctuation and splitting the text up by spaces.
		-	Next we cleaned the data further by removing any sets that had strange characters, numbers, or other symbols
		-	To generate the frequent itemsets we used both Apriori and FP-Growth with a minimum support of 1000
		
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