from pars.const import (
    parser_errors as errors,
    parser_warnings as warnings
)


class B2LangParser:

    def __init__(self, table_of_symbols, table_of_id, table_of_label, to_view=False):
        self.symbolsTable = table_of_symbols
        self.len_symbols = len(self.symbolsTable)
        self.row_number = 1
        self.table_of_label = table_of_label
        self.table_of_id = table_of_id
        self.table_of_consts = {}
        self.success = True
        self.postfix_code = []
        self.to_view = to_view
        self.for_vars = []

    def run(self):
        self.success = self.parse_program()
        print('\n\033[0m')

    @staticmethod
    def warning_parse(warning: str, *args):
        print("\033[33m")
        warning_msg = warnings.get(warning, None)
        print(warning_msg % args)
        print('\n\033[0m')

    @staticmethod
    def fail_parse(error: str, *args):
        print("\033[31m")
        error_msg, error_code = errors.get(error, (None, None))
        print(error_msg % args)
        print('\n\033[0m')
        exit(error_code)

    @staticmethod
    def print_lexeme_info(line_number, lex, tok, indent=''):
        print(indent + f'в рядку {line_number} - {(lex, tok)}')

    def configToPrint(self, lex):
        to_print = "\nTranslator step\n\tlexeme: %s\n\tsymbolsTable[%s]: %s\n\tpostfix_code %s\n"
        print(to_print % (lex, self.row_number, self.symbolsTable[self.row_number], self.postfix_code))

    @staticmethod
    def print_not_final_token(line_number, lex, tok, indent=''):
        print(indent + f'в рядку {line_number} - {(lex, tok)}')

    def get_symbol(self):
        if self.row_number > self.len_symbols:
            B2LangParser.fail_parse('eop', self.row_number)
        return self.symbolsTable[self.row_number][0:-1]

    def parse_token(self, lexeme, token, indent=''):
        line_number, lex, tok = self.get_symbol()

        self.row_number += 1

        if lex == lexeme and tok == token:
            return True
        else:
            B2LangParser.fail_parse('tokens', line_number, lex, tok, lexeme, token)
            return False

    def parse_program(self):
        try:
            self.parse_token('start', 'keyword')
            self.parse_token('{', 'curve_brackets_op')

            self.parse_statements_list()
            if self.row_number < self.len_symbols:
                B2LangParser.fail_parse('after_eop')
            else:
                self.parse_token('}', 'curve_brackets_op')
        except SystemExit as e:
            print("\033[31m", end='')
            print('Parser: Аварійне завершення програми з кодом {0}'.format(e))
            print("\033[31m", end='')
            return False

        print("\033[31m", end='')
        print('B2LangParser: Синтаксичний аналіз завершився успішно')
        print("\033[31m", end='')
        return True

    def parse_statements_list(self):
        while self.parse_statement():
            pass
        return True

    def parse_statement(self):
        line_number, lex, tok = self.get_symbol()

        if tok == 'ident':
            self.postfix_code.append((lex, tok, None))
            if self.to_view:
                self.configToPrint(lex)

            self.row_number += 1

            if self.get_symbol()[-1] == 'assign_op':
                self.parse_assign()
            else:
                self.row_number -= 1
                self.parse_expression()
                B2LangParser.warning_parse('no_effect', line_number)
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex == 'input' and tok == 'keyword':
            self.parse_input()
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex == 'print' and tok == 'keyword':
            self.parse_print()
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif tok == 'label':
            self.parse_label()
            return True

        elif lex == 'goto' and tok == 'keyword':
            self.parse_goto()
            return True

        elif lex in ('int', 'float', 'bool') and tok == 'keyword':
            self.parse_declaration()
            self.parse_token(';', 'op_end', '\t' * 3)
            return True

        elif lex == 'for' and tok == 'keyword':
            self.parse_for()
            return True
        #
        # elif lex == 'while' and tok == 'keyword':
        #     self.parse_for()
        #     return True

        elif lex == 'if' and tok == 'keyword':
            self.parse_if()
            return True

        # elif tok == 'label':
        #     self.parse_label()
        #     return True
        #
        # elif lex == 'goto' and tok == 'keyword':
        #     self.parse_goto()
        #     return True

        elif lex == '}' and tok == 'curve_brackets_op':
            return False

        else:
            self.parse_expression()
            self.parse_token(';', 'op_end', '\t' * 3)
            B2LangParser.warning_parse('no_effect', line_number)
            return True

    def parse_input(self):
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1

        self.parse_token('(', 'brackets_op', '\t' * 4)
        self.parse_io_content(allow_arithm_expr=False)
        self.parse_token(')', 'brackets_op', '\t' * 4)

    def parse_print(self):
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1

        self.parse_token('(', 'brackets_op', '\t' * 4)
        self.parse_io_content()
        self.parse_token(')', 'brackets_op', '\t' * 4)

    def parse_io_content(self, allow_arithm_expr=True):
        line_number, lex, tok = self.get_symbol()

        if tok in ('ident', 'int', 'float', 'bool') and allow_arithm_expr:
            self.parse_arithm_expression()
        elif tok == 'ident':
            self.postfix_code.append((lex, tok, None))
            self.row_number += 1
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                    "ідентифікатор (ident)")

        line_number, lex, tok = self.get_symbol()
        if lex == ')' and tok == 'brackets_op':
            if allow_arithm_expr:
                self.postfix_code.append(('OUT', 'out', None))
            else:
                self.postfix_code.append(('INPUT', 'input', None))
            return True

        elif lex == ',' and tok == 'comma':
            if allow_arithm_expr:
                self.postfix_code.append(('OUT', 'out', None))
            else:
                self.postfix_code.append(('INPUT', 'input', None))
            self.row_number += 1
            self.parse_io_content(allow_arithm_expr)

    def parse_assign(self):
        if self.parse_token('=', 'assign_op', '\t' * 3):
            self.parse_expression()
            self.postfix_code.append(("=", 'assign_op', None))
            if self.to_view:
                self.configToPrint('=')
            return True
        else:
            return False

    def parse_expression(self, required=False):
        self.parse_arithm_expression()

        while self.parse_bool_expr():
            pass

        return True

    def parse_bool_expr(self, required=False):
        line_number, lex, tok = self.get_symbol()
        if tok in ('rel_op', 'bool_op'):
            self.row_number += 1
            self.parse_arithm_expression()
            self.postfix_code.append((lex, tok, None))

            return True

        elif required:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok, required)

        else:
            return False

    def parse_arithm_expression(self):
        self.parse_term()

        while True:
            line_number, lex, tok = self.get_symbol()
            if tok == 'add_op':
                self.row_number += 1
                self.parse_term()
                self.postfix_code.append((lex, tok, None))
                if self.to_view:
                    self.configToPrint(lex)
            else:
                break
        return True

    def parse_term(self):
        self.parse_power()
        while True:
            line_number, lex, tok = self.get_symbol()
            if tok == 'mult_op':
                self.row_number += 1
                self.parse_power()
                self.postfix_code.append((lex, tok, None))
                if self.to_view:
                    self.configToPrint(lex)
            else:
                break
        return True

    def parse_power(self):
        self.parse_factor()
        while True:
            line_number, lex, tok = self.get_symbol()
            if tok == 'pow_op':
                self.row_number += 1
                self.parse_factor()
                self.postfix_code.append((lex, tok, None))
                if self.to_view:
                    self.configToPrint(lex)
            else:
                break
        return True

    def parse_factor(self):
        has_unar = False
        line_number, lex, tok = self.get_symbol()
        if lex == '-':
            has_unar = True
            self.row_number += 1
            line_number, lex, tok = self.get_symbol()

        if tok in ('int', 'float', 'bool', 'ident'):
            self.postfix_code.append((lex, tok, None))
            if self.to_view:
                self.configToPrint(lex)

            if has_unar:
                self.postfix_code.append(('@', 'unar_minus', None))
                if self.to_view:
                    self.configToPrint(lex)
            self.row_number += 1

        elif lex == '(':
            self.row_number += 1
            self.parse_arithm_expression()
            self.parse_token(')', 'brackets_op', '\t' * 7)
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                    'rel_op, int, float, ident або \'(\' Expression \')\'')
        return True

    def parse_label(self):
        line_number, lex, tok = self.get_symbol()
        self.table_of_label[lex] = len(self.postfix_code)
        self.postfix_code.append((lex, tok, None))
        self.row_number += 1
        while True:
            line_number, lex, tok = self.get_symbol()
            if tok == 'colon_op':
                self.row_number += 1
                self.postfix_code.append((lex, tok, None))
                if self.to_view:
                    self.configToPrint(lex)
            else:
                break
            return True

    def parse_goto(self):
        self.row_number += 1
        line_number, lex, tok = self.get_symbol()
        self.postfix_code.append((lex, tok, None))
        self.postfix_code.append(('JUMP', 'jump', None))
        self.row_number += 1
        self.parse_token(';', 'op_end', '\t' * 5)
        return True

    def parse_declaration(self):
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1
        if lex in ('int', 'float', 'bool') and tok == 'keyword':
            self.parse_var_list(lex)
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                    'int, float або bool.')

    def parse_var_list(self, var_type):
        line_number, lex, tok = self.get_symbol()
        self.row_number += 1

        if tok == 'ident':
            self.postfix_code.append((lex, tok, var_type))
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok,
                                    "ідентифікатор (ident)")

        line_number, lex, tok = self.get_symbol()
        if lex == '=' and tok == 'assign_op':
            self.parse_assign()
            line_number, lex, tok = self.get_symbol()

        if lex == ',' and tok == 'comma':
            self.row_number += 1
            self.parse_var_list(var_type)

        elif lex == ';' and tok == 'op_end':
            return True

    def parse_if(self):
        line_number, lex, tok = self.get_symbol()
        if lex == 'if' and tok == 'keyword':
            self.row_number += 1
            self.parse_expression(required=True)

            m1 = self.create_label()
            self.postfix_code.append((*m1, None))
            self.postfix_code.append(('JF', 'jf', None))
            self.parse_goto()
            self.set_label_val(m1)
            self.postfix_code.append((*m1, None))
            self.postfix_code.append((':', 'colon_op', None))
            return True
        else:
            return False

    def parse_for(self):
        step, end = self.create_label(), self.create_label()
        self.parse_token('for', 'keyword', '\t' * 4)
        self.parse_ind_expression(step, end)

        line_number, lex, tok = self.get_symbol()
        if lex == '{' and tok == 'curve_brackets_op':
            self.row_number += 1
            self.parse_statements_list()
            self.parse_token('}', 'curve_brackets_op', '\t' * 4)
            self.parse_token('rof', 'keyword')
            self.parse_token(';', 'op_end')
        else:
            self.parse_statement()
        tmp = self.for_vars.pop()
        self.postfix_code.append((tmp[1], 'ident', None))
        self.postfix_code.append((tmp[0], 'ident', None))
        self.postfix_code.append(('=', 'assign_op', None))

        self.postfix_code.append((*step, None))
        self.postfix_code.append(('JUMP', 'jump', None))
        self.set_label_val(end)
        self.postfix_code.append((*end, None))
        self.postfix_code.append((':', 'colon_op', None))

    def parse_ind_expression(self, step, end):
        line_number, lex, tok = self.get_symbol()
        if tok == 'ident':
            self.postfix_code.append((lex, tok, None))
            _len = len(self.for_vars)
            self.for_vars.append((f'temp_{_len}', lex))
            self.table_of_id[f'temp_{_len}'] = (len(self.table_of_id), 'int', 'null')
            self.row_number += 1
            self.parse_assign()
            self.set_label_val(step)
            self.postfix_code.append((*end, None))
            self.postfix_code.append((':', 'colon_op', None))
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok, "ідентифікатор")

        self.parse_token('to', 'keyword', '\t' * 5)

        self.postfix_code.append((self.for_vars[0][-1], 'ident', 'int'))
        self.parse_arithm_expression()
        self.postfix_code.append(('<', 'rel_op', None))

        self.parse_token('by', 'keyword', '\t' * 5)
        self.postfix_code.append((*end, None))
        self.postfix_code.append(('JF', 'jf', None))

        if tok == 'ident':
            _len = len(self.for_vars) - 1
            self.postfix_code.append((f'temp_{_len}', 'ident', 'int'))
            self.postfix_code.append((self.for_vars[0][-1], 'ident', 'int'))
            self.parse_expression()
            self.postfix_code.append(('+', 'add_op', None))
            self.postfix_code.append(("=", 'assign_op', None))

        self.parse_token('while', 'keyword', '\t' * 4)
        line_number, lex, tok = self.get_symbol()
        if lex == '(' and tok == 'brackets_op':

            self.row_number += 1
            self.parse_expression(required=True)
            self.postfix_code.append((*end, None))
            self.postfix_code.append(('JF', 'jf', None))
            self.parse_token(')', 'brackets_op', '\t' * 4)
        else:
            B2LangParser.fail_parse('not_expected', line_number, lex, tok, "ідентифікатор")

    def parse_my_for(self):
        self.parse_token('for', 'keyword', '\t' * 4)
        line_number, lex, tok = self.get_symbol()
        self.postfix_code.append((lex, tok, None))
        self.row_number += 1
        m1 = self.create_label()
        self.set_label_val(m1)
        self.postfix_code.append((*m1, None))
        self.postfix_code.append((':', 'colon_op', None))
        self.table_of_id['for_to'] = (len(self.table_of_id), 'type_undef', 'val_undef')

    # def parse_for(self):
    #     step, end = self.create_label(), self.create_label()
    #     self.parse_token('for', 'keyword', '\t' * 4)
    #     self.parse_expression()
    #     self.parse_token('by', 'keyword', '\t' * 4)
    #     self.parse_expression()
    #     self.parse_token('to', 'keyword', '\t' * 4)
    #     self.parse_expression()
    #
    #     else:
    #         self.parse_statement()
    #
    # def parse_ind_expression(self, step, end):
    #
    #     line_number, lex, tok = self.get_symbol()
    #     if tok == 'ident':
    #         self.postfix_code.append((lex, tok, None))
    #         self.row_number += 1
    #         self.parse_assign()
    #         self.set_label_val(step)
    #         self.postfix_code.append((*step, None))
    #         self.postfix_code.append((':', 'colon', None))
    #     else:
    #         B2LangParser.fail_parse('not_expected', line_number, lex, tok,
    #                              "ідентифікатор (ident)")
    #     self.parse_token(';', 'op_end', '\t' * 5)
    #     self.parse_expression(required=True)
    #     self.parse_token(';', 'op_end', '\t' * 5)
    #
    #     self.postfix_code.append((*end, None))
    #     self.postfix_code.append(('JF', 'jf', None))
    #
    #     if tok == 'ident':
    #         _len = len(self.for_vars)
    #         self.for_vars.append((f'temp_{_len}', lex))
    #         self.table_of_id[f'temp_{_len}'] = (len(self.table_of_id), 'int', 'null')
    #         self.postfix_code.append((f'temp_{_len}', 'ident', 'int'))
    #         self.row_number += 1
    #         self.parse_assign()
    #     else:
    #         B2LangParser.fail_parse('not_expected', line_number, lex, tok,
    #                              "ідентифікатор (ident)")

    def create_label(self):
        new_label = len(self.table_of_label) + 1
        lexeme = f"m{new_label}"
        if not self.table_of_label.get(lexeme):
            self.table_of_label[lexeme] = 'val_undef'
            return lexeme, 'label'
        B2LangParser.fail_parse('label_conflict')

    def set_label_val(self, m1):
        self.table_of_label[m1[0]] = len(self.postfix_code)
