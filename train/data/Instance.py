class Instance:
    def __init__(self, src_words, src_heads, src_childs, tgt_words, tgt_heads, tgt_childs, tag, type):
        self.src_words = src_words
        # self.src_heads = src_heads
        # self.src_childs = src_childs
        self.src_heads = []
        self.src_childs = []
        self.tgt_words = tgt_words
        # self.tgt_heads = tgt_heads
        # self.tgt_childs = tgt_childs
        self.tgt_heads = []
        self.tgt_childs = []
        self.tag = tag
        self.type = type

    def __str__(self):
        ## print source words
        output = ' '.join(self.src_words) + '\nc'
        src_len = len(self.src_words)
        # for idx in range(src_len):
        #     childs = self.src_childs[idx]
        #     child_len = len(childs)
        #     if child_len == 0:
        #         output = output + ' -1'
        #     else:
        #         output = output + ' ' + str(childs[0])
        #         for idz in range(1, child_len):
        #             output = output + ',' + str(childs[idz])
        output = output + '\nh'
        # for idx in range(src_len):
        #     heads = self.src_heads[idx]
        #     head_len = len(heads)
        #     if head_len == 0:
        #         output = output + ' -1'
        #     else:
        #         output = output + ' ' + str(heads[0])
        #         for idz in range(1, head_len):
        #             output = output + ',' + str(heads[idz])
        output = output + '\n'
        ## print target words
        output = output + ' '.join(self.tgt_words) + '\nc'
        # tgt_len = len(self.tgt_words)
        # for idx in range(tgt_len):
        #     childs = self.tgt_childs[idx]
        #     child_len = len(childs)
        #     if child_len == 0:
        #         output = output + ' -1'
        #     else:
        #         output = output + ' ' + str(childs[0])
        #         for idz in range(1, child_len):
        #             output = output + ',' + str(childs[idz])
        output = output + '\nh'
        # for idx in range(tgt_len):
        #     heads = self.tgt_heads[idx]
        #     head_len = len(heads)
        #     if head_len == 0:
        #         output = output + ' -1'
        #     else:
        #         output = output + ' ' + str(heads[0])
        #         for idz in range(1, head_len):
        #             output = output + ',' + str(heads[idz])
        output = output + '\n'
        if self.tag == 'yes':
            output = output + str(self.type) + '\n'
        else:
            output = output + '0\n'
        return output

    @property
    def src_len(self):
        return len(self.src_words)

    @property
    def tgt_len(self):
        return len(self.tgt_words)


def parseInstance(texts):
    if len(texts) != 7: return None
    src_words, tgt_words = texts[0].strip().split(' '), texts[3].strip().split(' ')
    type = int(texts[6].strip())
    tag = 'yes' if type > 0 else 'no'

    src_len, tgt_len = len(src_words), len(tgt_words)

    src_childs = []
    # childs = texts[1].strip().split(' ')
    # if len(childs) != src_len + 1 or childs[0] != 'c':
    #     print("Parse error: child length or child start mark")
    # for idx in range(src_len):
    #     wordchilds = childs[idx + 1].strip().split(',')
    #     cur_childs = []
    #     for curchild in wordchilds:
    #         childid = int(curchild)
    #         if childid != -1: cur_childs.append(childid)
    #     src_childs.append(cur_childs)

    src_heads = []
    # heads = texts[2].strip().split(' ')
    # if len(heads) != src_len + 1 or heads[0] != 'h':
    #     print("Parse error: head length or head start mark")
    # for idx in range(src_len):
    #     wordheads = heads[idx + 1].strip().split(',')
    #     cur_heads = []
    #     for curhead in wordheads:
    #         headid = int(curhead)
    #         if headid != -1: cur_heads.append(headid)
    #     src_heads.append(cur_heads)

    tgt_childs = []
    # childs = texts[4].strip().split(' ')
    # if len(childs) != tgt_len + 1 or childs[0] != 'c':
    #     print("Parse error: child length or child start mark")
    # for idx in range(tgt_len):
    #     wordchilds = childs[idx + 1].strip().split(',')
    #     cur_childs = []
    #     for curchild in wordchilds:
    #         childid = int(curchild)
    #         if childid != -1: cur_childs.append(childid)
    #     tgt_childs.append(cur_childs)

    tgt_heads = []
    # heads = texts[5].strip().split(' ')
    # if len(heads) != tgt_len + 1 or heads[0] != 'h':
    #     print("Parse error: head length or head start mark")
    # for idx in range(tgt_len):
    #     wordheads = heads[idx + 1].strip().split(',')
    #     cur_heads = []
    #     for curhead in wordheads:
    #         headid = int(curhead)
    #         if headid != -1: cur_heads.append(headid)
    #     tgt_heads.append(cur_heads)

    return Instance(src_words, src_heads, src_childs, tgt_words, tgt_heads, tgt_childs, tag, type)


def writeInstance(filename, insts):
    with open(filename, 'w') as file:
        for inst in insts:
            file.write(str(inst) + '\n')


def printInstance(output, inst):
    output.write(str(inst) + '\n')
