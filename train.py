from preprocess_dataset import prepare_dataset
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd
import argparse


def main():
    parser = argparse.ArgumentParser(description="Train a model on dialog acts")
    parser.add_argument(
        "-m",
        "--model",
        default="logistic_regression",
        choices=["logistic_regression", "decision_tree"],
        help="Model to train (default: logistic_regression)",
    )
    parser.add_argument(
        "-d",
        "--data",
        default="datasets/dialog_acts_deduplicated.dat",
        help="Path to dataset file (default: datasets/dialog_acts_deduplicated.dat)",
    )
    args = parser.parse_args()

    # preprocess dataset and get train/test splits. split is done in a stratified manner
    data = prepare_dataset(args.data)
    x_train, x_test, y_train, y_test = data['x_train'], data['x_test'], data['y_train'], data['y_test']
    label_encoder = data['encoder']

    # choose model
    if args.model == "logistic_regression":
        classifier = LogisticRegression(max_iter=1000, solver='saga', class_weight='balanced', C=1.0)
    else:  # decision_tree
        classifier = DecisionTreeClassifier(criterion='gini', class_weight='balanced', random_state=0)

    # fit the model to the training data
    classifier.fit(x_train, y_train)

    # evaluate on the test data
    pred = classifier.predict(x_test)
    print("\nAccuracy:", accuracy_score(y_test, pred), '\n')
    print("Classification Report:\n", classification_report(y_test, pred, target_names=label_encoder.classes_))
    # format and print confusion matrix with class labels
    cm = confusion_matrix(y_test, pred)
    labels = list(label_encoder.classes_)
    df_cm = pd.DataFrame(cm, index=labels, columns=labels)
    print("Confusion Matrix (counts)")
    with pd.option_context('display.max_columns', None, 'display.width', 200):
        print(df_cm.to_string())

if __name__ == "__main__":
    main()
