"""
This worker catch text features(count word in all space and etc)
"""

from database_interface import website_info_transf_, tf_count_info_, engine

from sqlalchemy import insert, select


def word_count_in_text(text: str) -> dict:
    words_counts = {}
    text = [text]
    for t in text:
        for word in t.split():
            if word in words_counts:
                words_counts[word] += 1
            else:
                words_counts[word] = 1
    return words_counts


def word_tf_in_text(text: str) -> dict:
    words_counts = {}
    text = [text]
    for t in text:
        for word in t.split():
            if word in words_counts:
                words_counts[word] += 1
            else:
                words_counts[word] = 1
    return words_counts


def conc2dict(d1, d2):
    d = d1
    for key, value in d2.items():
        if key in d1:
            d[key] += value
        else:
            d.update({key: value})
    return d


# TODO create async parallel
def catch_text_features():
    stmt = select(website_info_transf_.c.description_2trans)
    with engine.connect() as conn:
        final_dict = {}
        for row in conn.execute(stmt):
            dic = word_count_in_text(row[0])
            final_dict = conc2dict(final_dict, dic)

        for key, value in zip(final_dict.keys(), final_dict.values()):
            dic = {'word': key, 'count_word_in_all_space': value}
            conn.execute(insert(tf_count_info_), [dic])
            conn.commit()
