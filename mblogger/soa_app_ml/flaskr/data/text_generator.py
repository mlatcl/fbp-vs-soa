import random
import itertools as it
from typing import List, Dict

from mblogger.record_types import BigramWithWeight

POST_START_WORD = "^"
PERSONAL_WORDS_WEIGHT = 10.0


class TextGenerator:
    def __init__(self, bigram_weights: List[BigramWithWeight]):
        self._create_bigram_dicts(bigram_weights)

    def _create_bigram_dicts(self, bigram_weights):
        self._bigrams_dict = {}
        self._bigram_weights_dict = {}

        for bigram_weight in bigram_weights:
            lhs = bigram_weight.first_word
            rhs = bigram_weight.second_word

            if lhs not in self._bigrams_dict:
                self._bigrams_dict[lhs] = set()
            self._bigrams_dict[lhs].add(rhs)

            if (lhs, rhs) not in self._bigram_weights_dict:
                self._bigram_weights_dict[lhs, rhs] = 0
            self._bigram_weights_dict[lhs, rhs] += bigram_weight.weight

    def _word_generator(self, personal_words):
        current_word = POST_START_WORD

        while True:
            next_words = list(self._bigrams_dict.get(current_word, []))
            next_weights = [
                (PERSONAL_WORDS_WEIGHT if next_word in personal_words else 1.0)
                * self._bigram_weights_dict[current_word, next_word]
                for next_word in next_words
            ]
            if not next_words:
                return

            next_word = random.choices(next_words, weights=next_weights)[0]
            current_word = next_word
            yield current_word

    def generate(self, personal_words: Dict, word_count: int):
        text = " ".join(it.islice(self._word_generator(personal_words), word_count))

        return text
