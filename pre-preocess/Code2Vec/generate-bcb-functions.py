import sys

sys.path.extend(["../../", "../", "./"])
from configparser import ConfigParser
from multiprocessing import Process, Pool
import hashlib, os, argparse, time
from tqdm import *
from utils.Preprocessor import *
from utils.Normalizer import *
from utils.RelationExtractor import *
from utils.apply_bpe import *


def extract_function_body(function):
    return_string = ''
    num_level = 0
    is_in_body = False
    for char in function:
        if char == '{':
            num_level += 1
            if num_level == 1:
                is_in_body = True
            return_string += char
        elif char == '}':
            num_level -= 1
            return_string += char
            if num_level == 0:
                is_in_body = False
        else:
            if is_in_body:
                return_string += char
    return return_string


def process(config, functions, thread_no, bpe):
    print('thread #%d start' % (thread_no))
    thread_start = time.time()
    index = 0
    token_tokenized = ''
    stmt_tokenized = ''
    bpe_tokenized = ''
    ori_untokenized = ''
    preprocessor = PreProcessor()
    special_cutter = SpecialCharCutter(config)
    brace_cutter = BracesCutter()
    normalizer = Normalizer(config)
    extractor = RelationExtractor(config)
    bcb_base = config.get('IO', 'BCB_CODE_BASE')

    for info_str in functions:
        index += 1
        infos = info_str.split(',')
        file_path = os.path.join(bcb_base, os.path.join(infos[0], os.path.join(infos[1], infos[2])))
        start_loc = infos[3]
        end_loc = infos[4]
        with open(file_path, 'r', encoding='iso8859-1') as reader:
            j = 1
            f = ''
            for line in reader.readlines():
                if int(start_loc) <= j <= int(end_loc):
                    f += line.strip() + '\n'
                j += 1
                if j > int(end_loc):
                    break
        f = preprocessor.remove_comments(f)
        f = extract_function_body(f)
        f4ori = f
        f = normalizer.normalize_literal_values(f)
        f = special_cutter.cut(f)
        f = brace_cutter.cut(f)
        _, _, function_bpe, _, bpe_node_list, _ = extractor.extract(f)
        stmt_tokenized += function_bpe + '\nc -1\nh -1\n'
        token_tokenized += re.sub(r'\$\$', ' ', function_bpe) + '\nc -1\nh -1\n'
        function_bpe = bpe.process_line(function_bpe)
        bpe_tokenized += re.sub(r'@@', ' ', function_bpe) + '\nc -1\nh -1\n'
        extractor.reset()
        ori_untokenized += info_str.strip() + '\n\n'
        token_tokenized += info_str.strip() + '\n\n'
        stmt_tokenized += info_str.strip() + '\n\n'
        bpe_tokenized += info_str.strip() + '\n\n'

        if index % 100 == 0:
            print('thread #%d progress %d / %d = %.2f' % (thread_no, index, len(functions), index / len(functions)))

    thread_end = time.time()
    print('thread #%d end in %.2f ' % (thread_no, (thread_end - thread_start)))
    return (ori_untokenized, token_tokenized, stmt_tokenized, bpe_tokenized)


def write_files(output_base, ori_untokenized, token_tokenized, stmt_tokenized, bpe_tokenized):
    token_output_file = os.path.join(output_base, 'token.txt')
    stmt_output_file = os.path.join(output_base, 'stmt.txt')
    bpe_output_file = os.path.join(output_base, 'bpe.txt')
    ori_output_file = os.path.join(output_base, 'ori.txt')

    token_writer = open(token_output_file, 'w', encoding='UTF-8')
    stmt_writer = open(stmt_output_file, 'w', encoding='UTF-8')
    bpe_writer = open(bpe_output_file, 'w', encoding='UTF-8')
    ori_writer = open(ori_output_file, 'w', encoding='UTF-8')

    token_writer.write(''.join(token_tokenized))
    ori_writer.write(''.join(ori_untokenized))
    bpe_writer.write(''.join(bpe_tokenized))
    stmt_writer.write(''.join(stmt_tokenized))

    token_writer.close()
    stmt_writer.close()
    bpe_writer.close()
    ori_writer.close()


if __name__ == '__main__':
    print('Run the main process (%s)' % (os.getpid()))
    config = ConfigParser()
    config.read('config/myconfig.ini')
    code_file = config.get('IO','TPE_CODE')

    print(code_file)
    codes = open(code_file, 'r', encoding='utf-8')
    start = time.time()
    bpe_processor = BPE(codes, -1, '@@', None, None)
    bcb_nonclones_input = config.get('IO', 'BCB_NONCLONES_INPUT')
    bcb_clones_input = config.get('IO', 'BCB_CLONES_INPUT')
    output_base = os.path.join(config.get('IO', 'EXPERIMENT_OUT_BASE'), 'functions')
    function_info_file = os.path.join(output_base, 'function-info.txt')
    if not os.path.exists(function_info_file):
        with open(bcb_clones_input, 'r', encoding='UTF-8') as reader:
            clone_pairs = [line.strip() for line in reader.readlines() if line.strip() != '']
        with open(bcb_nonclones_input, 'r', encoding='UTF-8')as reader:
            clone_pairs.extend([line.strip() for line in reader.readlines() if line.strip() != ''])
        function_dict = {}
        for i in tqdm(range(len(clone_pairs))):
            pair = clone_pairs[i]
            # 2;sample,DownloadWebpage.java,32,53;sample,DownloadWebpage.java,55,67;4
            pair_info = pair.split(';')
            function_infos = [pair_info[0] + ',' + pair_info[1], pair_info[0] + ',' + pair_info[2]]
            for function in function_infos:
                key = hashlib.md5(function.encode('utf-8')).hexdigest()
                if key in function_dict.keys():
                    pass
                else:
                    function_dict[key] = function
        all_functions = [v for _, v in function_dict.items()]
        with open(function_info_file, 'w', encoding='UTF-8') as writer:
            writer.write('\n'.join([v for _, v in function_dict.items()]))
    else:
        all_functions = []
        with open(function_info_file, 'r', encoding='UTF-8') as reader:
            for line in reader.readlines():
                line = line.strip()
                all_functions.append(line)
    # num_pairs = 10
    ori = []
    token = []
    stmt = []
    bpe = []
    res = []
    # num_pairs = 15
    # num_thread = 1
    num_pairs = int(len(all_functions) / 20) + 1
    num_thread = 20
    print('平均每个线程处理 %d 条数据，共 %d 个进程' % (num_pairs, num_thread))
    pool = Pool(num_thread)
    for i in range(num_thread):
        i = i + 1
        list_start = (i - 1) * num_pairs
        list_end = i * num_pairs
        if list_end >= len(all_functions):
            target_functions = all_functions[list_start:]
        else:
            target_functions = all_functions[list_start:list_end]
        res.append(pool.apply_async(process, args=(config, target_functions, i, bpe_processor)))

    pool.close()
    pool.join()
    end = time.time()
    for s in res:
        (ori_untokenized, token_tokenized, stmt_tokenized, bpe_tokenized) = s.get()
        ori.append(ori_untokenized)
        token.append(token_tokenized)
        stmt.append(token_tokenized)
        bpe.append(bpe_tokenized)
    print('处理共计耗时 %.2f' % (end - start))
    write_files(output_base, ori, token, stmt, bpe)
    end = time.time()
    print('写文件结束，共计耗时 %.2f' % (end - start))
