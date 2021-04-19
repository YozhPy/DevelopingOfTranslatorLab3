from lexer.B2LangLexer import B2LangLexer
from pars.B2LangParser import B2LangParser
from interpreter.B2LangInterpreter import B2LangInterpreter


def main():
    with open('temp_test.b2lang', 'r') as f:
        source_code = f.read()
        lexer = B2LangLexer(source_code)
        lexer.start()
        lexer.print_symbols_table()
        if not lexer.success:
            return False

        parser = B2LangParser(lexer.table_of_symb)
        parser.run()
        if not parser.success:
            return False
        translator = B2LangInterpreter(parser.postfix_code, lexer.tableOfId, lexer.tableOfConst, to_view=True)
        translator.run()
        if translator.success:
            print(translator.table_of_ids)
            print(translator.table_of_consts)


if __name__ == '__main__':
    main()
