import re, os
from collections import Counter
import argparse, time


# Token pair encoding


class TPE(object):
    def __init__(self):
        self.merge_dict = dict()
        self.end_tag = '</eow>'
        self.cmark = '$$'

    def clear(self):
        self.merge_dict.clear()

    def learn_bpe(self, learn_from_file, num_merge):
        print('start to learn ')
        self.merge_dict.clear()
        vocab = self.__process_raw_code(learn_from_file)
        for i in range(num_merge):
            pairs = self.__get_symbol_pairs(vocab)
            symbol_pair = max(pairs, key=pairs.get)
            self.merge_dict[self.cmark.join(symbol_pair)] = pairs[symbol_pair]
            vocab = self.__merge_symbols(symbol_pair, vocab)
            if i % 1000 == 0 and i !=0:
                print('%d / %d' %(i,num_merge))
        print('learn finished.')
        pass

    def apply_on_statement(self, statement):
        statement = re.sub(r'\$\$', ' ', statement)
        statement += ' ' + self.end_tag
        tokens = statement.split()
        new_tokens = []
        up_len = len(tokens)
        while up_len > 0:
            for i in range(up_len):
                piece = self.cmark.join(tokens[i:up_len])
                if piece in self.merge_dict or i == up_len - 1:
                    up_len = i
                    new_tokens.insert(0, piece)
                    break
        return new_tokens

    def __merge_symbols(self, symbol_pair, vocab):
        '''把vocabs中的所有单词中的'a b'字符串用'ab'替换
            Args:
                symbol_pair: (a, b) 两个符号
                vocab: 用subword(symbol)表示的单词，(word, count)。其中word使用subword空格分割
            Returns:
                vocab_new: 替换'a b'为'ab'的新词汇表
            '''
        vocab_new = {}
        raw = ' '.join(symbol_pair)
        merged = self.cmark.join(symbol_pair)
        bigram = re.escape(raw)
        p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
        for word, count in vocab.items():
            word_new = p.sub(merged, word)
            vocab_new[word_new] = count
        return vocab_new

    def __process_raw_code(self, file):
        words = Counter()
        vocab = {}
        with open(file, 'r', encoding='utf-8') as reader:
            for line in reader.readlines():
                line = line.strip()
                if line != '' and line is not None:
                    statements = line.split()
                    for statement in statements:
                        words[statement] += 1
        for statement, count in words.items():
            statement = re.sub(r'\$\$', ' ', statement)
            statement += ' ' + self.end_tag
            vocab[statement] = count
        return vocab
        pass

    def __get_symbol_pairs(self, vocab):
        ''' 获得词汇中所有的字符pair，连续长度为2，并统计出现次数
            Args:
                vocabs: 单词dict，(word, count)单词的出现次数。单词已经分割为最小的字符
            Returns:
                pairs: ((符号1, 符号2), count)
            '''
        pairs = dict()
        for word, freq in vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                p = (symbols[i], symbols[i + 1])
                pairs[p] = pairs.get(p, 0) + freq
        return pairs
        pass

    def __cut_special(function=''):
        tokens = []
        function = re.sub(r'[\t\r]', '', function)
        ori_tokens = function.split(' ')
        for ori_token in ori_tokens:
            if ori_token == '':
                continue
            else:
                last_cut = 0
                for iter in re.finditer(r'[-+\\*/%=<>!&\\|\\^~\\?:"\']{1,2}[>=]{0,1}', ori_token):
                    operator_start, operator_end = iter.span()
                    operator = iter.group()
                    if operator_start > last_cut:
                        tokens.append(ori_token[last_cut:operator_start])
                    tokens.append(operator)
                    last_cut = operator_end
                if last_cut < len(ori_token):
                    tokens.append(ori_token[last_cut:])
        return ' '.join(tokens)

    def __cut_brace(function='', if_keep_function_call=False):
        tokens = []
        last_cut = 0
        regx = r'[\(\){}\[\]\.;]'
        if if_keep_function_call:
            regx = r'[\(\){}\[\];]'
        for iter in re.finditer(regx, function):
            start, end = iter.span()
            if start > last_cut:
                tokens.append(function[last_cut:start])
            tokens.append(function[start: end])
            last_cut = end
        if last_cut < len(function):
            tokens.append(function[last_cut:])
        return ' '.join(tokens)

    # to remove all comments in a target string
    def __remove_comments(file_content=''):
        temp_line = ''
        is_in_double_quotes = False
        is_in_single_quote = False
        is_block_comment_opened = False
        lines = file_content.split('\n')
        string_after_process = ''

        for line in lines:
            line = line.strip()
            if line.startswith('//') or line == '':
                continue
            else:
                i = 0
                while i < len(line):
                    current_char = line[i]
                    if current_char == '"':
                        if is_in_double_quotes:
                            # If not a  \" that found, means close double quote.
                            if i - 1 >= 0 and line[i - 1] != '\\' and not is_block_comment_opened:
                                is_in_double_quotes = False
                        elif is_in_single_quote and not is_block_comment_opened:
                            # '"'
                            is_in_double_quotes = False
                        else:
                            # "asdfasfd.......(to be continued).
                            if not is_block_comment_opened:
                                is_in_double_quotes = True

                        if not is_block_comment_opened:
                            temp_line += current_char

                    elif current_char == '\'':
                        if is_in_double_quotes:
                            # "'"
                            is_in_single_quote = False

                            if not is_block_comment_opened:
                                temp_line += current_char
                                i += 1
                            continue
                        elif is_in_single_quote:
                            # '\''
                            if i - 1 >= 0 and line[i - 1] != '\\':
                                is_in_single_quote = False
                        else:
                            # already opened a single quote and not all situations above.
                            # To close an opened single quotes
                            is_in_single_quote = True

                        if not is_block_comment_opened:
                            temp_line += current_char
                    elif current_char == '/' and i + 1 in range(len(line)) and line[i + 1] == '/':
                        if is_in_double_quotes:
                            if not is_block_comment_opened:
                                temp_line += '//'
                            i += 1
                        else:
                            # if not in double quotes, means start writing comments, chars after that is useless.
                            break
                    elif current_char == '/' and i + 1 in range(len(line)) and line[i + 1] == '*':
                        # if not in a literal String, or in a block comment, means start one blockment.
                        if is_in_double_quotes or is_block_comment_opened:
                            # do nothing
                            pass
                        else:
                            is_block_comment_opened = True
                            i += 1
                    elif current_char == '*' and i + 1 in range(len(line)) and line[i + 1] == '/':
                        # no need to worry about something like this: ".....*/....."
                        if is_in_double_quotes:
                            pass
                        elif is_block_comment_opened:
                            is_block_comment_opened = False
                            i += 1
                    else:
                        if not is_block_comment_opened:
                            temp_line += current_char
                    i += 1
                if temp_line != '':
                    string_after_process += temp_line + '\n'
                temp_line = ''

        return string_after_process


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input file', required=True)
    parser.add_argument('--output', help='Output file', required=True)
    args = parser.parse_args()
    start = time.time()
    input_file = args.input
    output_file = args.output

    print(input_file)
    print(output_file)

    tpencoder = TPE()
    tpencoder.learn_bpe(input_file, num_merge=16000)
    end = time.time()
    print('learn finished, time %.2f' % (end - start))
    print(len(tpencoder.merge_dict))
    print(tpencoder.merge_dict)
    reader = open(input_file, 'r', encoding='utf-8')
    writer = open(output_file, 'w', encoding='utf-8')
    i = 0
    print('start to apply')
    for line in reader.readlines():
        line = line.strip()
        if line != '' and line is not None:
            statements = line.split()
            for i, statement in enumerate(statements):
                new_tokens = tpencoder.apply_on_statement(statement)
                writer.write(' '.join(new_tokens))
                if i != len(statements) - 1:
                    writer.write(' ')

            writer.write('\n')
        i += 1
        if i % 10000 == 0:
            print('%d lines fininshed.' % (i))

    reader.close()
    writer.close()
    end = time.time()
    print('end in %.2f' % (end - start))
