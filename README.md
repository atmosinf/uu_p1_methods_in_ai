# uu_p1_methods_in_ai

Project for dialog act classification with simple data prep utilities and a training CLI.

## Quick Start
- Default (logistic regression): `python train.py`
- Select model: `python train.py --model decision_tree`
- Select dataset: `python train.py --data datasets/dialog_acts_lower.dat`

## Top-Level Files
- `train.py`: CLI to train a classifier on the dataset. Supports `--model {logistic_regression,decision_tree}` and `--data <path>`. Prints accuracy, classification report, and confusion matrix.
- `datasets/`: Folder containing dataset files:
  - `dialog_acts.dat`: Original dataset (label + utterance per line).
  - `dialog_acts_lower.dat`: Lowercased version of the dataset.
  - `dialog_acts_deduplicated.dat`: Deduplicated dataset (removed duplicate utterances).

## Data Prep Module (`preprocess_dataset/`)
- `__init__.py`: Re-exports helpers for convenient import.
- `dataio.py`: Loads a space-separated `label utterance` file into a pandas DataFrame with columns `label` and `text`.
- `split.py`: Creates a stratified train/test split (default 85/15) using scikit-learn.
- `vectorize.py`: Fits a `CountVectorizer` on train text and transforms train/test.
- `encode.py`: Encodes labels using `LabelEncoder` (fit on train, transform train/test).
- `prepare.py`: Orchestrates loading, filtering labels with <2 samples, splitting, vectorizing, encoding, and prints a brief dataset summary.

## Utility Scripts (`utils/`)
- `convert_data_to_lowercase.py`: Lowercases labels and utterances in a dataset file.
- `remove_duplicates.py`: Removes duplicate lines (keeps first occurrence).
- `get_label_dist.py`: Prints label distribution statistics.
- `check_more_than_one_dialog_act.py`: Checks for lines containing more than one dialog act token.

## Notes
- The training pipeline drops labels with fewer than 2 samples to keep stratified splitting valid.
- For multiclass text data, `solver='saga'` is used with LogisticRegression and `class_weight='balanced'` to handle imbalance.
