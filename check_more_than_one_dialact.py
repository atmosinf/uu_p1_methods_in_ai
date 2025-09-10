def look_for_multiple_dialog_acts(input_file):
    '''
    checks if a single line has more than one dialog act
    '''
    
    # possible dialog acts
    dialog_acts = ['ack', 'affirm', 'bye', 'confirm', 'deny', 'hello', 'inform',
    'negate', 'null', 'repeat', 'reqalts', 'reqmore',
    'request', 'restart', 'thankyou']

    count = 0
    print('## Sentences of more than one word, which also have more than than one dialog act assigned to it ##')
    with open(input_file, 'r') as fin:
        for i,line in enumerate(fin):
            line_stripped = line.strip()
            line_with_only_space = ' '.join(line_stripped.replace('\t',' ').split())
            words = line_with_only_space.split()

            if (words[0] == words[1]) and (words[0] in dialog_acts) and len(words) > 2:
                count += 1
                print(i+1,line)
    
    print(f'\nthere were {count} instances where the dialog act appeared twice')


def remove_duplicate_sentences(input_file, output_file):
    """
    Removes duplicate sentences from the input file, writing only the first occurrence
    of each normalized sentence to the output file.
    Normalization: strip whitespace, replace tabs with spaces, collapse multiple spaces.
    Prints the number of duplicates removed.
    """
    seen = set()
    duplicates = 0
    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        for line in fin:
            normalized = ' '.join(line.strip().replace('\t', ' ').split())
            if normalized not in seen:
                seen.add(normalized)
                fout.write(line)
            else:
                duplicates += 1
    print(f'Removed {duplicates} duplicate sentences.')

look_for_multiple_dialog_acts(input_file='dialog_acts.dat')