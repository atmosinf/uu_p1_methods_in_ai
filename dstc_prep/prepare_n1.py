from collections import Counter
from dataio_n1 import load_data_to_df
from split_n1 import stratified_split
from vectorize_n1 import vectorize_fit_transform
from encode_n1 import encode_labels
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder

from collections import Counter

from collections import Counter

def summarize_labels(y_train, y_test):
    print('--## Dataset Summary ##--')
    train_counts = dict(sorted(Counter(y_train).items(), key=lambda x: x[1], reverse=True))
    test_counts = dict(sorted(Counter(y_test).items(), key=lambda x: x[1], reverse=True))

    print(f"Train: total={len(y_train)}, unique={len(train_counts)}, counts={train_counts}")
    print(f"Test:  total={len(y_test)}, unique={len(test_counts)}, counts={test_counts}")

    return train_counts, test_counts

def prepare_dataset(path):
    df = load_data_to_df(path)

    # split the dataset into train test
    x_train, x_test, y_train, y_test = stratified_split(df, test_size=0.15)

    # create an instance of the CountVectorizer, and vectorize x_train and x_test
    vectorizer = CountVectorizer()
    x_train_transformed, x_test_transformed = vectorize_fit_transform(vectorizer, x_train, x_test)

    # encode the labels
    encoder = LabelEncoder()
    y_train_encoded, y_test_encoded = encode_labels(encoder, y_train, y_test)

    # get a summary of the train test split and the label distribution
    summarize_labels(y_train, y_test)

    

if __name__ == '__main__':
    prepare_dataset('dialog_acts_lower.dat')

    print('a')


