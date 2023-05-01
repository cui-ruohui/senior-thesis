# A program that highlights all phrases of length n of a certain structure
# currently does not take into account the length of the ending notes

import ms3
import os
import sys
import shutil
import fractions
import glob
import pandas as pd

if len(sys.argv) != 3:
    print('Please specify the phrase length by measure, and the structure')
    quit()
else:
    n = int(sys.argv[1])
    STRUCTURE = sys.argv[2]

PATH = 'phrases_by_length/' + str(n)
if not os.path.exists(PATH):
   os.makedirs(PATH)

if not os.path.exists(PATH + '/' + STRUCTURE):
   os.makedirs(PATH + '/' + STRUCTURE)

# for PIECE in ['K279-1', 'K279-3', 'K280-1', 'K280-3','K280-2']:
for FILENAME in glob.glob('MS3/*.mscx', recursive=False):
    PIECE = FILENAME[4:-5]

    # load phrase information
    phrases = ms3.load_tsv('phrases_by_length/' + str(n) + '/' + PIECE + '.tsv')

    score = ms3.Score('MS3/' + PIECE + '.mscx')

    # indices = [] # indices corresponding to n-bar phrases of the specified structure

    colored = 0
    for i in phrases.index:
        if 'structure' in phrases.columns and pd.isna(phrases.at[i, 'structure']):
        # if 'structure' in phrases.columns and phrases.at[i, 'structure'] == STRUCTURE:

            # score.mscx.parsed.color_notes(from_mc=int(phrases.at[i, 'mc']),
            #                               from_mc_onset=fractions.Fraction(phrases.at[i, 'mc_onset']),
            #                               to_mc=int(phrases.at[i, 'mc_end']),
            #                               to_mc_onset=fractions.Fraction(phrases.at[i, 'mc_onset_end']),
            #                               color_name='blue') # why can't I color non-chord tones in K279-1?
            # colored = 1
            shutil.copyfile('phrases/' + PIECE + '/' + str(n) + '/' + str(phrases.at[i, 'mn']) + '.png',
                            PATH + '/sentence' + '/' + PIECE + '-' + str(phrases.at[i, 'mn']) + '.png')

            # indices.append(i)

    # phrases_n = phrases.iloc[indices]
    # ms3.write_tsv(phrases_n, PATH + '/' + PIECE + '.tsv')

    # if colored:
        # score.store_score(PATH + '/' + PIECE + '-other.mscx')
