from wordcloud import WordCloud
import os
import matplotlib.pyplot as plt

# get counts of entities
num_words = 0
max_words = 20
word_count = dict()
for line in open('data/entitytyping.txt'):
	data = line.split('\t')
	word = data[0]
	try:
		count = int(data[1])
	except ValueError as e:
		continue
	word_count[word] = count
	if num_words < max_words:
		num_words += 1
	else:
		break

# generate text
text = ''
for word in word_count:
	for i in range(word_count[word]):
		text += ' {}'.format(word)
	
wc = WordCloud().generate(text)

plt.imshow(wc, interpolation='bilinear')
plt.axis("off")

plt.show()
plt.savefig('wordcloud.png')