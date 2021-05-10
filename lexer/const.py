# Таблица лексем
tableOfLanguageTokens = {
    'start': 'keyword', 'int': 'keyword', 'float': 'keyword', 'bool': 'keyword',
    'input': 'keyword', 'print': 'keyword', 'for': 'keyword', 'while': 'keyword',
    'to': 'keyword', 'by': 'keyword', 'rof': 'keyword',
    'if': 'keyword', 'goto': 'keyword',

    'true': 'bool', 'false': 'bool',

    '=': 'assign_op', '+': 'add_op', '-': 'add_op', '*': 'mult_op', '/': 'mult_op',
    '^': 'pow_op', '<': 'rel_op', '<=': 'rel_op', '==': 'rel_op', '!=': 'rel_op', '>=': 'rel_op',
    '>': 'rel_op', '&&': 'bool_op', '||': 'bool_op',

    '(': 'brackets_op', ')': 'brackets_op', '{': 'curve_brackets_op', '}': 'curve_brackets_op',
    ':': 'colon_op',
    '.': 'dot', ',': 'comma', ';': 'op_end', ' ': 'ws', '\t': 'ws', '\n': 'nl',
}

# Таблица идентификаторов и констант
tableIdentFloatInt = {2: 'ident', 5: 'float', 6: 'int', 19: 'int', 40: 'label'}

classes = {
    "Letter": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_",
    "NonZeroDigit": "123456789",
    "ZeroDigit": "0",
    "Dot": ".",
    "WhiteSep": " \t",
    "Newline": "\n",
    "Operators": "+-*/^(){}=><!;,&|",
    "ColonOp": ":",
}

# δ - state-transition functions (STF)
stf = {
    (0, 'WhiteSep'): 0,
    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'ZeroDigit'): 1, (1, 'NonZeroDigit'): 1, (1, 'ColonOp'): 40,
    (1, 'other'): 2,
    (0, 'NonZeroDigit'): 3, (3, 'ZeroDigit'): 3, (3, 'NonZeroDigit'): 3, (3, 'Dot'): 4, (3, 'other'): 6,
    (4, 'ZeroDigit'): 4, (4, 'NonZeroDigit'): 4, (4, 'other'): 5,  # Целые и числа с запятой
    (0, '!'): 7, (7, '='): 8, (7, 'other'): 102,  # символ неравенства
    (0, '='): 9, (0, '>'): 9, (0, '<'): 9, (9, '='): 10, (9, 'other'): 11,  # символы сравнения
    (0, ','): 12, (0, ';'): 12, (0, '+'): 12, (0, '-'): 12, (0, '*'): 12, (0, '/'): 12, (0, '^'): 12, (0, '('): 12,
    (0, ')'): 12, (0, '{'): 12, (0, '}'): 12,  # Операторы
    (0, 'ColonOp'): 33,
    (0, '&'): 14, (14, '&'): 15, (14, 'other'): 103,  # Булевое И
    (0, '|'): 16, (16, '|'): 17, (16, 'other'): 104,  # Булевое ИЛИ
    (0, 'ZeroDigit'): 18, (18, 'ZeroDigit'): 105, (18, 'NonZeroDigit'): 105, (18, 'Letter'): 105, (18, 'other'): 19,
    (18, 'Dot'): 4,  # Проверка после точки
    (0, 'Newline'): 13,
    (0, 'other'): 101
}

states = {
    'initial': (0,),
    'star': (2, 5, 6, 11, 19, 40),
    'errors': (101, 102, 103, 104, 105),
    'final': (2, 5, 6, 8, 10, 11, 12, 13, 15, 17, 19,33, 40, 101, 102, 103, 104, 105),
    'newLine': (13,),
    'operators': (8, 10, 11, 12, 15, 17, 33),
    'double_operators': (8, 10, 15, 17),
    'const': (5, 6, 19),
    'identifier': (2,),
    'colon': (40,)
}

errors_text = {
    101: 'B2LangLexerError: у рядку %s неочікуваний символ %s',
    102: 'B2LangLexerError: у рядку %s очікувався символ =, а не %s',
    103: 'B2LangLexerError: у рядку %s очікувався символ &, а не %s',
    104: 'B2LangLexerError: у рядку %s очікувався символ |, а не %s',
    105: 'B2LangLexerError: у рядку %s за нулем не може слідувати символ %s',
}
