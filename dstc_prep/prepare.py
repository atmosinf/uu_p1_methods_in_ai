
from collections import Counter
from .dataio import load_dialog_file
from .dedup import deduplicate_by_utterance
from .split import stratified_split
from .vectorize import build_vectorizer, vectorize_fit_transform
from .encode import encode_labels

def describe_split(y_train, y_test, title=""):
    c_tr = Counter(y_train)
    c_te = Counter(y_test)
    print(f"\n{title} label counts:")
    print("Train:", dict(c_tr))
    print("Test :", dict(c_te))

def prepare_dataset(path,
                    vectorizer_kind="bow",
                    min_df=1,
                    ngram_range=(1,1),
                    seed=42):
    """Prepares two variants: original and deduplicated."""
    df = load_dialog_file(path)

    # Variant A: original
    Xa_tr_text, Xa_te_text, ya_tr, ya_te = stratified_split(df, test_size=0.15, seed=seed)
    vecA = build_vectorizer(kind=vectorizer_kind, min_df=min_df, ngram_range=ngram_range)
    Xa_tr, Xa_te, vecA = vectorize_fit_transform(vecA, Xa_tr_text, Xa_te_text)
    ya_tr_enc, ya_te_enc, leA = encode_labels(ya_tr, ya_te)

    # Variant B: deduplicated
    df_dedup = deduplicate_by_utterance(df)
    Xb_tr_text, Xb_te_text, yb_tr, yb_te = stratified_split(df_dedup, test_size=0.15, seed=seed)
    vecB = build_vectorizer(kind=vectorizer_kind, min_df=min_df, ngram_range=ngram_range)
    Xb_tr, Xb_te, vecB = vectorize_fit_transform(vecB, Xb_tr_text, Xb_te_text)
    yb_tr_enc, yb_te_enc, leB = encode_labels(yb_tr, yb_te)

    print(f"Original rows: {len(df)} | Deduplicated rows: {len(df_dedup)}")
    describe_split(ya_tr, ya_te, title="Original")
    describe_split(yb_tr, yb_te, title="Deduplicated")

    return {
        "original": {
            "X_train": Xa_tr, "X_test": Xa_te,
            "y_train": ya_tr_enc, "y_test": ya_te_enc,
            "vectorizer": vecA, "label_encoder": leA,
            "train_text": Xa_tr_text, "test_text": Xa_te_text
        },
        "deduplicated": {
            "X_train": Xb_tr, "X_test": Xb_te,
            "y_train": yb_tr_enc, "y_test": yb_te_enc,
            "vectorizer": vecB, "label_encoder": leB,
            "train_text": Xb_tr_text, "test_text": Xb_te_text
        }
    }
