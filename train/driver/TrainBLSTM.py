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
import pickle


def train(data, dev_data, test_data, clone_detection, vocab, config):
    optimizer = Optimizer(filter(lambda p: p.requires_grad, clone_detection.model.parameters()), config)

    global_step = 0
    best_acc = 0
    batch_num = int(np.ceil(len(data) / float(config.train_batch_size)))
    for iter in range(config.train_iters):
        start_time = time.time()
        print('Iteration: ' + str(iter) + ', total batch num: ' + str(batch_num))
        batch_iter = 0

        correct_num, total_num = 0, 0
        for onebatch in data_iter(data, config.train_batch_size, True):
            tinst = batch_data_variable(onebatch, vocab)

            # 设置模型为训练模式
            clone_detection.model.train()
            if clone_detection.use_cuda:
                tinst.to_cuda(clone_detection.device)

            clone_detection.forward(tinst.inputs)
            loss = clone_detection.compute_loss(tinst.outputs)
            loss = loss / config.update_every
            loss_value = loss.data.cpu().numpy()
            loss.backward()

            cur_correct, cur_count = clone_detection.compute_accuracy(tinst.outputs)
            correct_num += cur_correct
            total_num += cur_count
            acc = correct_num * 100.0 / total_num
            during_time = float(time.time() - start_time)
            print("Step:%d, ACC:%.2f, Iter:%d, batch:%d, time:%.2f, loss:%.2f" \
                  % (global_step, acc, iter, batch_iter, during_time, loss_value))

            batch_iter += 1
            if batch_iter % config.update_every == 0 or batch_iter == batch_num:
                nn.utils.clip_grad_norm_(filter(lambda p: p.requires_grad, clone_detection.model.parameters()), \
                                         max_norm=config.clip)
                optimizer.step()
                clone_detection.model.zero_grad()
                optimizer.zero_grad()
                global_step += 1

            if batch_iter % config.validate_every == 0 or batch_iter == batch_num:
                tag_correct, tag_total, dev_tag_acc = \
                    evaluate(dev_data, classifier, vocab, config.dev_file + '.' + str(global_step))
                print("Dev: acc = %d/%d = %.2f" % (tag_correct, tag_total, dev_tag_acc))

                # tag_correct, tag_total, test_tag_acc = \
                #     evaluate(test_data, classifier, vocab, config.test_file + '.' + str(global_step))
                # print("Test: acc = %d/%d = %.2f" % (tag_correct, tag_total, test_tag_acc))
                if dev_tag_acc > best_acc:
                    print("Exceed best acc: history = %.2f, current = %.2f" % (best_acc, dev_tag_acc))
                    best_acc = dev_tag_acc
                    if config.save_after > 0 and iter > config.save_after:
                        torch.save(clone_detection.model.state_dict(), config.save_model_path)


def evaluate(data, clone_detection, vocab, outputFile):
    start = time.time()
    clone_detection.model.eval()
    output = open(outputFile, 'w', encoding='utf-8')
    tag_correct, tag_total = 0, 0

    for onebatch in data_iter(data, config.test_batch_size, False):
        tinst = batch_data_variable(onebatch, vocab)
        if clone_detection.use_cuda:
            tinst.to_cuda(clone_detection.device)
        count = 0
        pred_tags = clone_detection.classifier(tinst.inputs)
        for inst, bmatch in batch_variable_inst(onebatch, pred_tags, vocab):
            printInstance(output, inst)
            tag_total += 1
            if bmatch: tag_correct += 1
            count += 1

    output.close()

    acc = tag_correct * 100.0 / tag_total

    end = time.time()
    during_time = float(end - start)
    print("sentence num: %d,  classifier time = %.2f " % (len(data), during_time))

    return tag_correct, tag_total, acc


class Optimizer:
    def __init__(self, parameter, config):
        self.optim = torch.optim.Adam(parameter, lr=config.learning_rate, betas=(config.beta_1, config.beta_2),
                                      eps=config.epsilon)
        decay, decay_step = config.decay, config.decay_steps
        l = lambda epoch: decay ** (epoch // decay_step)
        self.scheduler = torch.optim.lr_scheduler.LambdaLR(self.optim, lr_lambda=l)

    def step(self):
        self.optim.step()
        self.schedule()
        self.optim.zero_grad()

    def schedule(self):
        self.scheduler.step()

    def zero_grad(self):
        self.optim.zero_grad()

    @property
    def lr(self):
        return self.scheduler.get_lr()


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
    argparser.add_argument('--config_file', default='default.cfg')
    argparser.add_argument('--thread', default=1, type=int, help='thread num')
    argparser.add_argument('--gpu', default=-1, type=int, help='Use id of gpu, -1 if cpu.')

    args, extra_args = argparser.parse_known_args()
    config = Configurable(args.config_file, extra_args)
    torch.set_num_threads(args.thread)

    vocab = creatVocab(config.train_file)
    vec = vocab.load_pretrained_embs(config.pretrained_embeddings_file)
    pickle.dump(vocab, open(config.save_vocab_path, 'wb'))

    config.use_cuda = False
    if gpu and args.gpu != -1:
        config.use_cuda = True
        torch.cuda.set_device(args.gpu)
        print('GPU ID:' + str(args.gpu))
    print("\nGPU using status: ", config.use_cuda)
    # print(config.use_cuda)

    model = BiLSTMModel(vocab, config, vec)
    if config.use_cuda:
        # torch.backends.cudnn.enabled = True
        model = model.cuda(args.gpu)

    classifier = CloneDetection(model, vocab, config.use_cosine)

    data = read_corpus(config.train_file)
    dev_data = read_corpus(config.dev_file)
    # test_data = read_corpus(config.test_file)
    test_data = dev_data
    train(data, dev_data, test_data, classifier, vocab, config)
