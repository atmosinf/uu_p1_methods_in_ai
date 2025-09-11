
def vectorize_fit_transform(vectorizer, x_train, x_test):
    '''
    fit vectorizer on train and transform both 
    '''
    x_train_transformed = vectorizer.fit_transform(x_train)
    x_test_transformed = vectorizer.transform(x_test)

    return x_train_transformed, x_test_transformed

if __name__ == '__main__':
    from dataio import load_data_to_df
    from split import stratified_split
    from sklearn.feature_extraction.text import CountVectorizer

    df = load_data_to_df('test_data.txt')
    x_train, x_test, y_train, y_test = stratified_split(df, test_size=0.15)
    vectorizer = CountVectorizer()
    x_train_transformed, x_test_transformed = vectorize_fit_transform(vectorizer, x_train, x_test)
    
