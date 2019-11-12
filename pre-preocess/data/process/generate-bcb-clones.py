import sys, os, hashlib

sys.path.extend(["../../", "../", "./"])
from configparser import ConfigParser
import time

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config/gpu-config.ini')

    experiment_base = config.get('IO', 'EXPERIMENT_OUT_BASE')
    bcb_clones_input = config.get('IO', 'BCB_CLONES_INPUT')
    bcb_nonclones_input = config.get('IO', 'BCB_NONCLONES_INPUT')

    function_input_base = os.path.join(experiment_base, 'functions')
    function_info_file = os.path.join(function_input_base, 'function-info.txt')
    bpe_functions_file = os.path.join(function_input_base, 'bpe.txt')
    stmt_functions_file = os.path.join(function_input_base, 'stmt.txt')
    token_functions_file = os.path.join(function_input_base, 'token.txt')
    ori_functions_file = os.path.join(function_input_base, 'ori.txt')

    clones_output_base = os.path.join(experiment_base, 'clones')
    output4bpe = os.path.join(clones_output_base, 'new-6000')
    bpe_clones_output_file = os.path.join(output4bpe, 'bpe.txt')
    stmt_clones_output_file = os.path.join(clones_output_base, 'stmt.txt')
    token_clones_output_file = os.path.join(clones_output_base, 'token.txt')
    ori_clones_output_file = os.path.join(clones_output_base, 'ori.txt')

    bpe_writer = open(bpe_clones_output_file, 'w', encoding='UTF-8')
    stmt_writer = open(stmt_clones_output_file, 'w', encoding='UTF-8')
    token_writer = open(token_clones_output_file, 'w', encoding='UTF-8')
    ori_writer = open(ori_clones_output_file, 'w', encoding='UTF-8')

    id2function = {}
    function2id = {}
    id2bpe = {}
    id2token = {}
    id2stmt = {}
    id2ori = {}
    start_time = time.time()
    print('开始读取BCB克隆和非克隆文件')
    pairs_info = []
    with open(bcb_clones_input, 'r', encoding='UTF-8') as reader:
        for line in reader.readlines():
            line = line.strip()
            pairs_info.append(line)
    num_clones = len(pairs_info)
    with open(bcb_nonclones_input, 'r', encoding='UTF-8') as reader:
        for line in reader.readlines():
            line = line.strip()
            pairs_info.append(line + ';0')
    print('读取结束，共有 %d 对函数信息，耗时 %.2f' % (len(pairs_info), time.time() - start_time))

    start_time = time.time()
    print('开始读取预处理的函数信息')
    with open(stmt_functions_file, 'r', encoding='UTF-8') as reader:
        context = []
        i = 0
        for line in reader.readlines():
            line = line.strip()
            if line == '':
                if len(context) == 4:
                    id2stmt[i] = '\n'.join(context[:3])
                    function_info = context[3]
                    id2function[i] = function_info
                    key = hashlib.md5(function_info.encode('utf-8')).hexdigest()
                    function2id[key] = i
                    i += 1
                else:
                    if len(context) == 0:
                        context.append('')
                        continue
                context.clear()
            else:
                context.append(line)
    with open(token_functions_file, 'r', encoding='UTF-8') as reader:
        context = []
        for line in reader.readlines():
            line = line.strip()
            if line == '':
                if len(context) == 4:
                    function_info = context[3]
                    key = hashlib.md5(function_info.encode('utf-8')).hexdigest()
                    if key in function2id.keys():
                        id = function2id[key]
                        recorded_info = id2function[id]
                        if recorded_info != function_info:
                            print('出现记录不匹配的情况，src %s , tgt %s ' % (recorded_info, function_info))
                            exit(-1)
                        else:
                            id2token[id] = '\n'.join(context[0:3])
                    else:
                        print('出现没有被记录的函数的情况，函数信息为 %s' % (function_info))
                else:
                    if len(context) == 0:
                        context.append('')
                        continue
                context.clear()
            else:
                context.append(line)
    with open(bpe_functions_file, 'r', encoding='UTF-8') as reader:
        context = []
        i = 0
        for line in reader.readlines():
            line = line.strip()
            if line == '':
                if len(context) == 4:
                    id2bpe[i] = '\n'.join(context[0:3])
                    function_info = context[3]
                    id2function[i] = function_info
                    key = hashlib.md5(function_info.encode('utf-8')).hexdigest()
                    function2id[key] = i
                    i += 1
                    # if key in function2id.keys():
                    #     id = function2id[key]
                    #     recorded_info = id2function[id]
                    #     if recorded_info != function_info:
                    #         print('出现记录不匹配的情况，src %s , tgt %s ' % (recorded_info, function_info))
                    #         exit(-1)
                    #     else:
                    #         id2function[i] = function_info
                    #         key = hashlib.md5(function_info.encode('utf-8')).hexdigest()
                    #         function2id[key] = i
                    #         i += 1
                    #         id2bpe[id] = '\n'.join(context[0:3])
                    # else:
                    #     print('出现没有被记录的函数的情况，函数信息为 %s' % (function_info))
                else:
                    if len(context) == 0:
                        context.append('')
                        continue
                context.clear()
            else:
                context.append(line)
    with open(ori_functions_file, 'r', encoding='UTF-8') as reader:
        context = []
        for line in reader.readlines():
            line = line.strip()
            if line == '':
                if len(context) == 4:
                    function_info = context[3]
                    key = hashlib.md5(function_info.encode('utf-8')).hexdigest()
                    if key in function2id.keys():
                        id = function2id[key]
                        recorded_info = id2function[id]
                        if recorded_info != function_info:
                            print('出现记录不匹配的情况，src %s , tgt %s ' % (recorded_info, function_info))
                            exit(-1)
                        else:
                            id2ori[id] = '\n'.join(context[0:3])
                    else:
                        print('出现没有被记录的函数的情况，函数信息为 %s' % (function_info))
                else:
                    if len(context) == 0:
                        context.append('')
                        continue
                context.clear()
            else:
                context.append(line)

    print('共有%d个函数， %d 条statement信息，%d 条token信息，%d 条bpe信息，%d 条ori信息，读取耗时 %.2f'
          % (
              len(id2function.keys()), len(id2stmt.keys()), len(id2token.keys()), len(id2bpe.keys()),
              len(id2ori.keys()), time.time() - start_time))

    bpe_added = 0
    token_added = 0
    stmt_added = 0
    ori_added = 0
    start_time = time.time()
    print('开始组装克隆对')
    for i in range(len(pairs_info)):
        # for i in range(5):
        pair = pairs_info[i]
        # 2;sample,DownloadWebpage.java,32,53;sample,DownloadWebpage.java,55,67;4
        infos = pair.split(';')
        functions = [infos[0] + ',' + infos[1], infos[0] + ',' + infos[2]]

        bpe_output_blocks = []
        stmt_output_blocks = []
        token_output_blocks = []
        ori_output_blocks = []

        for function in functions:
            key = hashlib.md5(function.encode('utf-8')).hexdigest()
            if key in function2id.keys():
                id = function2id[key]
                if id in id2bpe:
                    current_block = id2bpe[id].strip()
                    if current_block == '' or current_block.startswith('c'):
                        pass
                    else:
                        bpe_output_blocks.append(current_block)
                if id in id2token:
                    current_block = id2token[id].strip()
                    if current_block == '' or current_block.startswith('c'):
                        pass
                    else:
                        token_output_blocks.append(current_block)
                if id in id2stmt:
                    current_block = id2stmt[id].strip()
                    if current_block == '' or current_block.startswith('c'):
                        pass
                    else:
                        stmt_output_blocks.append(current_block)
                if id in id2ori:
                    current_block = id2ori[id].strip()
                    if current_block == '' or current_block.startswith('c'):
                        pass
                    else:
                        ori_output_blocks.append(current_block)

        tag = ' '.join([infos[3], functions[0], functions[1]]) + '\n'
        if len(bpe_output_blocks) == 2:
            bpe_added += 1
            bpe_output_blocks.append(tag)
            bpe_writer.write('\n'.join(bpe_output_blocks) + '\n')

        if len(token_output_blocks) == 2:
            token_added += 1
            token_output_blocks.append(tag)
            token_writer.write('\n'.join(token_output_blocks) + '\n')

        if len(stmt_output_blocks) == 2:
            stmt_added += 1
            stmt_output_blocks.append(tag)
            stmt_writer.write('\n'.join(stmt_output_blocks) + '\n')
        if len(ori_output_blocks) == 2:
            ori_added += 1
            ori_output_blocks.append(tag)
            ori_writer.write('\n'.join(ori_output_blocks) + '\n')

        if i % 100000 == 0 and i != 0:
            print(
                '构建进度 %d / %d = %.2f , 耗时 %.2f ' % (i, len(pairs_info), i / len(pairs_info), time.time() - start_time))
    print('构建了 %d 条statement信息，%d 条token信息，%d 条bpe信息，%d 条ori信息,总计耗时 %.2f' %
          (stmt_added, token_added, bpe_added, ori_added, time.time() - start_time))

    bpe_writer.close()
    stmt_writer.close()
    token_writer.close()
    ori_writer.close()
