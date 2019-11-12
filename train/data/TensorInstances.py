import torch
from torch.autograd import Variable


class TensorInstances:
    def __init__(self, batch_size, slen, tlen):
        self.src_words = Variable(torch.LongTensor(batch_size, slen).zero_(), requires_grad=False)
        self.src_heads = [[[] for idx in range(slen)] for idy in range(batch_size)]
        self.src_childs = [[[] for idx in range(slen)] for idy in range(batch_size)]
        self.src_masks = Variable(torch.Tensor(batch_size, slen).zero_(), requires_grad=False)
        self.tgt_words = Variable(torch.LongTensor(batch_size, tlen).zero_(), requires_grad=False)
        self.tgt_heads = [[[] for idx in range(tlen)] for idy in range(batch_size)]
        self.tgt_childs = [[[] for idx in range(tlen)] for idy in range(batch_size)]
        self.tgt_masks = Variable(torch.Tensor(batch_size, tlen).zero_(), requires_grad=False)
        self.tags = Variable(torch.LongTensor(batch_size).zero_(), requires_grad=False)

    def to_cuda(self, device):
        self.src_words = self.src_words.cuda(device)
        self.src_masks = self.src_masks.cuda(device)
        self.tgt_words = self.tgt_words.cuda(device)
        self.tgt_masks = self.tgt_masks.cuda(device)
        self.tags = self.tags.cuda(device)

    @property
    def inputs(self):
        return (self.src_words, self.src_heads, self.src_childs, self.src_masks, \
                self.tgt_words, self.tgt_heads, self.tgt_childs, self.tgt_masks)

    @property
    def outputs(self):
        return self.tags
