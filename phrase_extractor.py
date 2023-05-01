# Helia Cui, 2023/04/24
# A program to extract information about the phrases from the labels (written onto scores in 'MS3/',
# which are extracted into 'harmonies/')
# Output: .tsv files in 'phrases/'


import ms3
import pandas as pd
import os
import fractions
import glob
pd.options.mode.chained_assignment = None  # disable pandas SettingWithCopyWarning, default='warn'

phrase_start = ["{", "}{"]
phrase_end = ["}", "}{"]

PATH = 'phrases'
if not os.path.exists(PATH):
    os.makedirs(PATH)

file = open(r'phrases/information.txt', 'w')

for FILENAME in glob.glob('MS3/*.mscx', recursive=False):
    PIECE = FILENAME[4:-5]

    harmonies = ms3.load_tsv('harmonies/' + PIECE + '.tsv')
    phrases = harmonies[harmonies['phraseend'].isin(phrase_start)]
    phrases = phrases.drop(columns=['duration_qb', 'pedal', 'chord', 'numeral', 'form', 'figbass', 'changes', 'relativeroot',
                          'chord_type', 'globalkey_is_minor', 'localkey_is_minor', 'chord_tones', 'added_tones',
                          'root', 'bass_note'])
    phrases = phrases.rename(columns={'mc': 'from_mc', 'mn': 'from_mn', 'quarterbeats': 'from_quarterbeats',
                            'mc_onset': 'from_mc_onset', 'mn_onset': 'from_mn_onset'})

    for i in phrases.index:
        # find phrase_start and phrase_end in harmonies
        j = i + 1
        while harmonies.at[j, 'phraseend'] not in phrase_end:
            j += 1

        # write phrase_end location
        phrases.at[i, 'to_mc'] = harmonies.at[j, 'mc']
        phrases.at[i, 'to_mn'] = harmonies.at[j, 'mn']
        phrases.at[i, 'to_quarterbeats'] = harmonies.at[j, 'quarterbeats']
        phrases.at[i, 'to_mc_onset'] = harmonies.at[j, 'mc_onset']
        phrases.at[i, 'to_mn_onset'] = harmonies.at[j, 'mn_onset']

        # calculate and write phrase length
        start = harmonies.at[i, 'quarterbeats']
        end = harmonies.at[j, 'quarterbeats']

        if start == '':
            file.write("Missing quarterbeats information for " + PIECE + " at mn " + str(harmonies.at[i, 'mn']) + '\n')
        else:
            if end == '':
                file.write("Missing quarterbeats information for " + PIECE + " at mn " + str(harmonies.at[j, 'mn']) + '\n')
            else:
                phrases.at[i, 'length_qb'] = end - start
                phrases.at[i, 'length_m'] = (end - start) / 4 / fractions.Fraction(phrases.at[i, 'timesig'])

    ms3.write_tsv(phrases, PATH + '/' + PIECE + '.tsv')

file.close()