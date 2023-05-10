# Helia Cui, 2023/05/09
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


if not os.path.exists('structures'):
   os.makedirs('structures')

PATH = 'structures/' + STRUCTURE + '/' + str(n)
if not os.path.exists(PATH):
   os.makedirs(PATH)

# for PIECE in ['K279-1', 'K279-3', 'K280-1', 'K280-3','K280-2']:
for FILENAME in glob.glob('phrases/' + str(n) + '/*.tsv', recursive=False):
    PIECE = FILENAME[-10:-4]

    # load phrase information
    phrases = ms3.load_tsv('phrases/' + str(n) + '/' + PIECE + '.tsv')

    score = ms3.Score('MS3/' + PIECE + '.mscx')

    indices = [] # indices corresponding to n-bar phrases of the specified structure

    colored = 0
    for i in phrases.index:
        if STRUCTURE == 'other':
            if 'structure' in phrases.columns and pd.isna(phrases.at[i, 'structure']):

                score.mscx.parsed.color_notes(from_mc=int(phrases.at[i, 'from_mc']),
                                              from_mc_onset=fractions.Fraction(phrases.at[i, 'from_mc_onset']),
                                              to_mc=int(phrases.at[i, 'to_mc_end']),
                                              to_mc_onset=fractions.Fraction(phrases.at[i, 'to_mc_onset']),
                                              color_name='blue') # why can't I color non-chord tones in K279-1?
                colored = 1
                shutil.copyfile('matrices/' + str(n) + '/' + PIECE + '/' + str(phrases.at[i, 'from_mn']) + '.png',
                                PATH + '/' + PIECE + '-' + str(phrases.at[i, 'from_mn']) + '.png')

                indices.append(i)
        else:
            if 'structure' in phrases.columns and phrases.at[i, 'structure'] == STRUCTURE:
                score.mscx.parsed.color_notes(from_mc=int(phrases.at[i, 'from_mc']),
                                              from_mc_onset=fractions.Fraction(phrases.at[i, 'from_mc_onset']),
                                              to_mc=int(phrases.at[i, 'to_mc']),
                                              to_mc_onset=fractions.Fraction(phrases.at[i, 'to_mc_onset']),
                                              color_name='blue') # why can't I color non-chord tones in K279-1?
                colored = 1
                shutil.copyfile('matrices/' + str(n) + '/' + PIECE + '/' + str(phrases.at[i, 'from_mn']) + '.png',
                                PATH + '/' + PIECE + '-' + str(phrases.at[i, 'from_mn']) + '.png')

                indices.append(i)

    # phrases_n = phrases.iloc[indices]
    # ms3.write_tsv(phrases_n, PATH + '/' + PIECE + '.tsv')

    if colored:
        score.store_score(PATH + '/' + PIECE + '.mscx')
