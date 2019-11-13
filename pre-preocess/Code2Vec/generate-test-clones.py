import sys

sys.path.extend(["../../", "../", "./"])
import random
from configparser import ConfigParser
import time
from tqdm import *
from multiprocessing import *
from Normalizer import *
from RelationExtractor import *
from apply_bpe import *

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


def load_index_List(index_list_output):
    with open(index_list_output, 'r', encoding='UTF-8') as reader:
        content = reader.read()
    index_list = content.split(',')
    return index_list


def process_pairs(thread_no, config, clones, nonclones,bpe_processor):
    print('线程 %d 开始执行，共计 %d 条克隆和 %d 条非克隆数据' % (thread_no, len(clones), len(nonclones)))
    start_time = time.time()
    normalizer = Normalizer(config)
    preprocessor = PreProcessor()
    extractor = RelationExtractor(config)
    brace_cutter= BracesCutter()
    special_cutter = SpecialCharCutter(config)
    ori = []
    token = []
    bpe = []
    stmt = []
    for i in range(len(clones)):
        pair = clones[i]
        pairInfo = pair.split(';')
        tag = pairInfo[2]
        l_f = pairInfo[0]
        r_f = pairInfo[1]
        functions = [l_f, r_f]
        token_tokenized = ''
        stmt_tokenized = ''
        bpe_tokenized = ''
        ori_token = ''
        for function in functions:
            infos = function.split(',')
            start, end = infos[2], infos[3]
            f = ''
            with open(os.path.join(gy_clone_database, os.path.join(infos[0], infos[1])), 'r',
                      encoding='iso8859-1') as reader:
                i = 1
                for line in reader.readlines():
                    if int(start) <= i <= int(end):
                        f += line
                    i += 1
            f = extract_function_body(f)
            f = preprocessor.remove_comments(f)
            f4ori = f
            f = normalizer.normalize_literal_values(f)
            f = special_cutter.cut(f)
            f = brace_cutter.cut(f)
            # f = normalizer.line_as_word(f)
            # _, untokenized_dict, function_statement, function_token, stmt_node_list, token_node_list = extractor.extract(
            #     f)
            # function = re.sub('[ \n;]+', ' ', function)
            ori_node_children = ''
            ori_node_parent = ''
            stmt_node_children = ''
            stmt_node_parent = ''
            token_node_parent = ''
            token_node_children = ''
            bpe_node_children = ''
            bpe_node_parent = ''

            # for node in stmt_node_list:
            #     stmt_node_children += ','.join([str(c) for c in node.get_children()]) + ' '
            #     stmt_node_parent += ','.join([str(c) for c in node.get_parent()]) + ' '
            # for node in token_node_list:
            #     token_node_parent += ','.join([str(c) for c in node.get_children()]) + ' '
            #     token_node_children += ','.join([str(c) for c in node.get_parent()]) + ' '
            #
            # stmt_tokenized += function_statement + '\nc ' + stmt_node_children.strip() + '\nh ' + stmt_node_parent.strip() + '\n'
            # token_tokenized += function_token + '\nc ' + token_node_children.strip() + '\nh ' + token_node_parent.strip() + '\n'
            # ori_token += function + '\nc ' + ori_node_children.strip() + '\nh ' + ori_node_parent.strip() + '\n'
            _, _, function_bpe, _, bpe_node_list, _ = extractor.extract(f)
            # extractor.reset()
            function_bpe = bpe_processor.process_line(function_bpe)



            # file_operator = open(tmp_file1, 'w', encoding='UTF-8')
            # # file_operator.write(function_statement)
            # file_operator.write(f)
            # file_operator.close()
            # status = os.system('sh ~/apply_tpe-8000.sh ' + tmp_file1 + ' ' + tmp_file2)
            # file_operator = open(tmp_file2, 'r', encoding='UTF-8')
            # f = file_operator.read()
            # file_operator.close()
            # f = normalizer.unormalize(f, untokenized_dict, token_node_list)
            # if f != '':
            #
            #     for node in bpe_node_list:
            #         bpe_node_children += ','.join([str(c) for c in node.get_children()]) + ' '
            #         bpe_node_parent += ','.join([str(c) for c in node.get_parent()]) + ' '
            #     bpe_tokenized += function_bpe + '\nc ' + bpe_node_children.strip() + '\nh ' + bpe_node_parent.strip() + '\n'
            bpe_tokenized += re.sub(r'@@', '', function_bpe) + '\nc -1\nh -1\n'
            extractor.reset()
            #
            # ori_function, _, _, _, _, ori_token_node_list = extractor.extract(f4ori)
            # for node in ori_token_node_list:
            #     ori_node_parent += ','.join([str(c) for c in node.get_children()]) + ' '
            #     ori_node_children += ','.join([str(c) for c in node.get_parent()]) + ' '
            # ori_token += re.sub('[ \n;]+', ' ',
            #                     ori_function) + '\nc ' + ori_node_children.strip() + '\nh ' + ori_node_parent.strip() + '\n'
            # extractor.reset()
        token_tokenized += '3' + '\n'
        stmt_tokenized += '3' + '\n'
        ori_token += '3' + '\n'
        postfix = '\n'
        if bpe_tokenized != '':
            bpe_tokenized += '3' + '\n'
        ori.append(ori_token + postfix)
        token.append(token_tokenized + postfix)
        stmt.append(stmt_tokenized + postfix)
        bpe.append(bpe_tokenized + postfix)
    print('克隆对处理结束，耗时 %.2f s' % (time.time() - start_time))
    for i in range(len(nonclones)):
        pair = nonclones[i]
        pairInfo = pair.split(';')
        tag = '0'
        sub_base = pairInfo[0]
        l_f = pairInfo[1]
        r_f = pairInfo[2]
        functions = [l_f, r_f]
        ori_token = ''
        token_tokenized = ''
        stmt_tokenized = ''
        bpe_tokenized = ''
        for function in functions:
            infos = function.split(',')
            start, end = infos[2], infos[3]
            f = ''
            with open(os.path.join(os.path.join(gy_nonclone_database, sub_base), os.path.join(infos[0], infos[1])), 'r',
                      encoding='iso8859-1') as reader:
                i = 1
                for line in reader.readlines():
                    if int(start) <= i <= int(end):
                        f += line
                    i += 1
            f = extract_function_body(f)
            f = preprocessor.remove_comments(f)
            f4ori = f
            f = normalizer.normalize_literal_values(f)
            f = special_cutter.cut(f)
            f = brace_cutter.cut(f)
            # f = normalizer.line_as_word(f)
            # _, untokenized_dict, function_statement, function_token, stmt_node_list, token_node_list = extractor.extract(
            #     f)
            # function = re.sub(r'[ \n]+', ' ', function)
            ori_node_children = ''
            ori_node_parent = ''
            stmt_node_children = ''
            stmt_node_parent = ''
            token_node_parent = ''
            token_node_children = ''
            bpe_node_children = ''
            bpe_node_parent = ''

            # for node in stmt_node_list:
            #     stmt_node_children += ','.join([str(c) for c in node.get_children()]) + ' '
            #     stmt_node_parent += ','.join([str(c) for c in node.get_parent()]) + ' '
            # for node in token_node_list:
            #     token_node_parent += ','.join([str(c) for c in node.get_children()]) + ' '
            #     token_node_children += ','.join([str(c) for c in node.get_parent()]) + ' '
            #
            # stmt_tokenized += function_statement + '\nc ' + stmt_node_children.strip() + '\nh ' + stmt_node_parent.strip() + '\n'
            # token_tokenized += function_token + '\nc ' + token_node_children.strip() + '\nh ' + token_node_parent.strip() + '\n'
            # file_operator = open(tmp_file1, 'w', encoding='UTF-8')
            # file_operator.write(f)
            # file_operator.close()
            # status = os.system('sh ~/apply_tpe-8000.sh ' + tmp_file1 + ' ' + tmp_file2)
            # file_operator = open(tmp_file2, 'r', encoding='UTF-8')
            # f = file_operator.read()
            # file_operator.close()
            # f = normalizer.unormalize(f, untokenized_dict, token_node_list)
            # extractor.reset()
            #
            _, _, function_bpe, _, bpe_node_list, _ = extractor.extract(f)
            function_bpe = bpe_processor.process_line(function_bpe)
            #
            # for node in bpe_node_list:
            #     bpe_node_children += ','.join([str(c) for c in node.get_children()]) + ' '
            #     bpe_node_parent += ','.join([str(c) for c in node.get_parent()]) + ' '
            # bpe_tokenized += function_bpe + '\nc ' + bpe_node_children.strip() + '\nh ' + bpe_node_parent.strip() + '\n'
            bpe_tokenized += re.sub(r'@@', '', function_bpe) + '\nc -1\nh -1\n'
            # extractor.reset()

            # ori_function, _, _, _, _, ori_token_node_list = extractor.extract(f4ori)
            # for node in ori_token_node_list:
            #     ori_node_parent += ','.join([str(c) for c in node.get_children()]) + ' '
            #     ori_node_children += ','.join([str(c) for c in node.get_parent()]) + ' '
            # ori_token += re.sub('[ \n;]+', ' ',
            #                     ori_function) + '\nc ' + ori_node_children.strip() + '\nh ' + ori_node_parent.strip() + '\n'
            #
            # extractor.reset()
            # un_normalized_writer.write(
            #     ';'.join([str(k) + ',' + v for k, v in untokenized_dict.items()]) + '\n')
        token_tokenized += '0' + '\n'
        ori_token += '0' + '\n'
        stmt_tokenized += '0' + '\n'
        postfix = '\n'
        if bpe_tokenized != '':
            bpe_tokenized += '0' + '\n'

        ori.append(ori_token + postfix)
        token.append(token_tokenized + postfix)
        bpe.append(bpe_tokenized + postfix)
        stmt.append(stmt_tokenized + postfix)
    print('非克隆对处理结束，耗时 %.2f s' % (time.time() - start_time))
    return (ori, token, stmt, bpe)


if __name__ == "__main__":
    config = ConfigParser()
    config.read('config/myconfig.ini')

    random.seed(666)
    code_file = config.get('IO','TPE_CODE')
    print(code_file)
    codes = open(code_file, 'r', encoding='utf-8')
    gy_clone_database = os.path.join(config.get(section='IO', option='BCB_CODE_BASE'), '47')
    gy_nonclone_database = config.get('IO', 'BCB_CODE_BASE')

    gy_clone_file = config.get('IO', 'GY_TYPE3_INPUT')
    gy_nonclone_file = config.get('IO', 'GY_NONCLONES_INPUT')

    output_base = config.get('IO', 'TEST_OUTPUT_BASE')
    index_list_output = os.path.join(output_base, 'test_index.dict')
    pairs = []
    clones = []
    nonclones = []

    token_output_file = os.path.join(output_base, 'token.txt')
    stmt_output_file = os.path.join(output_base, 'stmt.txt')
    bpe_output_file = os.path.join(output_base, 'bpe.txt')
    tpe_output_file = os.path.join(output_base,'tpe.txt')
    un_normalized_output_file = os.path.join(output_base, 'unormalize.dict')
    ori_token_output_file = os.path.join(output_base, 'ori-token.txt')

    ori_token_writer = open(ori_token_output_file, 'w', encoding='UTF-8')
    token_writer = open(token_output_file, 'w', encoding='UTF-8')
    stmt_writer = open(stmt_output_file, 'w', encoding='UTF-8')
    bpe_writer = open(bpe_output_file, 'w', encoding='UTF-8')
    un_normalized_writer = open(un_normalized_output_file, 'w', encoding='UTF-8')
    tpe_writer = open(tpe_output_file,'w',encoding='utf-8')

    bpe = BPE(codes, -1, '@@', None, None)
    with open(gy_clone_file, 'r', encoding='UTF-8') as  reader:
        for line in reader.readlines():
            line = line.strip()
            if line != '':
                pairs.append(line)
    num_clones = len(pairs)
    with open(gy_nonclone_file, 'r', encoding='UTF-8') as  reader:
        for line in reader.readlines():
            line = line.strip()
            if line != '':
                pairs.append(line)
    index_list = []
    if os.path.exists(index_list_output):
        print('already a index-list file, reading...')
        index_list = load_index_List(index_list_output)
    else:
        print('no index-list file, generating')
        clone_indexes = random.sample(range(num_clones), 2000)
        nonclone_indexes = [x + num_clones for x in random.sample(range(len(pairs) - num_clones), 2000)]
        index_list.extend(clone_indexes)
        index_list.extend(nonclone_indexes)
        save_index_list(index_list, index_list_output)

    for index in index_list:
        index = int(index)
        if index >= num_clones:
            nonclones.append(pairs[index])
        else:
            clones.append(pairs[index])
    total_pairs = len(clones) + len(nonclones)
    print('Total %d pairs need to process' % (total_pairs))
    num_thread = 20
    num_pairs = int(total_pairs / num_thread) + 1
    # num_thread = 1
    # num_pairs =10
    pool = Pool(num_thread)
    results = []
    for thread_no in range(num_thread):
        thread_no += 1
        list_start = (thread_no - 1) * num_pairs
        list_end = (thread_no) * num_pairs
        target_clones = []
        target_nonclones = []
        num_clones = len(clones)
        if list_start >= num_clones:
            target_nonclones = nonclones[list_start - num_clones:list_end - num_clones]
            pass
        elif list_end < num_clones:
            target_clones = clones[list_start:list_end]
            pass
        else:
            target_clones = clones[list_start:]
            target_nonclones = nonclones[0:list_end - num_clones]
        print("线程 %d，预计处理 %d 条克隆和 %d条非克隆" % (thread_no, len(target_clones), len(target_nonclones)))
        r = pool.apply_async(process_pairs, (thread_no, config, target_clones, target_nonclones,bpe))
        results.append(r)
    pool.close()
    pool.join()

    for res in results:
        (ori, token, stmt, bpe) = res.get()
        ori_token_writer.write(''.join(ori))
        token_writer.write(''.join(token))
        stmt_writer.write(''.join(stmt))
        # bpe_writer.write(''.join(bpe))
        tpe_writer.write(''.join(bpe))

    ori_token_writer.close()
    token_writer.close()
    stmt_writer.close()
    un_normalized_writer.close()
    tpe_writer.close()
