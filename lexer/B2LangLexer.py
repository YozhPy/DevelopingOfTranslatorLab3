from lexer.const import *
from prettytable import PrettyTable


class B2LangLexer:
    tableOfLanguageTokens = tableOfLanguageTokens
    tableIdentFloatInt = tableIdentFloatInt
    classes = classes
    stf = stf
    states = states
    errors_text = errors_text

    def __init__(self, b2lang_code):
        self.program_code = b2lang_code + ' '
        self.lenOfCode = len(self.program_code)
        # Tables
        self.tableOfSymbols = PrettyTable(["#", "Лексема", "Токен", "Індекс"])

        self.table_of_id = {}
        self.table_of_const = {}
        self.table_of_symb = {}
        self.table_of_label = {}

        # Current State
        self.state = states["initial"][0]

        # Needed variables
        self.numLine = 1
        self.numChar = 0
        self.char = ''
        self.lexeme = ''
        self.success = True

    def start(self):
        try:
            while self.numChar < self.lenOfCode:
                self.char = self._next_char()  # read next char
                self.state = B2LangLexer._next_state(self.state, B2LangLexer._class_of_char(self.char))
                if B2LangLexer._is_initial_state(self.state):
                    self.lexeme = ''
                elif B2LangLexer._is_final_state(self.state):
                    self.processing()
                else:
                    self.lexeme += self.char
                   # print(self.lexeme)
            self.correct_label_and_id()
            print('Лексичний аналіз завершено. Успіх!')
        except SystemExit as err:
            self.success = False
            print('B2LangLexer: Аварійне завершення програми з кодом {0}'.format(err))

    def processing(self):

        if self.state in B2LangLexer.states['newLine']:
            self.numLine += 1
            self.state = B2LangLexer.states['initial'][0]

        elif self.state in (B2LangLexer.states['const'] + B2LangLexer.states['identifier']
                            + B2LangLexer.states['colon']):
            token = B2LangLexer._get_token(self.state, self.lexeme)
            if token != 'keyword':
                index = self._get_index()
                self.tableOfSymbols.add_row([self.numLine, self.lexeme, token, index])
                self.table_of_symb[len(self.table_of_symb) + 1] = (self.numLine, self.lexeme, token, index)
            else:
                self.tableOfSymbols.add_row([self.numLine, self.lexeme, token, ''])
                self.table_of_symb[len(self.table_of_symb) + 1] = (self.numLine, self.lexeme, token, '')

            self.lexeme = ''
            self.state = B2LangLexer.states['initial'][0]
            self._put_char_back()

        elif self.state in B2LangLexer.states['operators']:
            if not self.lexeme or self.state in B2LangLexer.states['double_operators']:
                self.lexeme += self.char
            token = B2LangLexer._get_token(self.state, self.lexeme)
            self.tableOfSymbols.add_row([self.numLine, self.lexeme, token, ''])
            self.table_of_symb[len(self.table_of_symb) + 1] = (self.numLine, self.lexeme, token, '')
            if self.state in B2LangLexer.states['star']:
                self._put_char_back()
            self.lexeme = ''
            self.state = B2LangLexer.states['initial'][0]

        elif self.state in B2LangLexer.states['errors']:
            self.fail()

    def fail(self):
        for num, text in B2LangLexer.errors_text.items():
            if self.state == num:
                print(text % (self.numLine, self.char))
                exit(num)

    def print_symbols_table(self):
        print("Таблиця символів")
        print(self.tableOfSymbols)

    def print_ids_table(self):
        print("Таблиця ідентифікаторів")
        tbl = PrettyTable(["Назва", "Індекс"])
        for name, indx in self.table_of_id.items():
            tbl.add_row([name, indx])
        print(tbl)

    def print_const_table(self):
        print("Таблиця констант")
        tbl = PrettyTable(["Константа", "Індекс"])
        for cnst, indx in self.table_of_const.items():
            tbl.add_row([cnst, indx])
        print(tbl)

    def print_label_table(self):
        print("Таблиця міток")
        tbl = PrettyTable(["Мітка", "Індекс"])
        for cnst, indx in self.table_of_label.items():
            tbl.add_row([cnst, indx])
        print(tbl)

    def _get_index(self):
        if self.state in self.states['const'] or self.lexeme in ('true', 'false'):
            return B2LangLexer._getSetID(self.state, self.lexeme, self.table_of_const)
        elif self.state in self.states['colon']:
            return B2LangLexer._getSetID(self.state, self.lexeme, self.table_of_label)
        elif self.state in self.states['identifier']:
            return B2LangLexer._getSetID(self.state, self.lexeme, self.table_of_id)

    def _next_char(self):
        char = self.program_code[self.numChar]
        self.numChar += 1
        return char

    def _put_char_back(self):
        self.numChar += -1

    @staticmethod
    def _get_token(state, lexeme):
        try:
            return B2LangLexer.tableOfLanguageTokens[lexeme]
        except KeyError:
            return B2LangLexer.tableIdentFloatInt[state]

    @staticmethod
    def _is_initial_state(state):
        return state in B2LangLexer.states['initial']

    @staticmethod
    def _is_final_state(state):
        return state in B2LangLexer.states['final']

    @staticmethod
    def _next_state(state, cls):
        try:
            return B2LangLexer.stf[(state, cls)]
        except KeyError:
            return B2LangLexer.stf[(state, 'other')]

    @staticmethod
    def _class_of_char(char):
        for key, value in classes.items():
            if char in value:
                if key == "Operators":
                    return char
                else:
                    return key
        return "Цей символ не входить в жодний клас"

    @staticmethod
    def _getSetID(state, lexeme, table):
        index = table.get(lexeme)
       # print(B2LangLexer._get_token(state, lexeme))
        if not index:
            index = len(table) + 1
            if (token := B2LangLexer._get_token(state,lexeme)) == 'ident':
                token = 'undefined'
            table[lexeme] = (index, token)

            if (token := B2LangLexer._get_token(state,lexeme)) == 'label':
                token = 'undefined'
            table[lexeme] = (index, token)

            if lexeme in ('true', 'false'):
                table[lexeme] += (eval(lexeme.title()),)
            elif state in (B2LangLexer.states['identifier'] + B2LangLexer.states['colon']):
                table[lexeme] += ('null',)
            else:
             #   print(eval(f"{token}({lexeme})"))
                table[lexeme] += (eval(f"{token}({lexeme})"), )
        return index

    def correct_label_and_id(self):
        for cnst, _ in self.table_of_label.items():
            if cnst in self.table_of_id:
                self.table_of_id.pop(cnst)
