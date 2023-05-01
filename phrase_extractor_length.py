# Helia Cui, 2023/04/24
# A program that extracts all phrases that last n measures.
# Output: 'phrases/n/'

# currently does not take into account the length of the ending notes

import sys
import ms3
import os
import fractions
import glob
import pandas as pd


if len(sys.argv) != 2:
    print('Please specify the phrase length by measure')
    quit()
else:
    n = int(sys.argv[1])

PATH = 'phrases/' + str(n)
if not os.path.exists(PATH):
   os.makedirs(PATH)

for FILENAME in glob.glob('MS3/*.mscx', recursive=False):
    PIECE = FILENAME[4:-5]

    # load phrase information
    phrases = ms3.load_tsv('phrases/' + PIECE + '.tsv')

    indices = []  # indices corresponding to n-bar phrases

    for i in phrases.index:
        if (not pd.isna(phrases.at[i, 'length_m'])) and (round(fractions.Fraction(phrases.at[i, 'length_m'])) == n):
            indices.append(i)

    phrases_n = phrases.iloc[indices]
    if not phrases_n.empty:
        ms3.write_tsv(phrases_n, PATH + '/' + PIECE + '.tsv')
