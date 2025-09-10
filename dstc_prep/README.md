
# dstc_prep

Small, debuggable module to prepare the DSTC-style dialog act dataset.

## Files
- `dataio.py`: load `dialog_act utterance` file into a DataFrame
- `dedup.py`: drop duplicate utterances (keep first occurrence)
- `split.py`: stratified 85/15 split
- `vectorize.py`: CountVectorizer/TF-IDF + fit/transform
- `encode.py`: label encoding for targets
- `prepare.py`: glue that returns both original and deduplicated variants
- `__init__.py`: convenient re-exports

## Example
```python
from dstc_prep import prepare_dataset

data = prepare_dataset("dialog_acts.dat", vectorizer_kind="bow", ngram_range=(1,1))
X_tr = data["original"]["X_train"]
y_tr = data["original"]["y_train"]
```

Replace the path with your dataset file.
