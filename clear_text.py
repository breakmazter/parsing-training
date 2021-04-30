import re
import string


def remove_URL(text: str) -> str:
    pattern_url = re.compile(r'https?://\S+|www\.\S+')
    return pattern_url.sub(r' ', text)


def remove_HTML(text: str) -> str:
    pattern_html = re.compile(r'<.*?>')
    return pattern_html.sub(r' ', text)


def remove_EMOJI(text: str) -> str:
    pattern_emoji = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return pattern_emoji.sub(r' ', text)


def remove_PUNC(text: str) -> str:
    table = str.maketrans(' ', ' ', string.punctuation)
    return text.translate(table)


def remove_NUM(text: str) -> str:
    pattern_num = re.compile(r'[^\w\s]+|[\d]+')
    return pattern_num.sub(r' ', text)


def remove_NOTASCII(text: str) -> str:
    return text.encode("ascii", errors="ignore").decode()


def remove_TABETC(text: str) -> str:
    pattern_tabetc = re.compile(r'^\s+|\n|\r|\s+$')
    return pattern_tabetc.sub(r' ', text)


def clear_all(text: str,
              html_e=True, url_e=True, emoji_e=True, punc_e=True, num_e=True, notascii_e=False, tabetc_e=True) -> str:
    if html_e:
        text = remove_HTML(text)
    if url_e:
        text = remove_URL(text)
    if emoji_e:
        text = remove_EMOJI(text)
    if punc_e:
        text = remove_PUNC(text)
    if num_e:
        text = remove_NUM(text)
    if notascii_e:
        text = remove_NOTASCII(text)
    if tabetc_e:
        text = remove_TABETC(text)

    text = ' '.join(text.split())
    return text.lower()
