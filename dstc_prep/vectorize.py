
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

def build_vectorizer(kind="bow", min_df=1, ngram_range=(1,1)):
    """kind='bow' -> CountVectorizer, kind='tfidf' -> TfidfVectorizer"""
    if kind == "tfidf":
        return TfidfVectorizer(min_df=min_df, ngram_range=ngram_range)
    return CountVectorizer(min_df=min_df, ngram_range=ngram_range)

def vectorize_fit_transform(vectorizer, X_train, X_test):
    """Fit on train only (to avoid leakage), transform both."""
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)
    return Xtr, Xte, vectorizer
