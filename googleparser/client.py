import random
import typing
import json

import httpcore
import httpx
from httpx import Timeout

from googleparser import urls, utils
from googleparser.gtoken import TokenAcquirer
from googleparser.constants import (
    DEFAULT_CLIENT_SERVICE_URLS,
    DEFAULT_FALLBACK_SERVICE_URLS,
    DEFAULT_USER_AGENT, LANGCODES, LANGUAGES, SPECIAL_CASES,
    DEFAULT_RAISE_EXCEPTION, DUMMY_DATA
)
from googleparser.models import Translated, Detected, TranslatedPart

EXCLUDES = ('en', 'ca', 'fr')

RPC_ID = 'MkEWBc'


class Translator:
    """
    General class to represent translations
    Attributes
    ----------
    client : httpx.Client
        client to communicate with Google Translate
    service_urls : List[str]
        list of urls to make requests to
    raise_exception : bool
        raise exception flag
    client_type : str
        determines the way of parsing
    token_acquirer : TokenAcquirer
        generates token for parsing
    """

    def __init__(self, service_urls=DEFAULT_CLIENT_SERVICE_URLS, user_agent=DEFAULT_USER_AGENT,
                 raise_exception=DEFAULT_RAISE_EXCEPTION,
                 proxies: typing.Dict[str, httpcore.SyncHTTPTransport] = None,
                 timeout: Timeout = None,
                 http2=True,
                 use_fallback=False):

        self.client = httpx.Client(http2=http2)
        if proxies is not None:  # pragma: nocover
            self.client.proxies = proxies

        self.client.headers.update({
            'User-Agent': user_agent,
            #'Referer': 'https://translate.google.com',
        })

        if timeout is not None:
            self.client.timeout = timeout

        if use_fallback:
            self.service_urls = DEFAULT_FALLBACK_SERVICE_URLS
            self.client_type = 'gtx'
            pass
        else:
            #default way of working: use the defined values from user app
            self.service_urls = service_urls
            self.client_type = 'tw-ob'
            self.token_acquirer = TokenAcquirer(
                client=self.client, host=self.service_urls[0])

        self.raise_exception = raise_exception

    def _build_rpc_request(self, text: str, dest: str, src: str):
        return json.dumps([[
            [
                RPC_ID,
                json.dumps([[text, src, dest, True], [None]], separators=(',', ':')),
                None,
                'generic',
            ],
        ]], separators=(',', ':'))

    def _pick_service_url(self):
        if len(self.service_urls) == 1:
            return self.service_urls[0]
        return random.choice(self.service_urls)

    def _translate(self, text: str, dest: str, src: str):
        url = urls.TRANSLATE_RPC.format(host=self._pick_service_url())
        data = {
            'f.req': self._build_rpc_request(text, dest, src),
        }
        params = {
            'rpcids': RPC_ID,
            'bl': 'boq_translate-webserver_20201207.13_p0',
            'soc-app': 1,
            'soc-platform': 1,
            'soc-device': 1,
            'rt': 'c',
        }
        r = self.client.post(url, params=params, data=data)
        if r.status_code != 200 and self.raise_exception:
            raise Exception('Unexpected status code "{}" from {}'.format(
                r.status_code, self.service_urls))

        return r.text, r

    def _translate_legacy(self, text, dest, src, override):
        token = '' #dummy default value here as it is not used by api client
        if self.client_type == 'webapp':
            token = self.token_acquirer.do(text)

        params = utils.build_params(client=self.client_type, query=text, src=src, dest=dest,
                                    token=token, override=override)

        url = urls.TRANSLATE.format(host=self._pick_service_url())
        r = self.client.get(url, params=params)

        if r.status_code == 200:
            data = utils.format_json(r.text)
            return data, r

        if self.raise_exception:
            raise Exception('Unexpected status code "{}" from {}'.format(
                r.status_code, self.service_urls))

        DUMMY_DATA[0][0][0] = text
        return DUMMY_DATA, r

    def _parse_extra_data(self, data):
        response_parts_name_mapping = {
            0: 'translation',
            1: 'all-translations',
            2: 'original-language',
            5: 'possible-translations',
            6: 'confidence',
            7: 'possible-mistakes',
            8: 'language',
            11: 'synonyms',
            12: 'definitions',
            13: 'examples',
            14: 'see-also',
        }

        extra = {}

        for index, category in response_parts_name_mapping.items():
            extra[category] = data[index] if (
                index < len(data) and data[index]) else None

        return extra

    def translate(self, text: str, dest='en', src='auto'):
        """Translate text from source language to destination language
        Parameters
        ----------
        text : str, str sequence
            The source text(s) to be translated. Batch translation is supported via sequence input.
        dest : str
            The language to translate the source text into.
                 The value should be one of the language codes listed in `googleparser.LANGUAGES`
                 or in `googleparser.LANGCODES`.
        src: str
            The language of the source text.
                The value should be one of the language codes listed in `googleparser.LANGUAGES`
                or in `googleparser.LANGCODES`.
                If a language is not specified,
                the system will attempt to identify the source language automatically.
        Returns
        -------
        Translated
            Translated object with translation info
        """

        dest = dest.lower().split('_', 1)[0]
        src = src.lower().split('_', 1)[0]

        if src != 'auto' and src not in LANGUAGES:
            if src in SPECIAL_CASES:
                src = SPECIAL_CASES[src]
            elif src in LANGCODES:
                src = LANGCODES[src]
            else:
                raise ValueError('invalid source language')

        if dest not in LANGUAGES:
            if dest in SPECIAL_CASES:
                dest = SPECIAL_CASES[dest]
            elif dest in LANGCODES:
                dest = LANGCODES[dest]
            else:
                raise ValueError('invalid destination language')

        origin = text
        data, response = self._translate(text, dest, src)

        token_found = False
        square_bracket_counts = [0, 0]
        resp = ''

        for line in data.split('\n'):
            token_found = token_found or f'"{RPC_ID}"' in line[:30]
            if not token_found:
                continue

            is_in_string = False
            for index, char in enumerate(line):
                if char == '\"' and line[max(0, index - 1)] != '\\':
                    is_in_string = not is_in_string
                if not is_in_string:
                    if char == '[':
                        square_bracket_counts[0] += 1
                    elif char == ']':
                        square_bracket_counts[1] += 1

            resp += line
            if square_bracket_counts[0] == square_bracket_counts[1]:
                break
        data = json.loads(resp)
        parsed = json.loads(data[0][2])
        # not sure

        try:
            translated_parts = list(
                map(lambda part: TranslatedPart(part[0], part[1] if len(part) >= 2 else []), parsed[1][0][0][5]))
        except IndexError as e:
            translated_parts = list(map(lambda part: TranslatedPart(part[0], part[1] if len(part) >= 2 else []),
                                        [[parsed[1][0][0][0], [parsed[1][0][0][0]]]]))

        translated = ''.join(
            map(lambda part: part.text if part.text[-1] == ' ' else part.text + ' ', translated_parts))[:-1]

        if src == 'auto':
            try:
                src = parsed[2]
            except:
                pass
        if src == 'auto':
            try:
                src = parsed[0][2]
            except:
                pass

        # currently not available
        confidence = None

        origin_pronunciation = None
        try:
            origin_pronunciation = parsed[0][0]
        except:
            pass

        pronunciation = None
        try:
            pronunciation = parsed[1][0][0][1]
        except:
            pass

        extra_data = {
            'confidence': confidence,
            'parts': translated_parts,
            'origin_pronunciation': origin_pronunciation,
            'parsed': parsed,
        }
        result = Translated(src=src, dest=dest, origin=origin,
                            text=translated, pronunciation=pronunciation,
                            parts=translated_parts,
                            extra_data=extra_data,
                            response=response)
        return result

    def translate_legacy(self, text, dest='en', src='auto', **kwargs):
        dest = dest.lower().split('_', 1)[0]
        src = src.lower().split('_', 1)[0]

        if src != 'auto' and src not in LANGUAGES:
            if src in SPECIAL_CASES:
                src = SPECIAL_CASES[src]
            elif src in LANGCODES:
                src = LANGCODES[src]
            else:
                raise ValueError('invalid source language')

        if dest not in LANGUAGES:
            if dest in SPECIAL_CASES:
                dest = SPECIAL_CASES[dest]
            elif dest in LANGCODES:
                dest = LANGCODES[dest]
            else:
                raise ValueError('invalid destination language')

        if isinstance(text, list):
            result = []
            for item in text:
                translated = self.translate_legacy(item, dest=dest, src=src, **kwargs)
                result.append(translated)
            return result

        origin = text
        data, response = self.translate_legacy(text, dest, src)

        # this code will be updated when the format is changed.
        translated = ''.join([d[0] if d[0] else '' for d in data[0]])

        extra_data = self._parse_extra_data(data)

        # actual source language that will be recognized by Google Translator when the
        # src passed is equal to auto.
        try:
            src = data[2]
        except Exception:  # pragma: nocover
            pass

        pron = origin
        try:
            pron = data[0][1][-2]
        except Exception:  # pragma: nocover
            pass

        if pron is None:
            try:
                pron = data[0][1][2]
            except:  # pragma: nocover
                pass

        if dest in EXCLUDES and pron == origin:
            pron = translated

        # put final values into a new Translated object
        result = Translated(src=src, dest=dest, origin=origin,
                            text=translated, pronunciation=pron,
                            extra_data=extra_data,
                            response=response)

        return result

    def detect(self, text: str):
        """Detect language of the input text
        Parameters
        ----------
        text : str, str sequence
            The source text(s) whose language you want to identify.
        Returns
        -------
        Detected
            Detected object with detection info
        """

        translated = self.translate(text, src='auto', dest='en')
        result = Detected(lang=translated.src, confidence=translated.extra_data.get('confidence', None), response=translated._response)
        return result

    def detect_legacy(self, text, **kwargs):

        if isinstance(text, list):
            result = []
            for item in text:
                lang = self.detect(item)
                result.append(lang)
            return result

        data, response = self._translate_legacy(text, 'en', 'auto', kwargs)

        # actual source language that will be recognized by Google Translator when the
        # src passed is equal to auto.
        src = ''
        confidence = 0.0
        try:
            if len(data[8][0]) > 1:
                src = data[8][0]
                confidence = data[8][-2]
            else:
                src = ''.join(data[8][0])
                confidence = data[8][-2][0]
        except Exception:  # pragma: nocover
            pass
        result = Detected(lang=src, confidence=confidence, response=response)

        return result

    def translate_secure(self, text, retries=3):
        """ Securely translate text from source language to destination language
        Parameters
        ----------
        text : str, str sequence
            The source text(s) to be translated. Batch translation is supported via sequence input.
        retries : int
            number of retries to make request again
        Returns
        -------
        dict
            dictionary with 'text' - translated text and 'src' - source language
        """

        if not text:
            return {'text': '', 'src': ''}
        title_trans = ''
        for _ in range(retries):
            try:
                title_trans = self.translate(text[:5000], dest='en')
                break
            except Exception as error:
                # empty responses restart session
                self._reset()
        else:
            title_trans = Translated(src='', dest='', origin='',
                                     text='', pronunciation='',
                                     extra_data='',
                                     response='', parts=[])

        title_trans, title_lang = title_trans.text, title_trans.src

        for chunk in range(1, len(text) // 5000 + 1):
            for _ in range(retries):
                try:
                    title_trans += self.translate(text[chunk * 5000:5000 * (chunk + 1)], dest='en')['text']
                    break
                except Exception as error:
                    # empty responses restart session
                    self._reset()  # TODO REINIT
            else:
                return {'text': '', 'src': ''}
        return {'text': title_trans, 'src': title_lang}

    def _reset(self):
        self.client = httpx.Client(http2=True)

        self.token_acquirer = TokenAcquirer(client=self.client, host=self.service_urls[0])
