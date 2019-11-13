import os
import hashlib
from tqdm import *
from Preprocessor import *

if __name__ == '__main__':

    preprocessor = PreProcessor()
    code_base = './'
    output_file = 'nonclone-candidates.txt'
    final_output = 'nonclone.txt'
    progress = 'progress.txt'
    if not os.path.exists(output_file):
        all_functions = []

        gy_pais_base = '/home/yanglin/Code2Vec/out/input/gy'
        files = ['gy-clone-pairs.txt', 'gy-type1.txt']
        functions = {}
        id2function = {}
        id2pairs = {}
        for file in files:
            file_path = os.path.join(gy_pais_base, file)
            with open(file_path, 'r', encoding='utf-8') as reader:
                for line in reader.readlines():
                    line = line.strip()
                    info = line.split(';')
                    l_f = info[0]
                    r_f = info[1]
                    package = l_f.split(',')[0]
                    if package not in functions.keys():
                        functions[package] = []
                    l_key = hashlib.md5(l_f.encode('utf-8')).hexdigest()
                    r_key = hashlib.md5(r_f.encode('utf-8')).hexdigest()
                    pair_1 = l_key + r_key
                    pair_2 = r_key + l_key
                    p_key_1 = hashlib.md5(pair_1.encode('utf-8')).hexdigest()
                    p_key_2 = hashlib.md5(pair_2.encode('utf-8')).hexdigest()
                    if l_key not in id2function.keys():
                        id2function[l_key] = l_f
                        functions[package].append(l_f)
                    if r_key not in id2function.keys():
                        id2function[r_key] = r_f
                        functions[package].append(r_f)
                    if p_key_1 in id2pairs.keys() or p_key_2 in id2pairs.keys():
                        pass
                    else:
                        id2pairs[p_key_1] = ';'.join([l_f, r_f])
        for package, list in functions.items():
            writer = open(output_file + package, 'w', encoding='UTF-8')
            for i in range(len(list)):
                for j in range(i + 1, len(list)):
                    pair_info = list[i] + ';' + list[j]
                    key = hashlib.md5(pair_info.encode('utf-8')).hexdigest()
                    if key in id2pairs.keys():
                        continue
                    else:
                        writer.write(pair_info + '\n')
            writer.close()

        # i = 0
        # for file in all_files:
        #     # /home/yanglin/dataset/bcb_reduced/47/opennlp_1.8.1/TokenNameFinderCrossValidator.java
        #     file_name = os.path.basename(file)
        #     parent_dir = os.path.basename(os.path.dirname(file))
        #     with open(file, 'r', encoding='UTF-8') as reader:
        #         ori_content = reader.read()
        #         # ori_content = preprocessor.remove_comments(ori_content)
        #     functions = function_finder.find_function_with_lines(ori_content)
        #     for function_str, start, end in functions:
        #         if end - start < 5:
        #             continue
        #         else:
        #             all_functions.append([parent_dir, file_name, str(start), str(end)])
        #
        # for i in tqdm(range(len(all_functions))):
        #     for j in range(i + 1, len(all_functions)):
        #         pair = [','.join(all_functions[i]), ','.join(all_functions[j])]
        #         writer.write(';'.join(pair) + '\n')
    else:
        if os.path.exists(progress):
            with open(progress, 'r', encoding='utf-8') as reader:
                last_end = reader.read()
                last_end = last_end.strip()
                if last_end == '' or last_end is None:
                    last_end = 0
        else:
            last_end = 0
        final_writer = open(final_output, 'a', encoding='UTF-8')
        reader = open(output_file, 'r', encoding='UTF-8')
        print('开始读取文件，从第%d条开始：' % (int(last_end)))
        line = reader.readline()
        line = line.strip()
        i = 0
        while line != '' and line is not None:
            if i < int(last_end):
                i += 1
                line = reader.readline()
                line = line.strip()
                continue
            line = line.strip()
            infos = line.split(';')
            l_f = infos[0].split(',')
            r_f = infos[1].split(',')
            file_path = os.path.join(code_base, os.path.join(l_f[0], l_f[1]))
            l_function = ''
            with open(file_path, 'r', encoding='UTF-8') as lreader:
                j = 1
                for tmpline in lreader.readlines():
                    tmpline = tmpline.strip()
                    if int(l_f[2]) <= j <= int(l_f[3]):
                        l_function += tmpline + '\n'
                    elif j > int(l_f[3]):
                        break
                    j += 1
            print(preprocessor.remove_comments(l_function))
            print('========================================================')
            file_path = os.path.join(code_base, os.path.join(r_f[0], r_f[1]))
            r_function = ''
            with open(file_path, 'r', encoding='UTF-8') as rreader:
                j = 1
                for tmpline in rreader.readlines():
                    tmpline = tmpline.strip()
                    if int(r_f[2]) <= j <= int(r_f[3]):
                        r_function += tmpline + '\n'
                    elif j > int(r_f[3]):
                        break
                    j += 1
            print(preprocessor.remove_comments(r_function))
            tag = input('是否是 非克隆对 : (y/n,q退出)')
            while tag not in ['y', 'Y', 'n', 'N', 'q', 'Q']:
                tag = input('是否是 非克隆对 : (y/n)')
            if tag in ['q', 'Q']:
                with open(progress, 'w', encoding='utf-8') as progress_writer:
                    progress_writer.write(str(i))
                break
            if tag in ['y', 'Y']:
                final_writer.write(line + '\n')
            line = reader.readline()
            line = line.strip()
            print('========================================================')
            i += 1
        reader.close()
        final_writer.close()
