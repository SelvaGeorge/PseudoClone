import os


class FileFinder:

    def find_files(self, code_base='', target_postfix='java'):
        all_java_files = []
        if os.path.isfile(code_base):
            all_java_files.append(code_base)
        else:
            for root, dirs, files in os.walk(code_base):
                for file in files:
                    if os.path.splitext(file)[1] == '.' + target_postfix:
                        # self_defined_classes[file[:-5]] += 1
                        all_java_files.append(os.path.join(root, file))
                for dir in dirs:
                    all_java_files.extend(self.find_files(dir))
        return all_java_files
