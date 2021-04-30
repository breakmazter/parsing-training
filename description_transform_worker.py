"""
This worker transform(cleaning from garbage and etc) text and translate to english text
"""

from database_interface import website_info_transf_, devby_website_, engine
from clear_text import clear_all

from word2word import Word2word

from sqlalchemy import insert, select

translate = Word2word("ru", "en")


def translate_text(text: str) -> str:
    mass_str = text.split()
    mass_trans = []
    for s in mass_str:
        try:
            tr_word = translate(s, n_best=2)[1]
        except KeyError as e:
            tr_word = ''

        mass_trans.append(tr_word)

    return ' '.join(mass_trans)


# TODO create async parallel
def clear_translate_description():
    stmt = select(devby_website_.c.id, devby_website_.c.description)
    with engine.connect() as conn:
        for row in conn.execute(stmt):
            dic = {'company_id': row[0], 'description_2trans': clear_all(translate_text(row[1]))}
            conn.execute(insert(website_info_transf_), [dic])
            conn.commit()
