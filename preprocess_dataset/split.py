from sklearn.model_selection import train_test_split

def stratified_split(df, test_size=0.15, seed=42):
    '''
    split the dataset in a stratified manner so that train and test sets have the same proportions of labels
    '''

    x_train, x_test, y_train, y_test = train_test_split(df['text'].tolist(), df['label'].tolist(), 
                                                        test_size=test_size, random_state=seed, stratify=df['label'])

    return x_train, x_test, y_train, y_test

if __name__ == '__main__':
    from dataio import load_data_to_df

    df = load_data_to_df("datasets/dialog_acts.dat")
    stratified_split(df, test_size=0.15)
