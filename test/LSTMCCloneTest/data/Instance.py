import copy


class SInput:
    def __init__(self, words, heads, childs, key):
        self.words = copy.deepcopy(words)
        self.heads = copy.deepcopy(heads)
        self.childs = copy.deepcopy(childs)
        self.key = copy.deepcopy(key)


class Instance:
    def __init__(self, src_words, src_heads, src_childs, str_key, tgt_words, tgt_heads, tgt_childs, tgt_key, tag, type,
                 logits=None):
        self.src_words = src_words
        self.src_heads = src_heads
        self.src_childs = src_childs
        self.src_key = str_key
        self.tgt_words = tgt_words
        self.tgt_heads = tgt_heads
        self.tgt_childs = tgt_childs
        self.tgt_key = tgt_key
        self.tag = tag
        self.type = type
        self.tag_logits = logits
        self.tgt_rep = None
        self.src_rep = None

    def set_reps(self, src_rep, tgt_rep):
        self.src_rep = src_rep
        self.tgt_rep = tgt_rep

    @property
    def reps(self):
        return self.src_rep, self.tgt_rep

    def __str__(self):
        output = ''
        ## print source words
        # output = ' '.join(self.src_words) + '\nc'
        # src_len = len(self.src_words)
        # for idx in range(src_len):
        #     # TODO: change the add children logic when using only blstm
        #     # childs = self.src_childs[idx]
        #     childs = []
        #     child_len = len(childs)
        #     if child_len == 0:
        #         output = output + ' -1'
        #     else:
        #         output = output + ' ' + str(childs[0])
        #         for idz in range(1, child_len):
        #             output = output + ',' + str(childs[idz])
        # output = output + '\nh'
        # for idx in range(src_len):
        #     # heads = self.src_heads[idx]
        #     heads = []
        #     head_len = len(heads)
        #     if head_len == 0:
        #         output = output + ' -1'
        #     else:
        #         output = output + ' ' + str(heads[0])
        #         for idz in range(1, head_len):
        #             output = output + ',' + str(heads[idz])
        # output = output + '\n'
        # ## print target words
        # output = output + ' '.join(self.tgt_words) + '\nc'
        # tgt_len = len(self.tgt_words)
        # for idx in range(tgt_len):
        #     # childs = self.tgt_childs[idx]
        #     childs = []
        #     child_len = len(childs)
        #     if child_len == 0:
        #         output = output + ' -1'
        #     else:
        #         output = output + ' ' + str(childs[0])
        #         for idz in range(1, child_len):
        #             output = output + ',' + str(childs[idz])
        # output = output + '\nh'
        # for idx in range(tgt_len):
        #     heads = []
        #     # heads = self.tgt_heads[idx]
        #     head_len = len(heads)
        #     if head_len == 0:
        #         output = output + ' -1'
        #     else:
        #         output = output + ' ' + str(heads[0])
        #         for idz in range(1, head_len):
        #             output = output + ',' + str(heads[idz])
        # output = output + '\n'

        if self.tag == 'yes':
            if self.type == 0:
                # output = output + '10000' + '\t' + self.src_key + '\t' + self.tgt_key + '\t' + ' '.join(
                #     [str(x) for x in
                #      self.tag_logits.float().tolist()]) + '\t' + ' '.join(
                #     [str(s) for s in self.src_rep.tolist()]) + '\t' + ' '.join(
                #     [str(s) for s in self.tgt_rep.tolist()]) + '\n'
                output = output + '10000' + '\t' + self.src_key + '\t' + self.tgt_key + '\t' + ' '.join(
                    [str(x) for x in self.tag_logits.float().tolist()]) + '\n'
            # elif self.type == 6:
            #     pass
            else:
                output = output + str(
                    self.type) + '\t' + self.src_key + '\t' + self.tgt_key + '\t' + ' '.join(
                    [str(x) for x in self.tag_logits.float().tolist()]) + '\n'
        else:
            output = output + '0' + '\t' + self.src_key + '\t' + self.tgt_key + '\t' + ' '.join(
                [str(x) for x in self.tag_logits.float().tolist()]) + '\n'
        return output

    @property
    def src_len(self):
        return len(self.src_words)

    @property
    def tgt_len(self):
        return len(self.tgt_words)


def parseInstance(texts):
    if len(texts) != 7: return None
    max_len = 1000
    src_words, tgt_words = texts[0].strip().split(' '), texts[3].strip().split(' ')

    last_items = texts[6].strip().split(' ')
    type = int(last_items[0])
    tag = 'yes' if type > 0 else 'no'
    src_key, tgt_key = last_items[1], last_items[2]

    src_len, tgt_len = len(src_words), len(tgt_words)
    org_src_len, org_tgt_len = len(src_words), len(tgt_words)
    if src_len > max_len:
        src_words = src_words[:max_len]
        src_len = len(src_words)
    if tgt_len > max_len:
        tgt_words = tgt_words[:max_len]
        tgt_len = len(tgt_words)

    src_childs = []
    # childs = texts[1].strip().split(' ')
    # # if len(childs) != org_src_len + 1 or childs[0] != 'c':
    # #     print("Parse error: child length or child start mark")
    # for idx in range(src_len):
    #     wordchilds = childs[idx+1].strip().split(',')
    #     cur_childs = []
    #     for curchild in wordchilds:
    #         childid = int(curchild)
    #         if childid != -1 and childid < src_len: cur_childs.append(childid)
    #     src_childs.append(cur_childs)
    #
    src_heads = []
    # heads = texts[2].strip().split(' ')
    # # if len(heads) != org_src_len + 1 or heads[0] != 'h':
    # #     print("Parse error: head length or head start mark")
    # for idx in range(src_len):
    #     wordheads = heads[idx+1].strip().split(',')
    #     cur_heads = []
    #     for curhead in wordheads:
    #         headid = int(curhead)
    #         if headid != -1 and headid < src_len: cur_heads.append(headid)
    #     src_heads.append(cur_heads)
    #
    tgt_childs = []
    # childs = texts[4].strip().split(' ')
    # # if len(childs) != org_tgt_len + 1 or childs[0] != 'c':
    # #     print("Parse error: child length or child start mark")
    # for idx in range(tgt_len):
    #     wordchilds = childs[idx+1].strip().split(',')
    #     cur_childs = []
    #     for curchild in wordchilds:
    #         childid = int(curchild)
    #         if childid != -1 and childid < tgt_len: cur_childs.append(childid)
    #     tgt_childs.append(cur_childs)
    #
    tgt_heads = []
    # heads = texts[5].strip().split(' ')
    # if len(heads) != org_tgt_len + 1 or heads[0] != 'h':
    #     print("Parse error: head length or head start mark")
    # for idx in range(tgt_len):
    #     wordheads = heads[idx+1].strip().split(',')
    #     cur_heads = []
    #     for curhead in wordheads:
    #         headid = int(curhead)
    #         if headid != -1 and headid < tgt_len: cur_heads.append(headid)
    #     tgt_heads.append(cur_heads)

    return Instance(src_words, src_heads, src_childs, src_key, \
                    tgt_words, tgt_heads, tgt_childs, tgt_key, \
                    tag, type)


def writeInstance(filename, insts):
    with open(filename, 'w') as file:
        for inst in insts:
            file.write(str(inst) + '\n')


def printInstance(output, inst):
    string = str(inst)
    if string != '':
        output.write(str(inst) + '\n')
