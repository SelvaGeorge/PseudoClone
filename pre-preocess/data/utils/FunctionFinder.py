from collections import Counter


class FunctionFinder:
    function_names = Counter()

    # This should be used after tokenizer.
    def find_by_curly_braces(self, origin_string='', target_level=2):
        num_level = 0
        return_string = ''
        for char in origin_string:
            if char == '{':
                num_level += 1
                if num_level >= target_level:
                    return_string += '{'
                    continue
            elif char == '}':
                num_level -= 1
                if not num_level == 0:
                    return_string += char
                if num_level == 1:
                    return_string += '<eof/>'
                continue

            if num_level >= target_level:
                return_string += char
        return return_string

    def find_function_with_lines(self, ori_string):
        functions = []
        total_line_no = 1
        start_line = 0
        end_line = 0
        num_level = 0
        return_string = ''
        for char in ori_string:
            if char == '{':
                num_level += 1
                if num_level >= 2:
                    return_string += '{'
                    start_line = total_line_no
                    continue
            elif char == '}':
                num_level -= 1
                if not num_level == 0:
                    return_string += char
                if num_level == 1:
                    end_line = total_line_no
                    return_string += '<eof/>'
                    functions.append([return_string, start_line, end_line])
                    return_string = ''
                continue
            elif char == '\n':
                total_line_no += 1
            if num_level >= 2:
                return_string += char
        return functions

    #
    # def find_function_names(self, file):
    #     try:
    #         possible_function_name = self.find_candidates(file)
    #         for function_name in possible_function_name:
    #             tokens = function_name.split(' ')
    #             last_token = ''
    #             for token in tokens:
    #                 if '(' in token:
    #                     index = str(token).find('(')
    #                     if index == 0:
    #                         token = last_token
    #                         self.function_names[token] += 1
    #                         break
    #                     else:
    #                         self.function_names[token[0:index]] += 1
    #                         break
    #                 last_token = token
    #     except Exception as e:
    #         print(e)
    #
    # def find_candidates(self, file):
    #     num_braces_level = 0
    #     full_string = ''
    #     with open(file, 'r', encoding='iso8859-1') as opened_file:
    #         for line in opened_file.readlines():
    #             if line.startswith("package") or line.startswith('import') or line.startswith('@'):
    #                 continue
    #             else:
    #                 full_string += line
    #     full_string = self.preprocessor.remove_comments(file_content=full_string)
    #     lines = full_string.split(';')
    #     possible_function_name = []
    #     for i in range(len(lines)):
    #         line = lines[i]
    #         last_cut = 0
    #         for j in range(len(line)):
    #             char = line[j]
    #             if char == '{':
    #                 if num_braces_level == 1:
    #                     # function start
    #                     function_name = line[last_cut:j].replace('\n', '').strip()
    #                     possible_function_name.append(function_name)
    #                 last_cut = j + 1
    #                 num_braces_level += 1
    #             elif char == '}':
    #                 num_braces_level -= 1
    #                 last_cut = j + 1
    #     return possible_function_name
