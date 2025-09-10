
from pathlib import Path
import pandas as pd

def load_dialog_file(path):
    """
    Reads `dialog_act utterance` lines into a DataFrame with columns: label, text.
    Skips blank/malformed lines.
    """
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                # skip malformed lines like a bare label with no text
                continue
            label, text = parts[0], parts[1]
            rows.append((label, text))
    df = pd.DataFrame(rows, columns=["label", "text"])
    return df

if __name__ == "__main__":
    df = load_dialog_file("dialog_acts.dat")
    print(df.head())
