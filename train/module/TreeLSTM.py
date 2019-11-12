from module.Common import *

class HTreeLSTM(nn.Module):

    """A module that runs multiple steps of LSTM."""

    def __init__(self, input_size, hidden_size, num_layers=1, batch_first=False, \
                 bidirectional=False, dropout_in=0, dropout_out=0):
        super(HTreeLSTM, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first
        self.bidirectional = bidirectional
        self.dropout_in = dropout_in
        self.dropout_out = dropout_out
        self.num_directions = 2 if bidirectional else 1

        self.fcells = []
        self.bcells = []
        for layer in range(num_layers):
            layer_input_size = input_size if layer == 0 else hidden_size * self.num_directions
            self.fcells.append(nn.LSTMCell(input_size=layer_input_size, hidden_size=hidden_size))
            if self.bidirectional:
                self.bcells.append(nn.LSTMCell(input_size=layer_input_size, hidden_size=hidden_size))

        self._all_weights = []
        for layer in range(num_layers):
            layer_params = (self.fcells[layer].weight_ih, self.fcells[layer].weight_hh, \
                            self.fcells[layer].bias_ih, self.fcells[layer].bias_hh)
            suffix = ''
            param_names = ['weight_ih_l{}{}', 'weight_hh_l{}{}']
            param_names += ['bias_ih_l{}{}', 'bias_hh_l{}{}']
            param_names = [x.format(layer, suffix) for x in param_names]
            for name, param in zip(param_names, layer_params):
                setattr(self, name, param)
            self._all_weights.append(param_names)

            if self.bidirectional:
                layer_params = (self.bcells[layer].weight_ih, self.bcells[layer].weight_hh, \
                                self.bcells[layer].bias_ih, self.bcells[layer].bias_hh)
                suffix = '_reverse'
                param_names = ['weight_ih_l{}{}', 'weight_hh_l{}{}']
                param_names += ['bias_ih_l{}{}', 'bias_hh_l{}{}']
                param_names = [x.format(layer, suffix) for x in param_names]
                for name, param in zip(param_names, layer_params):
                    setattr(self, name, param)
                self._all_weights.append(param_names)

        self.reset_parameters()

    def reset_parameters(self):
        for layer in range(self.num_layers):
            param_ih_name = 'weight_ih_l{}{}'.format(layer, '')
            param_hh_name = 'weight_hh_l{}{}'.format(layer, '')
            param_ih = self.__getattr__(param_ih_name)
            param_hh = self.__getattr__(param_hh_name)
            W = orthonormal_initializer(self.hidden_size, self.hidden_size + self.input_size)
            W_h, W_x = W[:, :self.hidden_size], W[:, self.hidden_size:]
            param_ih.data.copy_(torch.from_numpy(np.concatenate([W_x] * 4, 0)))
            param_hh.data.copy_(torch.from_numpy(np.concatenate([W_h] * 4, 0)))

            if self.bidirectional:
                param_ih_name = 'weight_ih_l{}{}'.format(layer, '_reverse')
                param_hh_name = 'weight_hh_l{}{}'.format(layer, '_reverse')
                param_ih = self.__getattr__(param_ih_name)
                param_hh = self.__getattr__(param_hh_name)
                W = orthonormal_initializer(self.hidden_size, self.hidden_size + self.input_size)
                W_h, W_x = W[:, :self.hidden_size], W[:, self.hidden_size:]
                param_ih.data.copy_(torch.from_numpy(np.concatenate([W_x] * 4, 0)))
                param_hh.data.copy_(torch.from_numpy(np.concatenate([W_h] * 4, 0)))

        for name, param in self.named_parameters():
            if "bias" in name:
                nn.init.constant_(self.__getattr__(name), 0)


    @staticmethod
    def _forward_rnn(cell, input, child, masks, initial, drop_masks):
        max_time = input.size(0)
        batch_size, hidden_size = initial[0].size()
        hiddens = [Variable(input.data.new(batch_size, hidden_size).zero_(), requires_grad=True)] * max_time
        cells = [Variable(input.data.new(batch_size, hidden_size).zero_(), requires_grad=True)] * max_time
        zeros = Variable(input.data.new(hidden_size).zero_(), requires_grad=False)
        hx = initial
        for time in range(max_time):
            hiddens[time], cells[time] = cell(input=input[time], hx=hx)
            hiddens[time] = hiddens[time]*masks[time] + initial[0]*(1-masks[time])
            cells[time] = cells[time]*masks[time] + initial[1]*(1-masks[time])
            if drop_masks is not None: hiddens[time] = hiddens[time] * drop_masks
            next_time = time + 1
            if next_time < max_time:
                avg_hidden, avg_cell = [], []
                for b in range(batch_size):
                    cur_childs = child[b][next_time]
                    child_count = len(cur_childs)
                    avgh, avgc = zeros, zeros
                    for chl in cur_childs:
                        avgh = avgh + hiddens[chl][b]/child_count
                        avgc = avgc + cells[chl][b]/child_count
                    avg_hidden.append(avgh)
                    avg_cell.append(avgc)
                avg_hidden = torch.stack(avg_hidden, 0)
                avg_cell = torch.stack(avg_cell, 0)
                hx = (avg_hidden, avg_cell)
            else:
                hx = (hiddens[time], cells[time])

        hiddens = torch.stack(hiddens, 0)
        return hiddens, hx

    @staticmethod
    def _forward_brnn(cell, input, head, masks, initial, drop_masks):
        max_time = input.size(0)
        batch_size, hidden_size = initial[0].size()
        hiddens = [Variable(input.data.new(batch_size, hidden_size).zero_(), requires_grad=True)] * max_time
        cells = [Variable(input.data.new(batch_size, hidden_size).zero_(), requires_grad=True)] * max_time
        zeros = Variable(input.data.new(hidden_size).zero_(), requires_grad=False)
        hx = initial
        for time in reversed(range(max_time)):
            hiddens[time], cells[time] = cell(input=input[time], hx=hx)
            hiddens[time] = hiddens[time]*masks[time] + initial[0]*(1-masks[time])
            cells[time] = cells[time]*masks[time] + initial[1]*(1-masks[time])
            if drop_masks is not None: hiddens[time] = hiddens[time] * drop_masks
            next_time = time - 1
            if next_time > 0:
                avg_hidden, avg_cell = [], []
                for b in range(batch_size):
                    cur_heads = head[b][next_time]
                    head_count = len(cur_heads)
                    avgh, avgc = zeros, zeros
                    for chl in cur_heads:
                        avgh = avgh + hiddens[chl][b]/head_count
                        avgc = avgc + cells[chl][b]/head_count
                    avg_hidden.append(avgh)
                    avg_cell.append(avgc)
                avg_hidden = torch.stack(avg_hidden, 0)
                avg_cell = torch.stack(avg_cell, 0)
                hx = (avg_hidden, avg_cell)
            else:
                hx = (hiddens[time], cells[time])

        hiddens = torch.stack(hiddens, 0)
        return hiddens, hx

    def forward(self, input, heads, childs, masks, initial=None):
        if self.batch_first:
            input = input.transpose(0, 1)
            masks = torch.unsqueeze(masks.transpose(0, 1), dim=2)
        max_time, batch_size, _ = input.size()
        masks = masks.expand(-1, -1, self.hidden_size)

        if initial is None:
            initial = Variable(input.data.new(batch_size, self.hidden_size).zero_())
            initial = (initial, initial)
        h_n = []
        c_n = []

        for layer in range(self.num_layers):
            max_time, batch_size, input_size = input.size()
            input_mask, hidden_mask = None, None
            if self.training:
                input_mask = input.data.new(batch_size, input_size).fill_(1 - self.dropout_in)
                input_mask = Variable(torch.bernoulli(input_mask), requires_grad=False)
                input_mask = input_mask / (1 - self.dropout_in)
                input_mask = torch.unsqueeze(input_mask, dim=2).expand(-1, -1, max_time).permute(2, 0, 1)
                input = input * input_mask

                hidden_mask = input.data.new(batch_size, self.hidden_size).fill_(1 - self.dropout_out)
                hidden_mask = Variable(torch.bernoulli(hidden_mask), requires_grad=False)
                hidden_mask = hidden_mask / (1 - self.dropout_out)

            layer_output, (layer_h_n, layer_c_n) = HTreeLSTM._forward_rnn(cell=self.fcells[layer], \
                input=input, child=childs, masks=masks, initial=initial, drop_masks=hidden_mask)
            if self.bidirectional:
                blayer_output, (blayer_h_n, blayer_c_n) = HTreeLSTM._forward_brnn(cell=self.bcells[layer], \
                    input=input, head=heads, masks=masks, initial=initial, drop_masks=hidden_mask)

            h_n.append(torch.cat([layer_h_n, blayer_h_n], 1) if self.bidirectional else layer_h_n)
            c_n.append(torch.cat([layer_c_n, blayer_c_n], 1) if self.bidirectional else layer_c_n)
            input = torch.cat([layer_output, blayer_output], 2) if self.bidirectional else layer_output

        h_n = torch.stack(h_n, 0)
        c_n = torch.stack(c_n, 0)

        return input, (h_n, c_n)
