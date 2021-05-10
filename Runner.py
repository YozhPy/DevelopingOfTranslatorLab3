from lexer.B2LangLexer import B2LangLexer
from pars.B2LangParser import B2LangParser
from interpreter.B2LangInterpreter import B2LangInterpreter


def main():
    with open('temp_test.b2lang', 'r') as f:
        source_code = f.read()
        lexer = B2LangLexer(source_code)
        lexer.start()
        #lexer.print_symbols_table()
        #lexer.print_label_table()
        #lexer.print_const_table()
        #lexer.print_ids_table()
        if not lexer.success:
            return False
        parser = B2LangParser(lexer.table_of_symb, lexer.table_of_id, lexer.table_of_label)
        parser.run()
        #print(parser.postfix_code)
        #print(parser.table_of_label)
        if not parser.success:
            return False
        translator = B2LangInterpreter(parser.postfix_code, parser.table_of_id, lexer.table_of_const,
                                       parser.table_of_label, to_view=True)
        translator.run()
        if translator.success:
            print("МОВА ПРОГРАМУВАННЯ B2LANG ХОЧЕ НАДРУКУВАТИ:")
            for val in translator.final_msg:
                print(val)
            translator.pretty_pr_table_id()
            translator.pretty_pr_table_label()


if __name__ == '__main__':
    main()
