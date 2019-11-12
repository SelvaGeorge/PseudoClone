from collections import Counter

from tqdm import *


class Constructor:
    clones_per_functionality = Counter()
    clones_per_similarity = Counter()
    train = []
    dev = []
    test = []

    def __init__(self, config):
        self.config = config

    # def read_clones(self, file_path):
    #     # file_path = self.config.get(section='IO', option='BCB_CLONES_OUTPUT')
    #     clones = [[], [], []]
    #     with open(file_path, 'r', encoding='UTF-8') as reader:
    #         lines = reader.readlines()
    #         target = -1
    #         for i in tqdm(range(len(lines))):
    #             line = lines[i]
    #             line = line.strip()
    #             if line != '':
    #                 if target == -1 or line.startswith('<'):
    #                     if line == '<train>':
    #                         target = 0
    #                     elif line == '<dev>':
    #                         target = 1
    #                     elif line == '<test>':
    #                         target = 2
    #                     elif line.endswith('/>'):
    #                         target = -1
    #                 else:
    #                     clone = self.extract_clone(line)
    #                     clones[target].append(clone)
    #                     pass
    #
    #         self.train = clones[0]
    #         self.dev = clones[1]
    #         self.test = clones[2]
    #
    #     # the function below should be only used once to save some information.
    #     # self.save_clones_info()
    #     return self.train, self.dev, self.test

    def extract_clone(self, line):
        infos = line.split(';')
        clone = [infos[0], infos[1], infos[2]]
        return clone

    def save_clones_info(self):
        middle_output_file = self.config.get(section='MIDDLE', option='CLONES_INFO_OUTPUT')
        with open(middle_output_file, 'w', encoding='UTF-8') as writer:
            for name, count in self.clones_per_similarity.most_common():
                writer.write(name + ',' + str(count) + "\n")
            writer.write('<end/>\n')
            for name, count in self.clones_per_functionality.most_common():
                writer.write(name + ',' + str(count) + "\n")
