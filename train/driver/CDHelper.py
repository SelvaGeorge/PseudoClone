import torch.nn.functional as F
import torch.nn  as nn
import torch
from torch.autograd import Variable


class CloneDetection(object):
    def __init__(self, model, vocab, use_cosine):
        self.model = model
        self.vocab = vocab
        p = next(filter(lambda p: p.requires_grad, model.parameters()))
        self.use_cuda = p.is_cuda
        self.device = p.get_device() if self.use_cuda else None
        self.loss = nn.CosineEmbeddingLoss()
        self.use_cosine_loss = use_cosine

    def forward(self, inputs):
        # if self.use_cuda:
        #     xlen = len(inputs)
        #     for idx in range(xlen):
        #         inputs[idx] = inputs[idx].cuda(self.device)
        tag_logits, src_represents, tgt_represents = self.model(inputs)
        # cache
        self.tag_logits = tag_logits
        self.src_represents = src_represents
        self.tgt_represents = tgt_represents

    def compute_loss(self, true_tags):
        tmp_true = []
        if self.use_cosine_loss:
            for tag in true_tags:
                if tag == 0:
                    tmp_true.append(float(-1.0))
                else:
                    tmp_true.append(float(1.0))
            loss = self.loss(self.src_represents, self.tgt_represents, torch.Tensor(tmp_true).to(self.device))
        else:
            loss = F.cross_entropy(self.tag_logits, true_tags)
        return loss

    def compute_accuracy(self, true_tags):
        b, l = self.tag_logits.size()
        pred_tags = self.tag_logits.detach().max(1)[1].cpu()
        true_tags = true_tags.detach().cpu()
        tag_correct = pred_tags.eq(true_tags).cpu().sum()
        return tag_correct, b

    def classifier(self, inputs):
        if inputs[0] is not None:
            self.forward(inputs)
        pred_tags = self.tag_logits.detach().max(1)[1].cpu()
        return pred_tags
