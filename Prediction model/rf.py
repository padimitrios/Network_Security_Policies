import numpy as np 
import pandas as pd

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

message=pd.read_csv('spam.csv',encoding='ISO-8859-1')

message=message[['v1','v2']]
message.columns=['label','message']

ps = PorterStemmer()
corpus = []
for i in range(0, len(message)):
    review = re.sub('[^a-zA-Z]', ' ', message['message'][i])
    review = review.lower()
    review = review.split()
    
    review = [ps.stem(word) for word in review if not word in stopwords.words('english')]
    review = ' '.join(review)
    corpus.append(review)

#print(message.head())
#print(corpus)

# Creating the Bag of Words model
from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer(max_features=4000)
X = cv.fit_transform(corpus).toarray()

y=pd.get_dummies(message['label'])
y=y.iloc[:,1].values

import matplotlib.pyplot as plt
message['label'].value_counts().plot(kind='bar')

#print(X,y)

#train test split
from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.20,random_state=42)

from sklearn.ensemble import RandomForestClassifier

model=RandomForestClassifier()
model.fit(X_train,y_train)
pred=model.predict(X_test)

from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
print(confusion_matrix(y_test,pred))

print(accuracy_score(y_test,pred))

import joblib
joblib.dump(model, 'model.pkl')

import pickle

# Save the corpus list
with open('corpus.pkl', 'wb') as f:
    pickle.dump(corpus, f)

