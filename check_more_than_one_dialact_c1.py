def clean_dataset(filepath, output_path, valid_labels):
    """
    Read `filepath`, ensure only the FIRST dialog-act label is kept at line start,
    write cleaned lines to `output_path`. Returns a summary dict.
    """
    valid_labels = {lbl.lower() for lbl in valid_labels}

    cleaned_multi = 0     # lines with >1 leading labels
    skipped_no_label = 0  # lines that didn't start with a valid label
    total = 0

    with open(filepath, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        for lineno, raw in enumerate(fin, 1):
            total += 1
            line = raw.strip()
            if not line:
                # skip empty lines silently
                continue

            # Normalize tabs → spaces, collapse multiple spaces
            line = " ".join(line.replace("\t", " ").split())
            tokens = line.split()

            # Collect consecutive labels from the start (case-insensitive)
            i = 0
            labels_found = []
            while i < len(tokens) and tokens[i].lower() in valid_labels:
                labels_found.append(tokens[i].lower())
                i += 1

            if not labels_found:
                # No valid starting label → log & skip (or write unchanged if you prefer)
                skipped_no_label += 1
                # print(f"[WARN] Line {lineno}: no starting label → {line}")
                continue

            if len(labels_found) > 1:
                cleaned_multi += 1

            label = labels_found[0]
            utterance = " ".join(tokens[i:])  # may be empty if no utterance tokens

            # Write cleaned line (label + single space + utterance if present)
            if utterance:
                fout.write(f"{label} {utterance}\n")
            else:
                # still write the label so you can catch these later
                fout.write(f"{label}\n")

    return {
        "total_lines_read": total,
        "cleaned_multiple_labels": cleaned_multi,
        "skipped_no_label": skipped_no_label,
        "written_lines": total - skipped_no_label  # minus blank+no-label lines
    }


# Example usage
VALID_LABELS = {
    "ack","affirm","bye","confirm","deny","hello","inform",
    "negate","null","repeat","reqalts","reqmore","request",
    "restart","thankyou"
}

summary = clean_dataset("dialog_acts.dat", "dialog_acts_cleaned.dat", VALID_LABELS)
print(summary)