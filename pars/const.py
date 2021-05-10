parser_errors = {
    'eop': ('B2LangParser ERROR:\n\tНеочікуваний кінець програми - в таблиці символів немає запису з номером %s.', 1001),
    'after_eop': ('B2LangParser ERROR:\n\tНеочікуваіні лексеми за межами головної програми.', 1002),
    'label_conflict': ('B2LangLabelConflict', 1003),
    'tokens': ('B2LangParser ERROR:\n\tВ рядку %s неочікуваний елемент (%s, %s). '
               '\n\tОчікувався - (%s, %s).', 1),
    'not_expected': (f'\n\tВ рядку %s неочікуваний елемент (%s, %s).\n\tОчікувався - %s.', 2)
}

parser_warnings = {
    'no_effect': 'B2LangParser Warning: \n\tВираз на рядку %s не має ефекту.'
}