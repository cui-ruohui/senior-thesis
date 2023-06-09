# Helia Cui, 2023/05/09
# a method that opens MuseScore and highlights a particular phrase (given mn) in a specified piece


import subprocess
import os
import ms3
import fractions
import glob


def highlight(PIECE, mn):
    if not os.path.exists('temp'):
        os.makedirs('temp')

    score = ms3.Score('MS3/' + PIECE + '.mscx')
    phrases = ms3.load_tsv('phrases/' + PIECE + '.tsv')

    i = phrases[phrases['from_mn'] == mn].index[0]
    score.mscx.parsed.color_notes(from_mc=int(phrases.at[i, 'from_mc']),
                                  from_mc_onset=fractions.Fraction(phrases.at[i, 'from_mc_onset']),
                                  to_mc=int(phrases.at[i, 'to_mc']),
                                  to_mc_onset=fractions.Fraction(phrases.at[i, 'to_mc_onset']),
                                  color_name='red') # why can't I color non-chord tones in K279-1?

    score.store_score('temp/' + PIECE + '.mscx')
    subprocess.call(['open', 'temp/' + PIECE + '.mscx'])  # '/Applications/MuseScore 3.app/Contents/MacOS/mscore'
    # os.remove('temp/' + PIECE + '.mscx')
    return


def clear_temp():
    for FILE in glob.glob('temp/*.mscx', recursive=False):
        os.remove(FILE)


# highlight('K283-1', 23)
# clear_temp()
