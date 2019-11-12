from data.utils.Preprocessor import *
from data.utils.Normalizer import *
from configparser import *
from data.utils.RelationExtractor import *


def extract_function_body(function):
    return_string = ''
    num_level = 0
    is_in_body = False
    for char in function:
        if char == '{':
            num_level += 1
            if num_level == 1:
                is_in_body = True
            return_string += char
        elif char == '}':
            num_level -= 1
            return_string += char
            if num_level == 0:
                is_in_body = False
        else:
            if is_in_body:
                return_string += char
    return return_string


# target = 'public void testHashCode() {\n'\
#         'final MutableLong mutNumA = new MutableLong(0f);\n'\
#         'final MutableLong mutNumB = new MutableLong(0f);\n'\
#         'final MutableLong mutNumC = new MutableLong(1f);\n'\
#         'assertTrue(mutNumA.hashCode() == mutNumA.hashCode());\n'\
#         'assertTrue(mutNumA.hashCode() == mutNumB.hashCode());\n'\
#         'assertFalse(mutNumA.hashCode() == mutNumC.hashCode());\n'\
#         'assertTrue(mutNumA.hashCode() == Float.valueOf(0f).hashCode());\n'\
#     '}'
target = 'public void testNotBlankMsgBlankStringShouldThrow() {\n' \
         '//given\n' \
         'final String string = " \n \t \r \n ";\n' \
         'try {\n' \
         '//when\n' \
         'Validate.notBlank(string, "Message");\n' \
         'fail("Expecting IllegalArgumentException");\n' \
         '} catch (final IllegalArgumentException e) {\n' \
         '//then\n' \
         'assertEquals("Message", e.getMessage());\n' \
         '}\n' \
         '}'
config = ConfigParser()
config.read('config/gpu-config.ini')
pre = PreProcessor()
extractor = RelationExtractor(config)
nor = Normalizer(config)
target = pre.remove_comments(target)
target = extract_function_body(target)
target = nor.normalize_literal_values(target)
function, untokenized_dict, function_statement, function_token, stmt_node_list, token_node_list = extractor.extract(
    target)
print(function_statement)
