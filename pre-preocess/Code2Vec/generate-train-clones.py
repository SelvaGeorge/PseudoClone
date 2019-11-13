import sys

sys.path.extend(["../../", "../", "./"])
from configparser import ConfigParser

import random, hashlib
from Normalizer import *
from RelationExtractor import *
from apply_bpe import *
from multiprocessing import *
import time


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


def save_index_list(index_list, index_list_output):
    with open(index_list_output, 'w', encoding='UTF-8') as writer:
        writer.write(','.join(str(i) for i in index_list))


def load_index_List(index_file):
    with open(index_file, 'r', encoding='UTF-8') as reader:
        content = reader.read()
    index_list = content.split(',')
    return index_list


def get_gy_nonclones(config):
    pairs = []
    gy_nonclones = []
    gy_nonclone_file = config.get('IO', 'GY_NONCLONES_INPUT')
    gy_clone_file = config.get('IO', 'GY_TYPE3_INPUT')
    gy_test_pairs = os.path.join(config.get('IO', 'TEST_OUTPUT_BASE'), 'test_index.dict')
    output_base = config.get('IO', 'TRAIN_OUTPUT_BASE')

    with open(gy_clone_file, 'r', encoding='UTF-8') as  reader:
        for line in reader.readlines():
            line = line.strip()
            if line != '':
                pairs.append(line)
    num_gy_clones = len(pairs)
    with open(gy_nonclone_file, 'r', encoding='UTF-8') as  reader:
        for line in reader.readlines():
            line = line.strip()
            if line != '':
                gy_nonclones.append(line)
    index_list = []

    if os.path.exists(gy_test_pairs):
        index_list = load_index_List(gy_test_pairs)
        pass
    else:
        print('no test file generated, exiting.')
        exit(1)
    for index in index_list:
        index = int(index)
        if index >= num_gy_clones:
            index -= num_gy_clones
            gy_nonclones[index] = ''

    gy_nonclones = [x for x in gy_nonclones if x != '']
    index_file = os.path.join(os.path.join(output_base, 'gy'), 'train_index_gy_nonclone.txt')
    if os.path.exists(index_file):
        train_index_list = load_index_List(index_file)
    else:
        train_index_list = random.sample(range(len(gy_nonclones)), 10000)
        save_index_list(train_index_list, index_file)
    return_nonclones = []
    for index in train_index_list:
        index = int(index)
        return_nonclones.append(gy_nonclones[index])

    # ##########For corpus effect ####################
    # sampled_nonclones = random.sample(return_nonclones, 9000)
    # return sampled_nonclones
    ################################################
    return return_nonclones


def get_autogen(config):
    md5 = hashlib.md5()
    output_base = config.get('IO', 'TRAIN_OUTPUT_BASE')
    autogen_block_input = os.path.join(config.get('IO', 'AUTOGEN_CLONES_BASE'), 'type3.txt')
    autogen_exchange_input = os.path.join(config.get('IO', 'AUTOGEN_CLONES_BASE'), 'exchange_type3.txt')
    with open(autogen_block_input, 'r', encoding='UTF-8') as reader:
        content = reader.read()
    pairs = [x for x in content.split('<eop>') if x != '']
    with open(autogen_exchange_input, 'r', encoding='UTF-8') as reader:
        content = reader.read()
    pairs.extend([x for x in content.split('<eop>') if x != ''])
    autogen_index_file = os.path.join(os.path.join(output_base, 'autogen'), 'train_index_autogen.txt')
    type1_index_file = os.path.join(os.path.join(output_base, 'autogen'), 'train_index_type1.txt')
    if os.path.exists(autogen_index_file):
        autogen_index_list = load_index_List(autogen_index_file)
    else:
        autogen_index_list = random.sample(range(len(pairs)), 10000)
        save_index_list(autogen_index_list, autogen_index_file)
    autogen_type3 = []
    for index in autogen_index_list:
        index = int(index)
        autogen_type3.append(pairs[index])

    function_dict = {}
    for pair in pairs:
        functions = pair.split('<eof>')
        for function in functions:
            function = function.strip()
            key = hashlib.md5(function.encode('UTF-8')).hexdigest()
            if key in function_dict.keys():
                pass
            else:
                function_dict[str(key)] = function
    print(len(function_dict))
    if os.path.exists(type1_index_file):
        sampled_functions = load_index_List(type1_index_file)
    else:
        sampled_functions = random.sample(function_dict.keys(), 10000)
        save_index_list(sampled_functions, type1_index_file)
    type1 = []
    for key in sampled_functions:
        if key in function_dict.keys():
            type1.append(function_dict[key])

    #####################For corpus effec########################
    # sampled_type1 = random.sample(type1, 9000)
    # sampled_autogen = random.sample(autogen_type3, 9000)
    # return sampled_type1, sampled_autogen
    ##############################################################
    return type1, autogen_type3


def load_function(file, start, end):
    f = ''
    with open(file, 'r', encoding='iso8859-1') as reader:
        i = 1
        for line in reader.readlines():
            if int(start) <= i <= int(end):
                f += line
            i += 1
    return f


def process_pairs(thread_no, pairs, config, bpe_processor):
    print('线程 %d 开始工作' % (thread_no))
    num_statement = 0
    normalizer = Normalizer(config)
    preprocessor = PreProcessor()
    special_cutter = SpecialCharCutter(config)
    braces_cutter = BracesCutter()
    extractor = RelationExtractor(config)
    token = []
    stmt = []
    bpe = []
    ori = []
    start_time = time.time()
    index = 0
    for target_pair in pairs:
        tag = target_pair[1]
        functions_info = target_pair[0]
        functions = functions_info.split('<eof>')
        token_tokenized = ''
        stmt_tokenized = ''
        bpe_tokenized = ''
        ori_token = ''
        terminated = False
        if tag == '1':
            functions = [functions[0]]
        for f in functions:
            f = preprocessor.remove_comments(f)
            f = extract_function_body(f)
            f = normalizer.normalize_literal_values(f)
            f = special_cutter.cut(f)
            f = braces_cutter.cut(f)
            num_statement += len(f.split('\n'))
            _, _, function_bpe, _, bpe_node_list, _ = extractor.extract(f)
            function_bpe = bpe_processor.process_line(function_bpe)
            if function_bpe == '' or function_bpe is None:
                terminated = True
                break
            bpe_tokenized += re.sub(r'@@', '', function_bpe) + '\nc -1\nh -1\n'
            extractor.reset()
        if not terminated:
            if tag == '1':
                token_tokenized += token_tokenized
                stmt_tokenized += stmt_tokenized
                bpe_tokenized += bpe_tokenized
                ori_token += ori_token

            token_tokenized += tag + '\n'
            stmt_tokenized += tag + '\n'
            bpe_tokenized += tag + '\n'
            ori_token += tag + '\n'
            postfix = '\n'
            stmt.append(stmt_tokenized + postfix)
            token.append(token_tokenized + postfix)
            bpe.append(bpe_tokenized + postfix)
            ori.append(ori_token + postfix)
            if index % 100 == 0:
                print('进程 %d 处理进度 %d / %d = %.2f 耗时 %.2f' % (
                    thread_no, index, len(pairs), index / len(pairs), time.time() - start_time))
        else:
            continue
        index += 1
    return (ori, token, stmt, bpe, num_statement)


if __name__ == "__main__":
    config = ConfigParser()
    config.read('config/myconfig.ini')
    code_file = config.get('IO', 'TPE_CODE')
    print(code_file)
    codes = open(code_file, 'r', encoding='utf-8')
    normalizer = Normalizer(config)
    preprocessor = PreProcessor()
    extractor = RelationExtractor(config)
    brace_cutter = BracesCutter()
    special_char_cutter = SpecialCharCutter(config)
    random.seed(666)
    all_ori = []
    all_token = []
    all_stmt = []
    all_bpe = []
    bpe = BPE(codes, -1, '@@', None, None)
    gy_nonclone_database = os.path.join(config.get('IO', 'BCB_CODE_BASE'), '46')
    output_base = config.get('IO', 'TRAIN_OUTPUT_BASE')

    # token_output_file = os.path.join(output_base, 'token.txt')
    # origin_token_output_file = os.path.join(output_base, 'ori-token.txt')
    # stmt_output_file = os.path.join(output_base, 'stmt.txt')
    # bpe_output_file = os.path.join(output_base, 'bpe.txt')
    tpe_output_file = os.path.join(output_base, 'tpe.txt')
    # un_normalized_output_file = os.path.join(output_base, 'unormalize.dict')

    # ori_token_writer = open(origin_token_output_file, 'w', encoding='UTF-8')
    # token_writer = open(token_output_file, 'w', encoding='UTF-8')
    # stmt_writer = open(stmt_output_file, 'w', encoding='UTF-8')
    # bpe_writer = open(bpe_output_file, 'w', encoding='UTF-8')
    tpe_writer = open(tpe_output_file, 'w', encoding='utf-8')
    start_time = time.time()
    print('开始获取所有训练用的方法对')
    gy_nonclones = get_gy_nonclones(config)
    type1, autogen_type3 = get_autogen(config)
    sources = ['gy', 'autogen', 'type1']
    all_pairs = []

    tag = '0'
    # 46;sample,Parser.java,5749,5759;sample,SelectorUtils.java,603,614
    for pair in gy_nonclones:
        pair = pair.strip()
        pair_info = pair.split(';')
        functionality = pair_info[0]
        functions = [pair_info[1], pair_info[2]]
        read_functions = []
        for function in functions:
            function_info = function.split(',')
            file_path = os.path.join(os.path.join(gy_nonclone_database, function_info[0]), function_info[1])
            function_start = function_info[2]
            function_end = function_info[3]
            f = load_function(file_path, function_start, function_end)
            read_functions.append(f)
        all_pairs.append(['<eof>'.join(read_functions), tag])

    tag = '3'
    for pair in autogen_type3:
        all_pairs.append([pair, tag])

    tag = '1'
    for function in type1:
        all_pairs.append(['<eof>'.join([function, function]), tag])
    print('方法对处理结束，共有 %d 对方法对，耗时 %.2f' % (len(all_pairs), time.time() - start_time))
    num_thread = 20
    # num_thread = 1
    # num_pairs = 15
    num_pairs = int(len(all_pairs) / num_thread) + 1
    res = []
    # for thread_no in range(2):
    pool = Pool(num_thread)
    for thread_no in range(num_thread):
        thread_no += 1
        start = (thread_no - 1) * num_pairs
        end = thread_no * num_pairs
        target_pairs = all_pairs[start:end]
        res.append(pool.apply_async(process_pairs, args=(thread_no, target_pairs, config, bpe)))
    pool.close()
    pool.join()
    print('多进程处理结束，开始写文件')
    total_lines = 0
    for s in res:
        (ori, token, stmt, bpe, num_statement) = s.get()
        total_lines += num_statement
        # ori_token_writer.write(''.join(ori))
        # token_writer.write(''.join(token))
        # stmt_writer.write(''.join(stmt))
        # bpe_writer.write(''.join(bpe))
        tpe_writer.write(''.join(bpe))
    #
    # ori_token_writer.close()
    # token_writer.close()
    # stmt_writer.close()
    # bpe_writer.close()
    tpe_writer.close()
    codes.close()
    print(total_lines / 30000)
    print('写文件结束，总计耗时 %.2f' % (time.time() - start_time))
