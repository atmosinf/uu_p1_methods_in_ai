from collections import Counter
from .dataio import load_data_to_df
from .split import stratified_split
from .vectorize import vectorize_fit_transform
from .encode import encode_labels
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder

def summarize_labels(y_train, y_test):
    print('--## Dataset Summary ##--')
    train_counts = dict(sorted(Counter(y_train).items(), key=lambda x: x[1], reverse=True))
    test_counts = dict(sorted(Counter(y_test).items(), key=lambda x: x[1], reverse=True))

    print(f"Train: total={len(y_train)}, unique={len(train_counts)}, counts={train_counts}")
    print(f"Test:  total={len(y_test)}, unique={len(test_counts)}, counts={test_counts}")
    print('-----#####-----\n')

    return train_counts, test_counts

def prepare_dataset(path):
    df = load_data_to_df(path)

    # Ensure stratified split works: drop labels with <2 samples
    label_counts = df['label'].value_counts()
    insufficient = label_counts[label_counts < 2]
    if not insufficient.empty:
        df = df[df['label'].isin(label_counts[label_counts >= 2].index)].reset_index(drop=True)
        print(f"Dropped {len(insufficient)} label(s) with <2 samples: {list(insufficient.index)}")

    # split the dataset into train test
    x_train, x_test, y_train, y_test = stratified_split(df, test_size=0.15)

    # create an instance of the CountVectorizer and vectorize x_train and x_test
    vectorizer = CountVectorizer()
    x_train_transformed, x_test_transformed = vectorize_fit_transform(vectorizer, x_train, x_test)

    # encode the labels
    encoder = LabelEncoder()
    y_train_encoded, y_test_encoded = encode_labels(encoder, y_train, y_test)

    # get a summary of the train test split and the label distribution
    summarize_labels(y_train, y_test)

    return {'x_train': x_train_transformed,
            'x_test': x_test_transformed,
            'y_train': y_train_encoded,
            'y_test': y_test_encoded,
            'encoder': encoder,
            'vectorizer': vectorizer}

if __name__ == '__main__':
    prepare_dataset('datasets/dialog_acts_deduplicated.dat')
