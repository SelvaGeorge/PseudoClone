from collections import Counter
import re, sys, os
from data.utils.DictReader import DictReader


class Normalizer:
    normalized_identifiers = Counter()
    function_name2token = {}
    class_name2token = {}
    attribute_name2token = {}
    identifier2token = {}

    string_counter = Counter()
    char_counter = Counter()
    number_counter = Counter()
    float_counter = Counter()
    hex_counter = Counter()

    def __init__(self, config):
        self.config = config
        self.dict_reader = DictReader(self.config)
        self.java_keyword, self.imported_java_class, self.self_defined_class = self.dict_reader.load()

        # f_n2token_file = config.get(section='MIDDLE', option='FUNCTION_NAME2TOKEN')
        # # TODO: Fix class name normalizer
        # # c_n2token_file = config.get(section='MIDDLE', option='CLASS_NAME2TOKEN')
        # a_n2token_file = config.get(section='MIDDLE', option='ATTRIBUTE_NAME2TOKEN')
        # i2token_file = config.get(section='MIDDLE', option='IDENTIFIER2TOKEN')

        # self.function_name2token = self.read_dict(f_n2token_file)
        # # self.class_name2token = self.read_dict(c_n2token_file)
        # self.attribute_name2token = self.read_dict(a_n2token_file)
        # self.identifier2token = self.read_dict(i2token_file)

        # self.extends_dict = True
        # if self.config.get(section='TOKENIZE', option='IF_EXTEND_DICT') == '0':
        #     self.extends_dict = False

    def read_dict(self, file_path):
        dict = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='UTF-8') as reader:
                for line in reader.readlines():
                    line = line.strip()
                    if line != '':
                        k_v = line.split(' ')
                        dict[k_v[0]] = k_v[1]
        return dict

    def normalize_class_names(self, file_content=''):
        if file_content != '':
            after_normalize = []
            file_content = file_content.replace('\t', ' ')
            terms = file_content.split(' ')
            for term in terms:
                last_cut = 0
                if term == '':
                    continue
                token = ''
                if term in self.java_keyword or term in self.imported_java_class:
                    token = term
                    pass
                elif term in self.self_defined_class:
                    # token = self.get_class_name_token(term)
                    token = 'Class'
                    pass
                else:
                    for iter in re.finditer(r'[a-zA-Z0-9_]+', term):
                        start, end = iter.span()
                        sub_term = iter.group()

                        # first add the chars between two cuts.
                        if start > last_cut:
                            token += term[last_cut:start]
                            pass
                        if sub_term in self.imported_java_class or sub_term in self.java_keyword or sub_term.startswith(
                                "FunctionCall") or sub_term.startswith(
                            'Attribute') or sub_term.startswith('Literal'):
                            token += sub_term
                            pass
                        elif sub_term in self.self_defined_class:
                            # token += self.get_class_name_token(term)
                            token += 'Class'
                            pass
                        else:
                            # if not sub_term in self.identifier2token:
                            #     if self.extends_dict:
                            #         tmp = 'Identifier' + str(
                            #             len(self.identifier2token))
                            #         self.identifier2token[sub_term] = tmp
                            #         pass
                            #     else:
                            #         tmp = ' <unk> '
                            #     pass
                            # else:
                            #     tmp = self.identifier2token[sub_term]
                            # token += tmp
                            token += 'identifier'
                        last_cut = end
                    if last_cut <= len(term):
                        token += term[last_cut:]

                after_normalize.append(token)
            return ' '.join(after_normalize)
        else:
            return ''

    # def get_class_name_token(self, term):
    #     if term in self.class_name2token:
    #         tmp_token = self.class_name2token[term]
    #     else:
    #         if self.extends_dict:
    #             tmp_token = 'Class' + str(len(self.class_name2token))
    #             self.class_name2token[term] = tmp_token
    #         else:
    #             tmp_token = ' <unk> '
    #     return tmp_token

    def normalize_literal_values(self, file_content=''):
        file_content = self.remove_string(file_content)
        file_content = self.remove_char(file_content)
        file_content = self.remove_floats(file_content)
        file_content = self.remove_number(file_content)
        # file_content = self.line_as_word(file_content)
        return file_content

    def normalize_function_calls(self, file_content=''):
        return_string = ''
        last_cut = 0
        fc_iter = re.finditer(r'\.[a-zA-Z0-9_]+\(', file_content)
        has_function_call = True
        try:
            fc_matcher = next(fc_iter)
        except StopIteration:
            # Means that there's no function calls.
            has_function_call = False
            pass

        for aa_matcher in re.finditer(r'\.[a-zA-Z0-9_]+', file_content):
            aa_start, aa_end = aa_matcher.span()
            try:
                if has_function_call:
                    fc_start, fc_end = fc_matcher.span()

                    if fc_start == aa_start and fc_end - aa_end == 1:
                        # This is actually a function call
                        function_name = file_content[fc_start:fc_end]
                        string_before = file_content[last_cut:fc_start]
                        current_token = '.functionCall('
                        # if function_name in self.function_name2token:
                        #     current_token = self.function_name2token[function_name]
                        #     pass
                        # else:
                        #     if self.extends_dict:
                        #         current_token = '.FunctionCall' + str(len(self.function_name2token)) + '('
                        #         self.function_name2token[function_name] = current_token
                        #     else:
                        #         current_token = ' <unk> '
                        #     pass
                        return_string += string_before + current_token
                        last_cut = fc_end
                        fc_matcher = next(fc_iter)

                    else:
                        # Function call start and end does not match, this is an attribute access
                        attribute = file_content[aa_start:aa_end]
                        string_before = file_content[last_cut:aa_start]

                        token_body = attribute[1:]
                        if token_body in self.java_keyword:
                            tmp_token = attribute
                            pass
                        else:
                            tmp_token = '.attribute'
                        # elif attribute in self.attribute_name2token:
                        #     tmp_token = self.attribute_name2token[attribute]
                        #     pass
                        # else:
                        #     if self.extends_dict:
                        #         tmp_token = '.Attribute' + str(len(self.attribute_name2token))
                        #         self.attribute_name2token[attribute] = tmp_token
                        #     else:
                        #         tmp_token = ' <unk> '
                        #     pass
                        return_string += string_before + tmp_token
                        last_cut = aa_end

                else:
                    # if there's no more function calls, all rest are attribute access.
                    attribute = file_content[aa_start:aa_end]
                    tmp_token = '.attribute'
                    # if not attribute in self.attribute_name2token:
                    #     if self.extends_dict:
                    #         tmp_token = '.Attribute' + str(len(self.attribute_name2token))
                    #         self.attribute_name2token[attribute] = tmp_token
                    #         pass
                    #     else:
                    #         tmp_token = ' <unk> '
                    # else:
                    #     tmp_token = self.attribute_name2token[attribute]
                    #     pass
                    string_before = file_content[last_cut:aa_start]
                    return_string += string_before + tmp_token
                    last_cut = aa_end

            except StopIteration:
                has_function_call = False
                continue
        if last_cut < len(file_content):
            return_string += file_content[last_cut:]
        return return_string

    def remove_char(self, file_content=''):
        regx = "'[\\w|.|@|;|\\\\\\\\|\"|'|\\(|\\)|\\{|\\}|\\[|\\]|\\*|\\^|\\$|\\?|\\+|\\-|\\=|\\>|\\<|\\/| ]{1,2}'"
        file_content = re.sub(regx, 'LiteralChar ', file_content)
        return file_content

    def remove_string(self, file_content=''):
        quotation_marks = []
        return_string = ''
        string_value = ''
        for i in range(len(file_content)):
            current_char = file_content[i]
            if current_char != '"':
                # current char is not "
                if len(quotation_marks) == 0:
                    return_string += current_char
                else:
                    string_value += current_char
                    pass
            else:
                # current_char is "
                if len(quotation_marks) == 0 and file_content[i - 1] != '\\' and i + 1 in range(len(file_content)) and (
                        file_content[i + 1] != '\'' or file_content[i - 1] != '\''):
                    # If c is ", stack is empty and the char before is not \, means that this " is not in any 's, so push a " into stack.
                    quotation_marks.append('"')
                else:
                    tmp_char = file_content[i - 1]
                    if tmp_char == '\\':
                        string_value += current_char
                        pass
                    else:
                        if len(quotation_marks) == 0:
                            return_string += current_char
                        else:
                            quotation_marks.pop()
                            self.string_counter[string_value] += 1
                            string_value = ''
                            return_string += 'LiteralString '
        return return_string

    def remove_number(self, file_content=''):
        return_string = ''
        last_cut = 0
        for iter in re.finditer(r"[-]{0,1}[0-9]+", file_content):
            start, end = iter.span()
            if file_content[start - 1] != '_' and not file_content[start - 1].isalpha():
                return_string += file_content[last_cut:start]
                if end < len(file_content) and file_content[end].lower() == 'l':
                    return_string += 'LiteralLong '
                    end += 1
                else:
                    return_string += 'LiteralNumber '
                last_cut = end
        if last_cut < len(file_content):
            return_string += file_content[last_cut:]
        return return_string

    def remove_hex_number(self, file_content=''):
        return_string = re.sub(r"0x[0-9a-fA-F]+", 'LiteralHexadecimal ', file_content)

        return return_string

    def remove_floats(self, file_content=''):
        return_string = ''
        last_cut = 0
        for iter in re.finditer(r"[-]{0,1}[0-9]+[\.][0-9]+[fFdD]", file_content):
            start, end = iter.span()
            if file_content[start - 1] != '_' and not file_content[start - 1].isalpha():
                return_string += file_content[last_cut:start]
                if file_content[end - 1].lower() == 'd':
                    return_string += 'LiteralDouble '
                elif file_content[end - 1].lower() == 'f':
                    return_string += 'LiteralFloat '
                last_cut = end
        if last_cut < len(file_content):
            return_string += file_content[last_cut:]
        return return_string

    def line_as_word(self, file_content=''):
        return_string = ''
        if file_content != '':
            lines = file_content.split('\n')
            for i in range(len(lines)):
                line = lines[i].strip()
                if line == '' or line.startswith('import') or line.startswith('package'):
                    continue
                else:
                    line = re.sub("[ \t]+", '$$', line)
                    return_string += line
                    pass
                if i != len(lines) - 1:
                    return_string += ' '
                    pass
            pass
        return return_string

    def normalize(self, function=''):
        function = self.normalize_literal_values(function)
        function = self.normalize_function_calls(function)
        function = self.normalize_class_names(function)
        return function

    # def save_dicts(self):
    #     with open(self.config.get(section='MIDDLE', option='CLASS_NAME2TOKEN'), 'w', encoding='UTF-8') as writer:
    #         for key, value in self.class_name2token.items():
    #             writer.write(key + ' ' + value + '\n')
    #     with open(self.config.get(section='MIDDLE', option='FUNCTION_NAME2TOKEN'), 'w', encoding='UTF-8') as writer:
    #         for key, value in self.function_name2token.items():
    #             writer.write(key + ' ' + value + '\n')
    #     with open(self.config.get(section='MIDDLE', option='ATTRIBUTE_NAME2TOKEN'), 'w', encoding='UTF-8') as writer:
    #         for key, value in self.attribute_name2token.items():
    #             writer.write(key + ' ' + value + '\n')
    #     with open(self.config.get(section='MIDDLE', option='IDENTIFIER2TOKEN'), 'w', encoding='UTF-8') as writer:
    #         for key, value in self.identifier2token.items():
    #             writer.write(key + ' ' + value + '\n')

    def unormalize(self, function, dict, token_node_list):
        function = re.sub(r'@@', ' ', function)
        cut_results = function.split(' ')
        return_result = ''
        return_tokens = []
        return_statements = []
        already_unormalized = 0
        for cut_res in cut_results:
            cut_res = re.sub(r'\$\$', ' ', cut_res)
            cut_res = cut_res.strip()
            tokens = cut_res.split()
            tmp_tokens = []
            for i in range(len(tokens)):
                if already_unormalized == 0:
                    current_loc = i
                else:
                    current_loc = already_unormalized + i
                current_token = tokens[i]
                if current_token == '':
                    i -= 1
                    continue
                ori_token = token_node_list[current_loc].get_content()
                if current_token != ori_token:
                    return ' '.join(tokens)
                if current_loc in dict.keys():
                    tmp_tokens.append(dict[current_loc])
                else:
                    tmp_tokens.append(current_token)
            already_unormalized += len(tmp_tokens)
            return_statements.append(' '.join(tmp_tokens))
            return_tokens.extend(tmp_tokens)
            return_tokens.append('\n')
        return_result += ' '.join(return_tokens)
        return return_result
