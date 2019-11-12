from data.Vocab import *
from data.Instance import *
from data.TensorInstances import *
from collections import Counter
import codecs

def read_corpus(file):
    data = []
    with codecs.open(file, encoding='utf8') as input_file:
        curtext = []
        for line in input_file.readlines():
            line = line.strip()
            if line is not None and line != '':
                curtext.append(line)
            else:
                slen = len(curtext)
                if slen == 7:
                    cur_data = parseInstance(curtext)
                    if cur_data.src_len <= 500 and cur_data.tgt_len <=500:
                        data.append(cur_data)
                curtext = []

    slen = len(curtext)
    if slen == 7:
        cur_data = parseInstance(curtext)
        if cur_data.src_len <= 500 and cur_data.tgt_len <= 500:
            data.append(cur_data)

    print("Total num: " + str(len(data)))
    return data

def creatVocab(corpusFile):
    tag_counter = Counter()
    alldatas = read_corpus(corpusFile)
    for inst in alldatas:
        tag_counter[inst.tag] += 1

    return Vocab(tag_counter)

def insts_numberize(insts, vocab):
    for inst in insts:
        yield inst2id(inst, vocab)

def inst2id(inst, vocab):
    srcids = vocab.word2id(inst.src_words)
    tgtids = vocab.word2id(inst.tgt_words)
    tagid = vocab.tag2id(inst.tag)

    return srcids, tgtids, tagid, inst


def batch_slice(data, batch_size):
    batch_num = int(np.ceil(len(data) / float(batch_size)))
    for i in range(batch_num):
        cur_batch_size = batch_size if i < batch_num - 1 else len(data) - batch_size * i
        insts = [data[i * batch_size + b] for b in range(cur_batch_size)]

        yield insts


def data_iter(data, batch_size, shuffle=True):
    """
    randomly permute data, then sort by source length, and partition into batches
    ensure that the length of  insts in each batch
    """

    batched_data = []
    if shuffle: np.random.shuffle(data)
    batched_data.extend(list(batch_slice(data, batch_size)))

    if shuffle: np.random.shuffle(batched_data)
    for batch in batched_data:
        yield batch


def batch_data_variable(batch, vocab):
    slen, tlen = len(batch[0].src_words), len(batch[0].tgt_words)
    batch_size = len(batch)
    for b in range(1, batch_size):
        cur_slen, cur_tlen = len(batch[b].src_words), len(batch[b].tgt_words)
        if cur_slen > slen: slen = cur_slen
        if cur_tlen > tlen: tlen = cur_tlen

    tinst = TensorInstances(batch_size, slen, tlen)

    b = 0
    for srcids, tgtids, tagid, inst in insts_numberize(batch, vocab):
        tinst.tags[b] = tagid
        cur_slen, cur_tlen = len(inst.src_words), len(inst.tgt_words)
        for index in range(cur_slen):
            tinst.src_words[b, index] = srcids[index]
            tinst.src_masks[b, index] = 1
            # tinst.src_heads[b][index].extend(inst.src_heads[index])
            # tinst.src_childs[b][index].extend(inst.src_childs[index])

        for index in range(cur_tlen):
            tinst.tgt_words[b, index] = tgtids[index]
            tinst.tgt_masks[b, index] = 1
            # tinst.tgt_heads[b][index].extend(inst.tgt_heads[index])
            # tinst.tgt_childs[b][index].extend(inst.tgt_childs[index])
        
        b += 1
    return tinst

def batch_variable_inst(insts, tagids, vocab):
    for inst, tagid in zip(insts, tagids):
        pred_tag = vocab.id2tag(tagid)
        yield Instance(inst.src_words, inst.src_heads, inst.src_childs, \
                       inst.tgt_words, inst.tgt_heads, inst.tgt_childs, \
                       pred_tag, inst.type), pred_tag == inst.tag


import argparse
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--input', default='dataset/train.tclone.txt')
    argparser.add_argument('--output', default='dataset/random.vec')
    argparser.add_argument('--dim', default=200, type=int, help='vec dim.')
    args, extra_args = argparser.parse_known_args()

    insts = read_corpus(args.input)
    word_counter = Counter()
    for inst in insts:
        for curword in inst.src_words:
            word_counter[curword] += 1
        for curword in inst.tgt_words:
            word_counter[curword] += 1
    word_size = len(word_counter)
    embeddings = np.random.randn(word_size, args.dim)
    output = open(args.output, 'w', encoding='utf-8')
    index = 0
    for curword, count in word_counter.most_common():
        outvalues = [curword]
        for curvalue in embeddings[index]:
            outvalues.append(str(curvalue))
        output.write(' '.join(outvalues) + '\n')
    output.close()
