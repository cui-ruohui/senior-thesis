# Helia Cui, 2023/04/29
# Classify phrases by their repetition pattern. Currently supporting only 4-bar and 8-bar phrases.
# Categories: sentence (AABC), period (ABAC), ABBC, AAAC, other, no_repetition
# Input: phrase information in 'phrases/length_m/PIECE.tsv' and repetition matrix in 'matrices/length_m/PIECE/*.npy'
# Output: column 'structure' in 'phrases/length_m/PIECE.tsv',
#         statistics in stdout, graph 'length_m-pie.png'


import sys
import ms3
import glob
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    print('Please specify the phrase length by measure')
    quit()
else:
    length_m = int(sys.argv[1])

total = 0
sentence_cnt = 0
period_cnt = 0
ABBC_cnt = 0
AAAC_cnt = 0
no_repetition_cnt = 0

for FILENAME in glob.glob('phrases/' + str(length_m) + '/*.tsv', recursive=False):
    PIECE = FILENAME[-10:-4]
    phrases = ms3.load_tsv('phrases/' + str(length_m) + '/' + PIECE + '.tsv')
    if not phrases.empty:
        for i in phrases.index:
            total += 1
            matrix = np.load('matrices/' + str(length_m) + '/' + PIECE + '/' + str(phrases.at[i, 'from_mn']) + '.npy')
            if 1 not in matrix[:, :]:
                phrases.at[i, 'structure'] = 'no_repetition'
                no_repetition_cnt += 1
            if len(matrix) >= 6:
                if matrix[0, 4] == 1 and matrix[1, 5] == 1:
                    if matrix[0, 2] == 1 and matrix[1, 3] == 1:
                        phrases.at[i, 'structure'] = 'AAAC'
                        AAAC_cnt += 1
                    else:
                        phrases.at[i, 'structure'] = 'period'
                        period_cnt += 1
                elif matrix[0, 2] == 1 and matrix[1, 3] == 1:
                    phrases.at[i, 'structure'] = 'sentence'
                    sentence_cnt += 1
                elif matrix[2, 4] == 1 and matrix[3, 5] == 1:
                    phrases.at[i, 'structure'] = 'ABBC'
                    ABBC_cnt += 1
            else:
                if matrix[0, 2] == 1:
                    if matrix[0, 1] == 1:
                        phrases.at[i, 'structure'] = 'AAAC'
                        AAAC_cnt += 1
                    else:
                        phrases.at[i, 'structure'] = 'period'
                        period_cnt += 1
                elif matrix[0, 1] == 1:
                    phrases.at[i, 'structure'] = 'sentence'
                    sentence_cnt += 1
                elif matrix[1, 2] == 1:
                    phrases.at[i, 'structure'] = 'ABBC'
                    ABBC_cnt += 1
    ms3.write_tsv(phrases, 'phrases/' + str(length_m) + '/' + PIECE + '.tsv')

print('total number of phrases:', total)
print('number of periods:', period_cnt)
print('number of sentences:', sentence_cnt)
print('number of ABBC\'s:', ABBC_cnt)
print('number of AAAC\'s:', AAAC_cnt)
print('number of no_repetition\'s:', no_repetition_cnt)

fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(aspect="equal"))

categories = ['sentence', 'period', 'ABBC', 'AAAC', 'other', 'no_repetition']
data = [sentence_cnt, period_cnt, ABBC_cnt, AAAC_cnt,
        total - sentence_cnt - period_cnt - ABBC_cnt - AAAC_cnt - no_repetition_cnt, no_repetition_cnt]


def func(pct, allvals):
    absolute = int(np.round(pct/100.*np.sum(allvals)))
    return f"{pct:.1f}%\n({absolute:d})"


wedges, texts, autotexts = ax.pie(data, labels=categories, autopct=lambda pct: func(pct, data),
                                  textprops=dict(color="w"))

# ax.legend(wedges, categories,
#           title="Categories",
#           loc="center left",
#           bbox_to_anchor=(1, 0, 0.5, 1))

for i, wedge in enumerate(wedges):
  texts[i].set_color(wedge.get_facecolor())
plt.setp(texts, fontweight=600)
plt.setp(autotexts, size=8, weight="bold")

ax.set_title(str(length_m) + '-bar phrase structures (total: ' + str(total) + ')')
plt.savefig(str(length_m) + '-pie.png')
