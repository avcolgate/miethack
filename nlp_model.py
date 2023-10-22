from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import string
import nltk
from nltk.corpus import stopwords
import joblib


def tokenize(x):
    return PredictModel.tokenize_sentence(x, remove_stop_words=True)

class PredictModel:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

    snowball = SnowballStemmer(language="russian")
    russian_stop_words = stopwords.words("russian")
    @classmethod
    def get_snowball(cls):
        return cls.snowball

    @classmethod
    def get_stopwords(cls):
        return cls.russian_stop_words

    @classmethod
    def tokenize_sentence(cls, sentence: str, remove_stop_words: bool = True):
        tokens = word_tokenize(sentence, language="russian")
        tokens = [i for i in tokens if i not in string.punctuation]
        if remove_stop_words:
            tokens = [i for i in tokens if i not in cls.get_stopwords()]
        tokens = [cls.get_snowball().stem(i) for i in tokens]
        return tokens


    @staticmethod
    def get_predict(text):
        loaded = joblib.load('model_nlp_persited.joblib')
        return int(loaded['model'].predict([text])[0])


