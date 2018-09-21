import spacy
import pickle

nlp = spacy.load('en_core_web_sm')

class CommentCleaner(object):
    '''
        A class for cleaning up comments. 

    Input: 
        comments (list): A list of comments.
    '''
    def __init__(self, comments):
        self.comments = comments    
        self.make_sentences_and_nlp()
        self.tokenizeText()
        self.vectorize()

    def make_sentences_and_nlp(self):
        self.all_reviews = {}
        for i, review in enumerate(self.comments):
            review = review.encode('utf-8').replace(b'\xe2\x80\x99', b"'").decode('utf-8')
            self.all_reviews[i] = [sent for sent in nlp(review).sents]

    def vectorize(self, vect_filename='app/models/Count_vectorizer_chicken'):
        count_vectorizer = pickle.load(open(vect_filename, 'rb'))
        self.all_vectorized_reviews = {}
        for key, val in self.all_tokenized_reviews.items():
            self.all_vectorized_reviews[key] = count_vectorizer.transform([' '.join(x) for x in val])

    def cleanText(self, text):
        text = text.strip().replace("\n", " ").replace("\r", " ")
        text = text.replace("-", "").replace(":", "").replace("(", "").replace(")", "")
        text = text.lower()
        return text

    def _tokenizeText(self, sample):
        tokens = []
        for tok in sample:
            if tok.pos_ == "SPACE":
                continue
            if tok.lemma_ != "-PRON-":
                tokens.append(self.cleanText(tok.lemma_))
            else:
                tokens.append(tok.lower_)
        return tokens
    
    def tokenizeText(self):
        self.all_tokenized_reviews = {}
        for k, v in self.all_reviews.items():
            token_list = []
            for sentence in v:
                token_list.append(self._tokenizeText(sentence))
                while '' in token_list[-1]:
                    token_list[-1].remove('')
                if len(token_list[-1]) == 0:
                    token_list.pop()
            self.all_tokenized_reviews[k] = token_list

