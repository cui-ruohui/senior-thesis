# Helia Cui, 2023/04/24
# Go through all the phrases of length_m measures, compute repetition matrices
# with a suitable window size.
# Input: length_m
# Output: 'matrices/length_m/PIECE/'
#         Three types of files: .tsv contains the similarities matrix
#                               .png a visualization of the repetition matrix
#                               .npy to be used in later computer analysis


import numpy as np
import matplotlib.pyplot as plt
import glob
import sys
import os
import ms3
from fractions import Fraction
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

# window size
FULL = 0
HALF = 1

if not os.path.exists('matrices'):
    os.makedirs('matrices')


def compare_by_staff(notes1, start1, end1, notes2, start2, end2, staff):  # start1, end1, start2, end2 in quarterbeats TODO: end2 not used
    # check if any of the segments has no notes in the specified staff
    notes1 = notes1[notes1['staff'] == staff]
    notes2 = notes2[notes2['staff'] == staff]

    if notes1.empty & notes2.empty:
        return 100.0, 100.0
    if notes1.empty | notes2.empty:
        return 0.0, 0.0

    # calculate the onsets (in quarterbeats)
    onsets1 = set()
    onsets2 = set()
    for qb in notes1['quarterbeats']:
        onsets1.add(qb - start1)
    for qb in notes2['quarterbeats']:
        onsets2.add(qb - start2)

    for i in notes1.index:
        notes1.loc[i, 'onset_qb'] = notes1.at[i, 'quarterbeats'] - start1
    for i in notes2.index:
        notes2.loc[i, 'onset_qb'] = notes2.at[i, 'quarterbeats'] - start2

    # The number of overlapping attacks over the number of distinctive elements.
    similarity_onset = len(onsets1 & onsets2) / float(len(onsets1 | onsets2)) * 100

    duration_qb = int(end1 - start1)
    score_by_quarterbeat = np.zeros(duration_qb)
    for beat in range(duration_qb):
        pitches1 = set(notes1[(notes1['quarterbeats'] >= (start1 + beat)) & (notes1['quarterbeats'] < (start1 + beat + 1))]['tpc'])
        pitches2 = set(notes2[(notes2['quarterbeats'] >= (start2 + beat)) & (notes2['quarterbeats'] < (start2 + beat + 1))]['tpc'])
        if pitches1.issubset(pitches2) or pitches2.issubset(pitches1):
            score_by_quarterbeat[beat] = 100.0

    similarity_pitch = np.average(score_by_quarterbeat)

    return similarity_onset, similarity_pitch


def compare(notes_all, windows, i, j, offset_dict):
    from_mc = windows.at[i, 'from_mc']
    from_mc_onset = windows.at[i, 'from_mc_onset']
    to_mc = windows.at[i, 'to_mc']
    to_mc_onset = windows.at[i, 'to_mc_onset']
    if from_mc == to_mc:
        notes1 = notes_all[(notes_all['mc'] == from_mc) & (notes_all['mc_onset'] >= from_mc_onset)
                           & (notes_all['mc_onset'] < to_mc_onset)]
    else:
        notes1 = notes_all[((notes_all['mc'] == from_mc) & (notes_all['mc_onset'] >= from_mc_onset)) |
                           ((notes_all['mc'] > from_mc) & (notes_all['mc'] < to_mc)) |
                           ((notes_all['mc'] == to_mc) & (notes_all['mc_onset'] < to_mc_onset))
                           ]
    start1 = offset_dict[from_mc] + from_mc_onset * 4
    end1 = offset_dict[to_mc] + to_mc_onset * 4

    from_mc = windows.at[j, 'from_mc']
    from_mc_onset = windows.at[j, 'from_mc_onset']
    to_mc = windows.at[j, 'to_mc']
    to_mc_onset = windows.at[j, 'to_mc_onset']
    if from_mc == to_mc:
        notes2 = notes_all[(notes_all['mc'] == from_mc) & (notes_all['mc_onset'] >= from_mc_onset)
                           & (notes_all['mc_onset'] < to_mc_onset)]
    else:
        notes2 = notes_all[((notes_all['mc'] == from_mc) & (notes_all['mc_onset'] >= from_mc_onset)) |
                           ((notes_all['mc'] > from_mc) & (notes_all['mc'] < to_mc)) |
                           ((notes_all['mc'] == to_mc) & (notes_all['mc_onset'] < to_mc_onset))
                           ]
    start2 = offset_dict[from_mc] + from_mc_onset * 4
    end2 = offset_dict[to_mc] + to_mc_onset * 4

    # similarity_onset_1, similarity_pitch_1 = compare_by_staff(notes1, start1, end1, notes2, start2, end2, 1)
    # similarity_onset_2, similarity_pitch_2 = compare_by_staff(notes1, start1, end1, notes2, start2, end2, 2)
    similarities_1 = compare_by_staff(notes1, start1, end1, notes2, start2, end2, 1)
    similarities_2 = compare_by_staff(notes1, start1, end1, notes2, start2, end2, 2)

    return tuple(map(lambda i, j: (i + j)/2, similarities_1, similarities_2))


if len(sys.argv) != 2:
    print('Please specify the phrase length by measure')
    quit()
else:
    length_m = int(sys.argv[1])

for FILENAME in glob.glob('phrases/' + str(length_m) + '/*.tsv', recursive=False):
    PIECE = FILENAME[-10:-4]
# for PIECE in ['K279-1']:  # for debugging
    phrases = ms3.load_tsv('phrases/' + str(length_m) + '/' + PIECE + '.tsv')
    notes = ms3.load_tsv('notes/' + PIECE + '.tsv')
    measures = ms3.load_tsv('measures/' + PIECE + '.tsv')
    offset_dict = ms3.utils.make_offset_dict_from_measures(measures)
    window_size = FULL
    for phrase in phrases.index:
        timesig = str(phrases.at[phrase, 'timesig'])
        if length_m <= 6:
            if timesig not in ['2/4', '3/4', '3/8', '9/8']:
                window_size = HALF
        timesig = Fraction(timesig)
        if window_size == FULL:
            if not pd.isna(measures.at[int(phrases.at[phrase, 'from_mc']) - 1, 'dont_count']):
                from_mc = int(phrases.at[phrase, 'from_mc']) + 1
            else:
                from_mc_onset = Fraction(phrases.at[phrase, 'from_mc_onset'])
                if from_mc_onset > timesig / 2:
                    from_mc = int(phrases.at[phrase, 'from_mc']) + 1
                else:
                    from_mc = int(phrases.at[phrase, 'from_mc'])

            if Fraction(phrases.at[phrase, 'to_mc_onset']) >= timesig / 2:
                n = int(phrases.at[phrase, 'to_mc']) - from_mc + 1
            else:
                n = int(phrases.at[phrase, 'to_mc']) - from_mc

            windows = pd.DataFrame(index=range(n), columns=['from_mc', 'from_mc_onset', 'to_mc', 'to_mc_onset'])
            for i in range(n):
                windows.at[i, 'from_mc'] = from_mc
                windows.at[i, 'from_mc_onset'] = 0
                windows.at[i, 'to_mc'] = from_mc + 1
                windows.at[i, 'to_mc_onset'] = 0
                from_mc += 1

        if window_size == HALF:
            short = 0  # 1 if the first window starts in the middle of a measure, used to calculate n
            if not pd.isna(measures.at[int(phrases.at[phrase, 'from_mc']) - 1, 'dont_count']):
                from_mc = int(phrases.at[phrase, 'from_mc']) + 1
                from_mc_onset = 0
            else:
                from_mc_onset = Fraction(phrases.at[phrase, 'from_mc_onset'])
                if from_mc_onset > timesig * 3 / 4:
                    from_mc = int(phrases.at[phrase, 'from_mc']) + 1
                    from_mc_onset = 0
                elif timesig / 4 < from_mc_onset <= timesig * 3 / 4:
                    from_mc = int(phrases.at[phrase, 'from_mc'])
                    from_mc_onset = timesig / 2
                    short = 1
                else:
                    from_mc = int(phrases.at[phrase, 'from_mc'])
                    from_mc_onset = 0

            if Fraction(phrases.at[phrase, 'to_mc_onset']) >= timesig / 2:
                n = (int(phrases.at[phrase, 'to_mc']) + 1 - from_mc) * 2 - short
            else:
                n = (int(phrases.at[phrase, 'to_mc']) - from_mc) * 2 + 1 - short

            windows = pd.DataFrame(index=range(n), columns=['from_mc', 'from_mc_onset', 'to_mc', 'to_mc_onset'])
            for i in range(n):
                windows.at[i, 'from_mc'] = from_mc
                windows.at[i, 'from_mc_onset'] = from_mc_onset
                if from_mc_onset < timesig / 2:
                    windows.at[i, 'to_mc'] = from_mc
                    windows.at[i, 'to_mc_onset'] = from_mc_onset + timesig / 2
                    from_mc_onset = from_mc_onset + timesig / 2
                else:
                    windows.at[i, 'to_mc'] = from_mc + 1
                    windows.at[i, 'to_mc_onset'] = from_mc_onset - timesig / 2
                    from_mc += 1
                    from_mc_onset = from_mc_onset - timesig / 2

        similarities = pd.DataFrame(index=range(n), columns=range(1, n))
        repetitions = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                similarities.at[i, j] = compare(notes, windows, i, j, offset_dict)
                if similarities.at[i, j][0] > 85:  #
                    repetitions[i, j] = 1
                elif similarities.at[i, j][0] > 40 and similarities.at[i, j][1] > 85:
                    repetitions[i, j] = 1

        ms3.write_tsv(similarities, 'matrices/' + str(length_m) + '/' + PIECE + '/' + str(phrases.at[phrase, 'from_mn']) + '.tsv')
        np.save('matrices/' + str(length_m) + '/' + PIECE + '/' + str(phrases.at[phrase, 'from_mn']), repetitions)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        cax = ax.matshow(repetitions, vmin=0, vmax=1)
        fig.colorbar(cax)
        if window_size == FULL:
            labels = [str(x) for x in range(1, n+1)]
        else:
            labels = [str((x+1)/2) for x in range(1, n + 1)]
        ax.set_xticks(range(n))
        ax.set_xticklabels(labels)
        ax.set_yticks(range(n))
        ax.set_yticklabels(labels)
        ax.set_title(PIECE + '-' + str(phrases.at[phrase, 'from_mn']))
        plt.savefig('matrices/' + str(length_m) + '/' + PIECE + '/' + str(phrases.at[phrase, 'from_mn']) + '.png')
        plt.close()

