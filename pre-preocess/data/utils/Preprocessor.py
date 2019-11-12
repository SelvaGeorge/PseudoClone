import os
import re
from collections import Counter


class PreProcessor:
    imported_java_classes = Counter()
    imported_outside_classes = Counter()
    self_defined_classes = Counter()
    function_names = Counter()
    all_java_files = []
    failed_java_files = []

    # to remove all comments in a target string
    def remove_comments(self, file_content=''):
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

    # to find self defined classes under specific folder
    def find_self_defined(self, files_list=[]):
        # In real project, in a single java file, there must have one and only one public class
        # so that other classes can access. What's more, the class name should be the same as
        # the file name. So, we extract user defined class names based on java file names.
        for file in files_list:
            if file.endswith('.java'):
                infos = file.split(os.path)
                file_name = infos.reverse()[0]
                seperated_file_info = file_name.split('.')
                self.self_defined_classes[seperated_file_info[0]] += 1

    def find_imported(self, file_content=''):
        statements = file_content.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement.startswith('import'):
                # ignore "import " sub-string
                statement = statement[7:]
                tokens = statement.split('.')
                if 'java' in tokens and tokens[0] == 'java':
                    if tokens[len(tokens) - 1] != '*':
                        self.imported_java_classes[tokens[len(tokens) - 1]] += 1
                else:
                    if tokens[len(tokens) - 1] != '*':
                        self.imported_outside_classes[tokens[len(tokens) - 1]] += 1

    def read_file(self, file_path='', start=0, end=0):
        return_string = ''
        with open(file_path, 'r', encoding='iso8859-1') as reader:
            lines = reader.readlines()
            for i in range(len(lines)):
                if i >= start - 1 and i < end:
                    return_string += lines[i]
        return return_string

    def write_to_file(self, target_file='', target_string=''):
        with open(target_file, 'w', encoding='UTF-8') as writer:
            writer.write(target_string)



class SpecialCharCutter:
    cut_regx = r"[-+\\*/%=<>!&\\|\\^~\\?:,\"']{1,2}[>=]{0,1}"

    def __init__(self, config):
        self.config = config
        self.dict = []
        self.load_dict()

    def get_dict(self):
        return self.dict

    def load_dict(self):
        with open(self.config.get(section='MIDDLE', option='OPERATION_CUTTER_DICT')) as reader:
            for line in reader.readlines():
                line = line.strip()
                if line.startswith('#'):
                    continue
                else:
                    tokens = line.split(',')
                    self.dict.extend(tokens)
                    pass

    def cut(self, function=''):
        tokens = []
        function = re.sub(r'[\t\r]', '', function)
        ori_tokens = function.split(' ')
        for ori_token in ori_tokens:
            if ori_token == '':
                continue
            else:
                last_cut = 0
                for iter in re.finditer(r'[-+\\*/%=<>!&\\|\\^~\\?:",\']{1,2}[>=]{0,1}', ori_token):
                    operator_start, operator_end = iter.span()
                    operator = iter.group()
                    if operator_start > last_cut:
                        tokens.append(ori_token[last_cut:operator_start])
                    tokens.append(operator)
                    last_cut = operator_end
                if last_cut < len(ori_token):
                    tokens.append(ori_token[last_cut:])
        return ' '.join(tokens)


class BracesCutter:
    def cut(self, function='', if_keep_function_call=False):
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


class FunctionCallCutter:
    # TODO: Add function call and attribute access cutter
    def __init__(self, config):
        self.config = config
        self.operator_dict = []
        self.load_dict()
        self.function_call_regx = '[\\.]?[ ]*[a-zA-Z0-9_]+\\('
        # self.attribute_acc_regx = '\\.[ ]*[a-zA-Z0-9_]+'

    def load_dict(self):
        with open(self.config.get(section='MIDDLE', option='OPERATION_CUTTER_DICT')) as reader:
            for line in reader.readlines():
                line = line.strip()
                if line.startswith('#'):
                    continue
                else:
                    tokens = line.split(',')
                    self.operator_dict.extend(tokens)
                    pass
        self.operator_dict = set(self.operator_dict)

    def cut(self, function):
        normalize_dict = {}
        after_normalized = ''
        last_cut = 0
        for iter in re.finditer('[\.]?[ ]*[a-zA-Z0-9_]+\(', function):
            start, end = iter.span()
            function_name = iter.group()
            if start > last_cut:
                after_normalized += function[last_cut:start]
            fucntion_name = function_name.replace(' ', '')
            if function_name.startswith('.'):
                current_after_normalize = ' .functionCall( '
                normalize_dict[str(start) + '-' + str(end)] = fucntion_name
                pass
            else:
                current_after_normalize = ' functionCall( '
                normalize_dict[str(start) + '-' + str(end)] = fucntion_name
                pass
            after_normalized += current_after_normalize
            last_cut = end
        if last_cut < len(function): after_normalized += function[last_cut:]
        return after_normalized
