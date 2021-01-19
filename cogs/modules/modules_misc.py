import discord
from discord.ext import commands
import re
from textblob import TextBlob as tb
import asyncio
from functools import partial
import csv
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix,classification_report
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
language_detection_model = None #This variable stores the model that will make predictions

# credit: https://gist.github.com/dperini/729294
_url = re.compile("""
            # protocol identifier
            (?:(?:https?|ftp)://)
            # user:pass authentication
            (?:\S+(?::\S*)?@)?
            (?:
              # IP address exclusion
              # private & local networks
              (?!(?:10|127)(?:\.\d{1,3}){3})
              (?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})
              (?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})
              # IP address dotted notation octets
              # excludes loopback network 0.0.0.0
              # excludes reserved space >= 224.0.0.0
              # excludes network & broacast addresses
              # (first & last IP address of each class)
              (?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])
              (?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}
              (?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))
            |
              # host name
              (?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)
              # domain name
              (?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*
              # TLD identifier
              (?:\.(?:[a-z\u00a1-\uffff]{2,}))
              # TLD may end with dot
              \.?
            )
            # port number
            (?::\d{2,5})?
            # resource path
            (?:[/?#]\S*)?
        """, re.VERBOSE | re.I)

_emoji = re.compile(r'<a?(:[A-Za-z0-9\_]+:|#|@|@&)!?[0-9]{17,20}>')

"""thanks to @Ryry013#9234"""
def is_emoji(char):
    EMOJI_MAPPING = (
        # (0x0080, 0x02AF),
        # (0x0300, 0x03FF),
        # (0x0600, 0x06FF),
        # (0x0C00, 0x0C7F),
        # (0x1DC0, 0x1DFF),
        # (0x1E00, 0x1EFF),
        # (0x2000, 0x209F),
        # (0x20D0, 0x214F),
        # (0x2190, 0x23FF),
        # (0x2460, 0x25FF),
        # (0x2600, 0x27EF),
        # (0x2900, 0x2935),
        # (0x2B00, 0x2BFF),
        # (0x2C60, 0x2C7F),
        # (0x2E00, 0x2E7F),
        # (0x3000, 0x303F),
        (0xA490, 0xA4CF),
        (0xE000, 0xF8FF),
        (0xFE00, 0xFE0F),
        (0xFE30, 0xFE4F),
        (0x1F000, 0x1F02F),
        (0x1F0A0, 0x1F0FF),
        (0x1F100, 0x1F64F),
        (0x1F680, 0x1F6FF),
        (0x1F910, 0x1F96B),
        (0x1F980, 0x1F9E0),
    )
    return any(start <= ord(char) <= end for start, end in EMOJI_MAPPING)


_loop = asyncio.get_event_loop()

"""thanks to @Ryry013#9234"""


def rem_emoji_url(msg):

    if isinstance(msg, discord.Message):
        msg = msg.content
    new_msg = _emoji.sub('', _url.sub('', msg))
    for char in msg:
        if is_emoji(char):
            new_msg = new_msg.replace(char, '').replace('  ', '')
    return new_msg


def _pre_load_language_dection_model():
    global language_detection_model
    english = []
    spanish = []
    for csv_name in ['principiante.csv', 'avanzado.csv', 'beginner.csv', 'advanced.csv']:
        with open(f"{dir_path}/cogs/modules/{csv_name}", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            if csv_name in ['principiante.csv', 'avanzado.csv']:
                for row in reader:
                    spanish.append(row[2])
            else:
                for row in reader:
                    english.append(row[2])

    def make_set(english, spanish, pipeline=None):
        if pipeline:
            eng_pred = pipeline.predict(english)
            sp_pred = pipeline.predict(spanish)
            new_english = []
            new_spanish = []
            for i in range(len(english)):
                if eng_pred[i] == 'en':
                    new_english.append(english[i])
            for i in range(len(spanish)):
                if sp_pred[i] == 'sp':
                    new_spanish.append(spanish[i])
            spanish = new_spanish
            english = new_english

        x = np.array(english + spanish)
        y = np.array(['en'] * len(english) + ['sp'] * len(spanish))

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.05, random_state=42)
        cnt = CountVectorizer(analyzer='char', ngram_range=(2, 2))

        pipeline = Pipeline([
            ('vectorizer', cnt),
            ('model', MultinomialNB())
        ])

        pipeline.fit(x_train, y_train)
        # y_pred = pipeline.predict(x_test)

        return pipeline

    language_detection_model = make_set(english, spanish, make_set(english, spanish, make_set(english, spanish)))


def detect_language(text):
    probs = language_detection_model.predict_proba([text])[0]
    if probs[0] > 0.9:
        return 'en'
    elif probs[0] < 0.1:
        return 'es'
    else:
        return None


async def load_language_dection_model():
    await _loop.run_in_executor(None, _pre_load_language_dection_model)

#Old language detection system

def _predetectblob(text):
    return tb(text).detect_language()

async def detect_languageblob(text):
    return await _loop.run_in_executor(None, partial(_predetectblob, text))