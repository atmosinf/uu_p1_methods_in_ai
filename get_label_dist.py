from collections import Counter
import matplotlib.pyplot as plt

def plot_dialog_act_counts(dat_path, save_path=None, title="Dialog act frequency"):
    """
    Reads a `dialog_act utterance` .dat file, counts label frequencies,
    and shows (or saves) a bar chart.

    Parameters
    ----------
    dat_path : str or Path
        Path to the .dat file (format: 'label<space>utterance').
    save_path : str or Path, optional
        If given, saves the plot to this path instead of just showing it.
    title : str
        Title for the chart.

    Returns
    -------
    counts : dict
        {label: count} dictionary sorted by descending count.
    """
    counts = Counter()
    total_lines = 0
    skipped = 0

    with open(dat_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            total_lines += 1
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                skipped += 1
                continue  # malformed line (no utterance)
            label = parts[0]
            counts[label] += 1

    # Sort by count (desc), then label (asc) for stable display
    items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    labels = [k for k, _ in items]
    values = [v for _, v in items]

    # ---- Plot ----
    plt.figure(figsize=(10, 5))
    plt.bar(labels, values)
    plt.title(title)
    plt.xlabel("Dialog act")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches="tight")
    else:
        plt.show()

    # Console summary
    print(f"Total non-empty lines read : {total_lines}")
    print(f"Malformed/label-only lines : {skipped}")
    print("Counts:", dict(items))

    return dict(items)

plot_dialog_act_counts('dialog_acts_deduplicated.dat')