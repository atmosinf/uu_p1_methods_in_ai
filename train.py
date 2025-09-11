from dstc_prep import prepare_dataset
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# preprocess dataset and get train/test splits. split is done in a stratified manner
data = prepare_dataset('dialog_acts_deduplicated.dat')
x_train, x_test, y_train, y_test = data['x_train'], data['x_test'], data['y_train'], data['y_test']
label_encoder = data['encoder']

# train a logistic regression model
classifier = LogisticRegression(max_iter=1000, solver='liblinear', class_weight='balanced', C=1.0)

# fit the model to the training data
classifier.fit(x_train, y_train)

# evaluate on the test data
pred = classifier.predict(x_test)
print("Accuracy:", accuracy_score(y_test, pred))
print(classification_report(y_test, pred, target_names=label_encoder.classes_))
print(confusion_matrix(y_test, pred))
