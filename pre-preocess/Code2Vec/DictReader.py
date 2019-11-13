class DictReader:

    def __init__(self, config):
        self.config = config

    def load(self):
        java_keyword = self.read_java_keyword()
        imported_java, imported_outside = self.read_imported_class()
        self_defined = self.read_self_defined()
        self_defined.extend(imported_outside)
        return java_keyword, imported_java, self_defined
    def read_java_keyword(self):
        return_dict = []
        dict_file = self.config.get(section='MIDDLE', option='JAVA_KEYWORD_DICT')
        with open(dict_file, 'r', encoding='UTF-8') as reader:
            for line in reader.readlines():
                if line != '' and line != '\n':
                    words = line.split(',')
                    for word in words:
                        if word != '':
                            word = word.strip()
                            return_dict.append(word)

        return set(return_dict)

    def read_imported_class(self):
        imported_java_classes = []
        imported_outside_classes = []
        vocab_file = self.config.get(section='MIDDLE', option='IMPORTED_CLASSES')
        end_of_java_classes = False
        with open(vocab_file, 'r', encoding='UTF-8') as reader:
            for line in reader.readlines():
                line = line.strip()
                if line == '<java-classes-end>':
                    end_of_java_classes = True
                    pass
                if not end_of_java_classes:
                    imported_java_classes.append(line.split(' ')[0])
                else:
                    imported_outside_classes.append(line.split(' '[0]))

        return imported_java_classes, imported_outside_classes

    def read_self_defined(self):
        self_defined_classes = []
        vocab_file = self.config.get(section='MIDDLE', option='SELF_DEFINED_CLASSES')
        with open(vocab_file, 'r', encoding='UTF-8') as reader:
            for line in reader.readlines():
                if line[0].isupper():
                    self_defined_classes.append(line.split(' ')[0])
        return self_defined_classes
