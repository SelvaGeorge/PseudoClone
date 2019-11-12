import re

from data.entity.Node import Node
from data.utils.DictReader import DictReader
from data.utils.Preprocessor import *


class RelationExtractor:
    def __init__(self, config):
        self.stmt_tree = Node(-1, 'root')
        self.token_tree = Node(-1, 'root')
        self.stmt_node_list = []
        self.stmt_lists = []
        self.token_node_list = []
        self.token_in_stmt_dict = {}
        self.token2token_dict = {}
        self.untokenized_dict = {}
        self.config = config
        self.java_keyword, self.imported_java, self.self_defined = DictReader(config).load()
        self.keep_dict = [x for x in self.java_keyword]
        self.keep_dict.extend(self.self_defined)
        self.operation_cutter = SpecialCharCutter(config=self.config)
        self.operator_dict = self.operation_cutter.get_dict()
        self.operator_dict.extend(['.', '{', '}', '(', ')', '[', ']'])

    def reset(self):
        self.stmt_node_list = []
        self.stmt_lists = []
        self.token_node_list = []
        self.token_in_stmt_dict = {}
        self.token2token_dict = {}
        self.untokenized_dict = {}

    # function string should remove comments and literal values first
    def extract(self, function=''):
        return_statements = []
        return_tokens = []
        function = SpecialCharCutter(self.config).cut(function)
        function = BracesCutter().cut(function)
        tmp = re.split(r'[;\n]', function)
        statements = []
        for statement in tmp:
            statement = statement.strip()
            if statement == '' or statement is None:
                pass
            else:
                statements.append(statement)
        last_stmt_index = 0
        total_tokens = 0
        for stmt_index in range(len(statements)):
            statement = statements[stmt_index]
            if statement == '':
                continue
            else:
                stmt_nodes = []
                normalized_tokens = []

                tokens = re.split(r'[ ]+', statement)

                stmt_node = Node(stmt_index, '')

                total_tokens += len(tokens)
                for token_index in range(len(tokens)):
                    token = tokens[token_index]
                    current_token_index = len(self.token_node_list)
                    if token == '':
                        continue
                    token_node = Node(current_token_index, content=token)
                    # 如果是保留字或者操作符、运算符、括号等
                    if token in self.keep_dict or token in self.operator_dict:
                        normalized_tokens.append(token)
                        pass
                    elif token in self.self_defined:
                        self.untokenized_dict[current_token_index] = token
                        normalized_tokens.append('Class')
                        pass
                    else:
                        # 这里就是标志符了，不区分函数调用和属性访问了
                        # if token in self.token_in_stmt_dict.keys():
                        #     # 如果之前这个identifier出现过，说明两个statement之间有连接关系
                        #     last_show_statement = self.token_in_stmt_dict[token]
                        #     if last_show_statement != stmt_index:
                        #         self.stmt_node_list[last_show_statement].add_parent(stmt_index)
                        #         self.token_in_stmt_dict[token] = stmt_index
                        #         stmt_node.add_child(last_show_statement)
                        #         pass
                        #     last_appear = self.token2token_dict[token]
                        #     # 如果在当前token之前出现？？？
                        #     if last_appear < current_token_index:
                        #         self.token_node_list[last_appear].add_parent(current_token_index)
                        #         token_node.add_child(last_appear)
                        #         self.token2token_dict[token] = current_token_index
                        #     pass
                        # # elif token in self.token2token_dict.keys():
                        #
                        # else:
                        #     # 如果之前这个identifier没有出现过，那么这次是新出现的标识符
                        #     self.token_in_stmt_dict[token] = stmt_index
                        #     self.token2token_dict[token] = current_token_index
                        #     pass

                        normalized_tokens.append('identifier')
                        token_node.set_content('identifier')
                        self.untokenized_dict[current_token_index] = token
                        pass
                    if current_token_index != 0:
                        token_node.add_child(current_token_index - 1)
                        self.token_node_list[current_token_index - 1].add_parent(current_token_index)
                    stmt_nodes.append(token_node)
                    self.token_node_list.append(token_node)

                self.stmt_lists.append([])
                stmt_node.set_content('$$'.join(normalized_tokens))
                if stmt_index != 0 and stmt_index != last_stmt_index:
                    self.stmt_node_list[last_stmt_index].add_parent(stmt_index)
                    stmt_node.add_child(last_stmt_index)

                last_stmt_index = stmt_index
                return_statements.append(stmt_node.get_content())
                return_tokens.extend(normalized_tokens)
                self.stmt_node_list.append(stmt_node)

        return function, self.untokenized_dict, ' '.join(return_statements), ' '.join(
            return_tokens), self.stmt_node_list, self.token_node_list
