from data.Vocab import *
from data.Instance import *
from data.TensorInstances import *
import codecs


def read_one_instance(data_in):
    curtext = []
    while True:
        line = data_in.readline().strip()
        if line is None or line == '':
            break
        curtext.append(line)

    length = len(curtext)
    if length == 7:
        return parseInstance(curtext)
    else:
        return None


def buildSInputs(testfile):
    input_keys = set()
    all_sinputs = []
    # data_in = codecs.open(testfile, encoding='utf8')
    data_in = open(testfile, 'r', encoding='utf-8')
    data_count = 0
    while True:
        inst = read_one_instance(data_in)
        if inst is None:
            break
        if inst.src_key not in input_keys:
            all_sinputs.append(SInput(inst.src_words, inst.src_heads, inst.src_childs, inst.src_key))
            input_keys.add(inst.src_key)
        if inst.tgt_key not in input_keys:
            all_sinputs.append(SInput(inst.tgt_words, inst.tgt_heads, inst.tgt_childs, inst.tgt_key))
            input_keys.add(inst.tgt_key)
        data_count += 1
        if data_count % 100000 == 0:
            print('Finished %d paired inputs. all function no %d ' % (data_count, len(all_sinputs)))

    data_in.close()
    print('Finished %d paired inputs.' % (data_count))
    ##sorted
    total_num = len(all_sinputs)
    print("Total method num: " + str(total_num))
    all_ids = sorted(range(total_num), key=lambda xid: len(all_sinputs[xid].words), reverse=True)
    sorted_sinputs = [all_sinputs[xid] for xid in all_ids]
    print("Sort method finished. ")

    return sorted_sinputs


def sinput_numberize(sinputs, vocab):
    for sinput in sinputs:
        yield sinput2id(sinput, vocab)


def sinput2id(sinput, vocab):
    wordids = vocab.word2id(sinput.words)
    return wordids, sinput


def batch_slice(data, batch_size):
    batch_num = int(np.ceil(len(data) / float(batch_size)))
    for i in range(batch_num):
        cur_batch_size = batch_size if i < batch_num - 1 else len(data) - batch_size * i
        insts = [data[i * batch_size + b] for b in range(cur_batch_size)]

        yield insts


def data_iter(data, batch_size):
    """
    randomly permute data, then sort by source length, and partition into batches
    ensure that the length of  insts in each batch
    """
    batched_data = []
    batched_data.extend(list(batch_slice(data, batch_size)))
    for batch in batched_data:
        yield batch


def batch_data_variable(batch, vocab):
    length = len(batch[0].words)
    batch_size = len(batch)
    for b in range(1, batch_size):
        cur_len = len(batch[b].words)
        if cur_len > length: length = cur_len

    tsinput = TensorSInput(batch_size, length)
    b = 0
    for wordids, sinput in sinput_numberize(batch, vocab):
        cur_len = len(sinput.words)
        for index in range(cur_len):
            tsinput.words[b, index] = wordids[index]
            tsinput.masks[b, index] = 1
            # tsinput.heads[b][index].extend(sinput.heads[index])
            # tsinput.childs[b][index].extend(sinput.childs[index])

        b += 1
    return tsinput


def batch_paired_inputs(batch, method_represents, hidden_dim):
    batch_size = len(batch)
    src_represents = Variable(torch.Tensor(batch_size, hidden_dim).zero_(), requires_grad=False)
    tgt_represents = Variable(torch.Tensor(batch_size, hidden_dim).zero_(), requires_grad=False)
    b = 0
    for inst in batch:
        src_represents[b] = src_represents[b] + method_represents[inst.src_key]
        tgt_represents[b] = tgt_represents[b] + method_represents[inst.tgt_key]

        b += 1

    return src_represents, tgt_represents


def batch_variable_inst(insts, tagids, vocab, tag_logits):
    for inst, tagid, tag_logits in zip(insts, tagids, tag_logits):
        pred_tag = vocab.id2tag(tagid)
        yield Instance(inst.src_words, inst.src_heads, inst.src_childs, inst.src_key, \
                       inst.tgt_words, inst.tgt_heads, inst.tgt_childs, inst.tgt_key, \
                       pred_tag, inst.type, tag_logits), inst, pred_tag == inst.tag
