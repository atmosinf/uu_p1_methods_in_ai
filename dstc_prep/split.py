
from sklearn.model_selection import train_test_split

def stratified_split(df, test_size=0.15, seed=42):
    """Stratified split so label proportions are preserved."""
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"].tolist(),
        df["label"].tolist(),
        test_size=test_size,
        random_state=seed,
        stratify=df["label"]
    )
    return X_train, X_test, y_train, y_test
