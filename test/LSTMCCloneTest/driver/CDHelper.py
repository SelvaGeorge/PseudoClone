import torch.nn.functional as F
from torch.autograd import Variable


class CloneDetection(object):
    def __init__(self, model, vocab, use_cosine):
        self.model = model
        self.vocab = vocab
        p = next(filter(lambda p: p.requires_grad, model.parameters()))
        self.use_cuda = p.is_cuda
        self.use_cosine = use_cosine
        self.device = p.get_device() if self.use_cuda else None

    def forward(self, inputs):
        method_vecs = self.model.method(inputs)
        # cache
        return method_vecs.detach().cpu()

    def classifier(self, src_represents, tgt_represents):
        if self.use_cuda:
            src_represents = src_represents.cuda(self.device)
            tgt_represents = tgt_represents.cuda(self.device)

        # 二维，分别表示 0型/非0型克隆的概率
        tag_logits = self.model.predict(src_represents, tgt_represents)
        # 通过数值对比获取判断的类型
        pred_tags = tag_logits.detach().max(1)[1].cpu()
        return pred_tags, tag_logits.detach().cpu()
