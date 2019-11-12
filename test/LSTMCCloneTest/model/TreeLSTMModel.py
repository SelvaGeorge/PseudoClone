from module.TreeLSTM import *
from module.Attention import *
from module.CPUEmbedding import *

class TreeLSTMModel(nn.Module):
    def __init__(self, vocab, config, pretrained_embedding):
        super(TreeLSTMModel, self).__init__()
        self.config = config
        vocab_size, word_dims = pretrained_embedding.shape
        if vocab.vocab_size != vocab_size:
            print("word vocab size does not match, check word embedding file")
        self.word_embed = CPUEmbedding(vocab.vocab_size, word_dims, padding_idx=vocab.PAD)
        self.word_embed.weight.data.copy_(torch.from_numpy(pretrained_embedding))
        self.word_embed.weight.requires_grad = False

        self.lstm = HTreeLSTM(
            input_size=word_dims,
            hidden_size=config.lstm_hiddens,
            num_layers=config.lstm_layers,
            batch_first=True,
            bidirectional=True,
            dropout_in=config.dropout_lstm_input,
            dropout_out=config.dropout_lstm_hidden,
        )
        self.sent_dim = 2 * config.lstm_hiddens
        self.atten_guide = Parameter(torch.Tensor(self.sent_dim))
        self.atten_guide.data.normal_(0, 1)
        self.atten = LinearAttention(tensor_1_dim=self.sent_dim, tensor_2_dim=self.sent_dim)
        self.proj = NonLinear(self.sent_dim, vocab.tag_size)

    def forward(self, inputs):
        ##unpack inputs
        (src_words, src_heads, src_childs, src_masks, \
         tgt_words, tgt_heads, tgt_childs, tgt_masks) = inputs
        src_embed = self.word_embed(src_words)
        tgt_embed = self.word_embed(tgt_words)

        if self.training:
            src_embed = drop_input_independent(src_embed, self.config.dropout_emb)
            tgt_embed = drop_input_independent(tgt_embed, self.config.dropout_emb)

        batch_size = src_embed.size(0)
        atten_guide = torch.unsqueeze(self.atten_guide, dim=1).expand(-1, batch_size)
        atten_guide = atten_guide.transpose(1, 0)

        src_hiddens, src_state = self.lstm(src_embed, src_heads, src_childs, src_masks, None)
        src_hiddens = src_hiddens.transpose(1, 0)
        src_sent_probs = self.atten(atten_guide, src_hiddens, src_masks)
        batch_size, srclen, dim = src_hiddens.size()
        src_sent_probs = src_sent_probs.view(batch_size, srclen, -1)
        src_represents = src_hiddens * src_sent_probs
        src_represents = src_represents.sum(dim=1)

        tgt_hiddens, tgt_state = self.lstm(tgt_embed, tgt_heads, tgt_childs, tgt_masks, None)
        tgt_hiddens = tgt_hiddens.transpose(1, 0)
        tgt_sent_probs = self.atten(atten_guide, tgt_hiddens, tgt_masks)
        batch_size, tgtlen, dim = tgt_hiddens.size()
        tgt_sent_probs = tgt_sent_probs.view(batch_size, tgtlen, -1)
        tgt_represents = tgt_hiddens * tgt_sent_probs
        tgt_represents = tgt_represents.sum(dim=1)

        diff_hiddens = src_represents - tgt_represents
        hiddens = diff_hiddens * diff_hiddens
        outputs = self.proj(hiddens)
        return outputs

    def method(self, inputs):
        ##unpack inputs
        (words, heads, childs, masks) = inputs
        embed = self.word_embed(words)

        batch_size = embed.size(0)
        atten_guide = torch.unsqueeze(self.atten_guide, dim=1).expand(-1, batch_size)
        atten_guide = atten_guide.transpose(1, 0)

        hiddens, state = self.lstm(embed, heads, childs, masks, None)
        hiddens = hiddens.transpose(1, 0)
        sent_probs = self.atten(atten_guide, hiddens, masks)
        batch_size, length, dim = hiddens.size()
        sent_probs = sent_probs.view(batch_size, length, -1)
        sent_represents = hiddens * sent_probs
        sent_represents = sent_represents.sum(dim=1)

        return sent_represents

    def predict(self, src_represents, tgt_represents):
        diff_hiddens = src_represents - tgt_represents
        hiddens = diff_hiddens * diff_hiddens
        outputs = self.proj(hiddens)
        return outputs