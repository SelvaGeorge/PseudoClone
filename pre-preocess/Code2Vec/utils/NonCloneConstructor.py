from collections import Counter
from tqdm import *


class Constructor:
    non_clones_per_functionality = Counter()

    def __init__(self, config):
        self.config = config

    def read_nonclones(self):
        non_clones = []
        file_path = self.config.get(section='IO', option='BCB_NONCLONES_INPUT')
        with open(file_path, 'r', encoding='UTF-8') as reader:
            lines = reader.readlines()
            for i in tqdm(range(len(lines))):
                # 2;selected,2235447.java,39,100;sample,DownloadWebpage.java,55,67
                line = lines[i]
                line = line.strip()
                infos = line.split(';')
                self.non_clones_per_functionality[infos[0]] += 1
                non_clone = [infos[0], infos[1], infos[2]]
                non_clones.append(non_clone)

        # the function below should be only used once to save some information.
        # self.save_non_clones_info()
        return non_clones

    def save_non_clones_info(self):
        middle_output_file = self.config.get(section='MIDDLE', option='NONCLONES_INFO_OUTPUT')
        with open(middle_output_file, 'w', encoding='UTF-8') as writer:
            for name, count in self.non_clones_per_functionality.most_common():
                writer.write(name + ',' + str(count) + "\n")
