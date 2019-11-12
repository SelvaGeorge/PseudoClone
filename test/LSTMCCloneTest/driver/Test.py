import sys

sys.path.extend(["../../", "../", "./"])
import time
import torch.optim.lr_scheduler
import torch.nn as nn
import random
import argparse
from driver.Config import *
from model.BiLSTMModel import *
from model.TreeLSTMModel import *
from driver.CDHelper import *
from data.Dataloader import *
from collections import Counter
import pickle

def evaluate(in_file, clone_detection, vocab, output_file):
    start = time.time()
    clone_detection.model.eval()
    ###step 1
    method_represents = {}
    method_num = 0
    all_methods = buildSInputs(in_file)
    for onebatch in data_iter(all_methods, config.test_batch_size):
        tinst = batch_data_variable(onebatch, vocab)
        if clone_detection.use_cuda:
            tinst.to_cuda(clone_detection.device)
        method_vecs = clone_detection.forward(tinst.inputs)

        batch_size = len(onebatch)
        for idx in range(batch_size):
            method_represents[onebatch[idx].key] = method_vecs[idx]

        end = time.time()
        during_time = float(end - start)
        method_num += batch_size
        print("method num: %d,  representation time = %.2f " % (method_num, during_time))

    ###step 2
    start = time.time()
    pair_num = 0
    extended_batch = 100 * config.test_batch_size
    sent_dim = clone_detection.model.sent_dim
    correct_freq, gold_freq, predict_freq = Counter(), Counter(), Counter()
    tag_correct, tag_total = 0, 0

    data_in = codecs.open(in_file, encoding='utf8')
    output = open(output_file, 'w', encoding='utf-8')
    cur_batch = []
    while True:
        inst = read_one_instance(data_in)
        if inst is not None:
            cur_batch.append(inst)

        cur_batch_num = len(cur_batch)
        if (inst is None and cur_batch_num > 0) or  cur_batch_num == extended_batch:
            src_represents, tgt_represents = batch_paired_inputs(cur_batch, method_represents, sent_dim)
            pred_tags = clone_detection.classifier(src_represents, tgt_represents)

            for pred, gold, bmatch in batch_variable_inst(cur_batch, pred_tags, vocab):
                printInstance(output, pred)
                tag_total += 1
                gold_freq[gold.type] += 1

                if bmatch:
                    correct_freq[gold.type] += 1
                    predict_freq[gold.type] += 1
                    tag_correct += 1
                else:
                    pred_type = 3 if gold.type == 0 else 0
                    predict_freq[pred_type] += 1
            cur_batch = []

            end = time.time()
            during_time = float(end - start)
            pair_num += cur_batch_num
            print("processed pair num: %d,  classifier time = %.2f " % (pair_num, during_time))

        if inst is None: break

    data_in.close()
    output.close()

    acc = tag_correct * 100.0 / tag_total

    end = time.time()
    during_time = float(end - start)
    print("sentence num: %d,  classifier time = %.2f " % (tag_total, during_time))

    print("Total Acc = %d/%d = %.2f" % (tag_correct, tag_total, acc))

    for type, count in correct_freq.most_common():
        precision = count * 100.0 / predict_freq[type]
        recall = count * 100.0 / gold_freq[type]
        print("Type %d:  Prec = %d/%d = %.2f,  Recall = %d/%d = %.2f"
              % (type, count, predict_freq[type], precision, count, gold_freq[type], recall))

    return acc


if __name__ == '__main__':
    torch.manual_seed(666)
    torch.cuda.manual_seed(666)
    random.seed(666)
    np.random.seed(666)

    ### gpu
    gpu = torch.cuda.is_available()
    print("GPU available: ", gpu)
    print("CuDNN: \n", torch.backends.cudnn.enabled)

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--config_file', default='dev/config.cfg')
    argparser.add_argument('--thread', default=1, type=int, help='thread num')
    argparser.add_argument('--gpu', default=-1, type=int, help='Use id of gpu, -1 if cpu.')
    argparser.add_argument('--input', default='dev/dev.txt')
    argparser.add_argument('--output', default='dev/dev.txt.out')

    args, extra_args = argparser.parse_known_args()
    config = Configurable(args.config_file, extra_args)
    torch.set_num_threads(args.thread)

    vocab = pickle.load(open(config.load_vocab_path, 'rb+'))
    vec = vocab.create_placeholder_embs(config.pretrained_embeddings_file)

    config.use_cuda = False
    # if gpu and args.use_cuda:
    if gpu and args.gpu >= 0:
        config.use_cuda = True
        torch.cuda.set_device(args.gpu)
        print('GPU ID:' + str(args.gpu))


    model = TreeLSTMModel(vocab, config, vec)
    model.load_state_dict(torch.load(config.load_model_path, map_location=lambda storage, loc: storage))
    if config.use_cuda:
        # torch.backends.cudnn.enabled = True
        model = model.cuda(device=args.gpu)

    classifier = CloneDetection(model, vocab)
    evaluate(args.input, classifier, vocab, args.output)

