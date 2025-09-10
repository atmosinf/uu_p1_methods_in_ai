
from sklearn.preprocessing import LabelEncoder

def encode_labels(y_train, y_test):
    """Fit label encoder on train, apply to both."""
    le = LabelEncoder()
    ytr = le.fit_transform(y_train)
    yte = le.transform(y_test)
    return ytr, yte, le
