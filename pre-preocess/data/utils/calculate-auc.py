from collections import Counter
import hashlib
from data.utils import *


def get_gold(clone, nonclone, seperator=','):
    clone_info_reader = open(clone, 'r', encoding='utf-8')
    nonclone_info_reader = open(nonclone, 'r', encoding='utf-8')
    pair2type = {}
    gold = Counter()
    num_repeated = 0
    flag = True
    for line in clone_info_reader.readlines():
        # 2;selected,1624067.java,222,257;sample,DownloadWebpage.java,55,67;6
        line = line.strip()
        info = line.split(';')
        tag = info[3]
        function_l = ','.join([info[0], info[1]])
        function_r = ','.join([info[0], info[2]])
        key = hashlib.md5(seperator.join([function_l, function_r]).encode('utf-8')).hexdigest()
        if flag:
            print(seperator.join([function_l, function_r]))
            flag = False
        if key in pair2type.keys():
            if tag != pair2type[key]:
                print('出现标注问题！')
                exit(-1)
            else:
                num_repeated += 1
        else:
            gold[tag] += 1
            pair2type[key] = tag

    clone_info_reader.close()

    for line in nonclone_info_reader.readlines():
        line = line.strip()
        # 2;selected,2235447.java,39,100;sample,DownloadWebpage.java,55,67
        info = line.split(';')

        if 'gy' in clone:
            key = hashlib.md5(seperator.join([info[0], info[1]]).encode('utf-8')).hexdigest()
        else:
            # key = hashlib.md5(seperator.join([info[1], info[2]]).encode('utf-8')).hexdigest()
            function_l = ','.join([info[0], info[1]])
            function_r = ','.join([info[0], info[2]])
            key = hashlib.md5(seperator.join([function_l, function_r]).encode('utf-8')).hexdigest()
        tag = '0'
        if key in pair2type.keys():
            if tag != pair2type[key]:
                print(seperator.join([info[0], info[1]]) + ' ' + tag + ' ' + pair2type[key])
                print('出现标注问题！')
                # exit(-1)
            else:
                num_repeated += 1
        else:
            pair2type[key] = tag
            gold[tag] += 1
    nonclone_info_reader.close()
    print('共读取到了 %d 对不同的克隆对和非克隆对信息' % (len(pair2type.keys())))
    return pair2type, gold


if __name__ == '__main__':
    corrected = Counter()
    # gold = Counter()

    clone_info_file = '/home/yanglin/LSTMTest/dataset/inputs/bcb/clones.out'
    nonclone_info_file = '/home/yanglin/Code2Vec/out/input/ori-non-clones.out'

    id2type,gold  = get_gold(clone_info_file, nonclone_info_file, seperator='\t')

    true = []
    false = []
    input_files = {
            # '1000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/bcb/1000/bpe.out',
            # '2000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/2000/bpe.out',
            # '4000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/4000/bpe.out',
            # '6000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/6000/bpe.out',
            # '8000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/8000/bpe.out',
            '10000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/10000/bpe.out',
            # '12000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/12000/bpe.out',
            # '14000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/14000/bpe.out',
            # '16000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/16000/bpe.out',
            # '20000': '/home/yanglin/LSTMTest/dataset/blstm/tpe/res/bcb/20000/bpe.out',
            # 'stmt': '/home/yanglin/LSTMTest/dataset/blstm/stmt/res/bcb/stmt.out',
            # 'token': '/home/yanglin/LSTMTest/dataset/blstm/token/res/bcb/token.out',
        }
    context = []
    for key, file in input_files.items():
        print(key)
        with open(file,'r',encoding='utf-8') as reader:
            for line in reader.readlines():
                line = line.strip()
                if line != '' and line is not None:
                    context.append(line)
                    pass
                elif line == '':
                    if len(context) == 7:
                        tmp = context[6].split('\t')
                        if len(tmp) == 4:
                            clone_type = tmp[0]
                            function_info = '\t'.join(tmp[1:3])
                            true_prob, false_prob = [float(s) for s in tmp[3].split(' ')]
                            id = hashlib.md5(function_info.encode('utf-8')).hexdigest()
                            if id in id2type:
                                if int(id2type[id]) > 0:
                                    true.append([function_info,true_prob,false_prob])
                                else:
                                    false.append([function_info,true_prob,false_prob])
                        pass
                    context.clear()
