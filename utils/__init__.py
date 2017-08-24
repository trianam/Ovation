# We put here the default parameters for all datasets. For these parameters, we
# precreated the datasets and organized them already in a directory structure.
#
import os
import re
import spacy
import tflearn
import collections
from nltk.tokenize import word_tokenize as nltk_tokenizer

shuffle = True
stratified = True
train_validate_split = 0.9
test_split_large = 0.3
test_split_small = 0.2
data_root_directory = os.path.join('scratch', 'OSA-alpha', 'datasets')
spacy_nlp = spacy.load('en_core_web_md')
spacy_tokenizer = spacy_nlp.tokenizer


def tokenize(sentence):
    return [i for i in re.split(r"([-.\"',:? !\$#@~()*&\^%;\[\]/\\\+<>\n=])",
                                sentence) if i!='' and i!=' ' and i!='\n']

def padseq(data):
    if self.pad == 0:
        return data
    else:
        return tflearn.data_utils.pad_sequences(data, maxlen=self.pad,
                dtype='int32', padding='post', truncating='post', value=0)


def id2seq(data, i2w):
    buff = []
    for seq in data:
        w_seq = []
        for term in seq:
            if term in i2w:
                if term == 0 or term == 1 or term == 2:
                    continue
                w_seq.append(i2w[term])
        sent = ' '.join(w_seq)
        buff.append(sent)
    return buff


def seq2id(data, w2i, seq_begin=False, seq_end=False):
    buff = []
    for seq in data:
        id_seq = []
        if seq_begin: id_seq.append(w2i['SEQ_BEGIN'])
        for term in seq:
            if term in w2i:
                id_seq.append(w2i[term])
            else:
                id_seq = [w2i['UNK']]
        if seq_end: id_seq.append(w2i['SEQ_BEGIN'])
        buff.append(id_seq)
    return buff


def vocabulary_builder(data_path, min_frequency=5, tokenizer='spacy',
                       downcase=True, max_vocab_size=None):
    cnt = collections.Counter()

    for line in open(data_path, 'r'):
        tokens = []
        if downcase:
            line = line.lower()

        line = " ".join(line.split('\t')[:2])
        if tokenizer == 'spacy':
            doc = spacy_tokenizer(line)
            for token in doc:
                tokens.append(token)
        elif tokenizer == 'nltk':
            tokens = nltk_tokenizer(line)
        else:
            tokens = tokenize(line)
        tokens = [_ for _ in tokens if len(_) > 0]
        cnt.update(tokens)

    print("Found %d unique tokens in the vocabulary.", len(cnt))

    # Filter tokens below the frequency threshold
    if min_frequency > 0:
        filtered_tokens = [(w, c) for w, c in cnt.most_common()
                           if c > min_frequency]
        cnt = collections.Counter(dict(filtered_tokens))

    print("Found %d unique tokens with frequency > %d.",
          len(cnt), min_frequency)

    # Sort tokens by 1. frequency 2. lexically to break ties
    word_with_counts = cnt.most_common()
    word_with_counts = sorted(
            word_with_counts, key=lambda x: (x[1], x[0]), reverse=True)

    # Take only max-vocab
    if max_vocab_size is not None:
        word_with_counts = word_with_counts[:max_vocab_size]

    return word_with_counts

from .microsoft_paraphrase_dataset import MicrosoftParaphraseDataset
from .sts_all import STSAll
#from gersen import Gersen

