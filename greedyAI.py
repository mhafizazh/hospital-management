import pickle
import re
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


def machineLearning(text: str):
    test_text = [text]
    with open('mlModel/greedAI1.pkl', 'rb') as file:
        model = pickle.load(file)
    with open('mlModel/count_vectorizer.pkl', 'rb') as file:
        loaded_cv = pickle.load(file)
    # test_text = ["I am Hafiz I got heart attack I live in Indonesia"]
    corpus2 = []
    for i in range(0, len(test_text)):
        message = re.sub('[^a-zA-Z]', ' ', test_text[i])
        message = message.lower()
        message = message.split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        all_stopwords.remove('not')
        message = [ps.stem(word) for word in message if not word in set(all_stopwords)]
        message = ' '.join(message)
        corpus2.append(message)
    new_data_transformed = loaded_cv.transform(corpus2).toarray()
    # Make predictions
    prediction = model.predict(new_data_transformed)

    # Output the prediction
    return prediction


print(machineLearning("I feel tired today"))
