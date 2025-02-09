import pickle
import re
import string
import streamlit as st
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import numpy as np

def transform_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters
    text = text.translate(str.maketrans('', '', string.punctuation))  # Removing Punctuation
    tokens = word_tokenize(text)  # Tokenization
    tokens1 = [PorterStemmer().stem(word) for word in tokens if word not in stopwords.words('english')]
                                                            # Removing Stop word and Stemming

    return " ".join(tokens1)

with open('text_vectorizer.pkl', 'rb') as fh:
    vec = pickle.load(fh)

with open('final_model.pkl', 'rb') as f:
    model = pickle.load(f)


st.title('SMS SPAM CLASSIFIER')

input_sms = st.text_area('Enter the message')

# STEP 1: Text Pre-Processing
transform_sms = transform_text(input_sms)

if st.button('PREDICT'):
    # STEP 2: Text Vectorization
    v  = vec.transform([transform_sms])

    # STEP 3: Prediction
    res = model.predict(v.toarray())

    # STEP 4: DISPLAY
    if res == 1 :
        st.header('SPAM')
    else :
        st.header('NOT SPAM')


