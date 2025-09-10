def convert_file_to_lowercase(input_file, output_file=None):
    """
    Reads a text file, converts all words to lowercase, 
    and optionally writes the result to a new file.

    :param input_file: str, path to the input text file
    :param output_file: str or None, path to save the lowercase text (if None, no file is saved)
    :return: str, lowercase text content
    """
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    lower_text = text.lower()

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(lower_text)

    return lower_text

convert_file_to_lowercase(input_file='dialog_acts.dat', output_file='dialog_acts_lower.dat')