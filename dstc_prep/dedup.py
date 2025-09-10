
import pandas as pd

def deduplicate_by_utterance(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the first time an utterance appears (drop duplicates by 'text')."""
    return df.drop_duplicates(subset=["text"], keep="first").reset_index(drop=True)
