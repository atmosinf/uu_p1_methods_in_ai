def remove_duplicate_lines(input_file: str, output_file: str):
    """
    Removes duplicate utterances from a dialog act dataset.
    Keeps only the first occurrence of each utterance.
    
    Parameters:
        input_file (str): Path to the input .dat file
        output_file (str): Path to save the deduplicated file
    """
    seen = set()
    deduped_lines = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Split dialog act and utterance
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue  # skip malformed lines
            act, utterance = parts[0], parts[1]

            # Only check duplicate utterances
            if utterance not in seen:
                seen.add(utterance)
                deduped_lines.append(f"{act} {utterance}")

    with open(output_file, "w", encoding="utf-8") as f:
        for line in deduped_lines:
            f.write(line + "\n")

    print(f"Deduplicated file written to {output_file} with {len(deduped_lines)} lines.")

remove_duplicate_lines(input_file='dialog_acts_lower.dat', output_file='dialog_acts_lower_cleaned.dat')