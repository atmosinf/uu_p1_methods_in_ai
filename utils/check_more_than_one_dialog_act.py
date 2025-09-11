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
