from tqdm import *
import re
from collections import Counter

pos_file = "E:\\machine-learning\\codeclone\\pos.txt"
neg_file = "E:\\machine-learning\\codeclone\\neg.txt"

pos_output = "E:\\machine-learning\\codeclone\\pos-remove@.txt"
neg_output = "E:\\machine-learning\\codeclone\\neg-remove@.txt"

tokens_counter = Counter()
max = 0
lines = []
with open(pos_file, 'r', encoding='UTF-8') as pos_reader:
    for line in pos_reader.readlines():
        lines.append(line)
with open(neg_file, 'r', encoding='UTF-8') as neg_reader:
    for line in neg_reader.readlines():
        lines.append(line)
for i in tqdm(range(len(lines))):
    line = lines[i]
    line = re.sub('[\@]{2}', '', line)
    functions = line.split('< eo f / >')
    for function in functions:
        tokens = function.split(' ')
        tokens_counter[len(tokens)] += 1
        if len(tokens) > max:
            max = len(tokens)

less_than_50 = 0
from50_100 = 0
from100_150 = 0
from150_200 = 0
from200_250 = 0
from250_300 = 0
from300_350 = 0
from350_400 = 0
above400 = 0

for name, value in tokens_counter.most_common():
    if int(name) < 50:
        less_than_50 += value
        pass
    elif int(name) < 100:
        from50_100 += value
        pass
    elif int(name) < 150:
        from100_150 += value
        pass
    elif int(name) < 200:
        from150_200 += value
        pass
    elif int(name) < 250:
        from200_250 += value
        pass
    elif int(name) < 300:
        from250_300 += value
        pass
    elif int(name) < 350:
        from300_350 += value
        pass
    elif int(name) < 400:
        from350_400 += value
        pass
    else:
        above400 += value

print('max:' + str(max))

print(str(less_than_50), str(from50_100), str(from100_150), str(from150_200), str(from200_250), str(from250_300),
      str(from300_350), str(from350_400), str(above400))
