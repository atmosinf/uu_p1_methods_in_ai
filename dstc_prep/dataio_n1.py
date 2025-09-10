from pathlib import Path
import pandas as pd

def load_data_to_df(path):
    '''
    reads the file with lines in the format 'dialog_act utterance'
    returns a dataframe with the columns: label, text
    '''

    rows = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip() # strip \n at the end

            if not line: # skip if line if empty
                continue

            pieces = line.split(maxsplit=1) # get the lines in two pieces, 1st piece being the dialog act and the 2nd being the utterance
            
            label, text = pieces[0], pieces[1]
            rows.append((label,text))
    
    # create a dataframe with the appended rows
    df = pd.DataFrame(rows, columns=['label','text'])

    return df

if __name__ == "__main__":
    df = load_data_to_df("dialog_acts.dat")
    print(df.head())

