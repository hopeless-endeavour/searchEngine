import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import text
from collections import Counter
import pandas as pd

data = pd.read_pickle('dtm.pkl')
data_clean = pd.read_pickle('data_clean.pkl')
data = data.transpose()
# print(data.head())


top_dict = {}
for c in data.columns:
    top = data[c].sort_values(ascending=False).head(30)
    top_dict[c] = list(zip(top.index, top.values))

# print(top_dict)


for name, top_words in top_dict.items():
    print(name)
    print(', '.join([word for word, count in top_words[0:14]]))
    print('---')


# Let's first pull out the top 30 words for each comedian
words = []
for name in data.columns:
    top = [word for (word, count) in top_dict[name]]
    for t in top:
        words.append(t)

# print(words)


Counter(words).most_common()
stop_words = [word for word, count in Counter(
    words).most_common() if count > 3]

# Recreate document-term matrix
cv = CountVectorizer(stop_words=stop_words)
data_cv = cv.fit_transform(data_clean.transcript)
data_stop = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names())
data_stop.index = data_clean.index

# Pickle it for later use
pickle.dump(cv, open("cv_stop.pkl", "wb"))
data_stop.to_pickle("dtm_stop.pkl")


wc = WordCloud(stopwords=stop_words, background_color="white", colormap="Dark2",
               max_font_size=150, random_state=42)


plt.rcParams['figure.figsize'] = [16, 6]

names = ['bird-and-whale', 'chick-little', 'goldilocks', 'threepigs',
         'petitchaperonrouge', 'uglyduckling']

# Create subplots for each comedian
# for index, name in enumerate(data.columns):
#     wc.generate(data_clean.transcript[name])
#
#     plt.subplot(3, 4, index+1)
#     plt.imshow(wc, interpolation="bilinear")
#     plt.axis("off")
#     plt.title(names[index])
#
# plt.show()

unique_list = []
for name in data.columns:
    uniques = data[name].to_numpy().nonzero()[0].size
    unique_list.append(uniques)

# Create a new dataframe that contains this unique word count
data_words = pd.DataFrame(list(zip(names, unique_list)), columns=[
                          'names', 'unique_words'])
data_unique_sort = data_words.sort_values(by='unique_words')
print(data_unique_sort)
