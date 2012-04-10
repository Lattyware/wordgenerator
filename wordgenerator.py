#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Copyright © 2012: Gareth Latty <gareth@lattyware.co.uk>

	wordgenerator.py

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

A small library/command line application that generates word-like strings from a
given input language using Markov chains.
"""

import argparse
import collections
import re
import random
import sys
import json
import itertools

class EmptyDictionaryError(Exception):
	def __str__(self):
		return "Before generating words, the word generator must be seeded " \
		       "with values from a language."

class WordGenerator:
	"""A generator for word-like strings that follow the 'feel' of a given input
	language.
	"""

	MARKER = "~"
	"""This is a marker character used to indicate the beginning or end of a
	word. It needs to not interfere with regular expressions, or be a character
	in words you in the language."""
	ENGLISH_VOWELS = {"a", "e", "i", "o", "u"}
	"""A set of the vowels for english."""

	def __init__(self, dictionary=None, language=None, weighted=True, vowels=ENGLISH_VOWELS):
		"""Creates a new, seeded WordGenerator. Provide one of dictionary or
		language.

		:param dictionary: A newline delimited file of words to use as a
		                   language.
		:param language: An iterator of words the language to seed the
		                 generator. Giving English words will produce
		                 English-like 'words' as output, likewise for other
		                 languages.
		:param weighted: If more common segments in the language are more likely
						 to appear in the output. This will make for more
						 realistic words, but also often less interesting.
		:param vowels: A set of the vowels for the input language.
		"""
		self.marker = WordGenerator.MARKER
		self.weighted = weighted
		if dictionary or language:
			self.seed(dictionary, language, vowels)

	def seed(self, dictionary=None, language=None, vowels=ENGLISH_VOWELS, append=False):
		"""Seed the generator with a set of words. Provide one of dictionary or
		language.

		:param dictionary: A newline delimited file of words to use as a
		                   language.
		:param language: An iterator of words the language to seed the
		                 generator. Giving English words will produce
		                 English-like 'words' as output, likewise for other
		                 languages.
		:param vowels: A set of the vowels for the input language.
		:param append: If true, add the given language to the current library -
		               this can be used to make amalgamation languages. If
		               false, replaces the current library with the new one.
		"""
		self.vowels = vowels
		self.vowels.add(WordGenerator.MARKER)
		self.regex = re.compile("([%]+)([^%]+)(?=([%]+))".replace("%", "".join(self.vowels)))
		if not append:
			self.components = collections.defaultdict(collections.Counter)
			self.starts = collections.Counter()
		if dictionary and not language:
			try:
				with open(dictionary, "r") as file:
					self.seed(language=file)
			except TypeError:
				self.seed(language=dictionary)
		elif language and not dictionary:
			for key, value in itertools.chain.from_iterable(
				(self.split_word(word) for word in
					(item.strip().lower() for item in language if item))):
				if key.startswith(WordGenerator.MARKER):
					self.starts[key] += 1
				self.components[key][value] += 1
			if self.weighted:
				self.components = {key: dict(value) for key, value in self.components.items()}
				self.starts = dict(self.starts)
			else:
				self.components = {key: list(value.keys()) for key, value in self.components.items()}
				self.starts = list(self.starts.keys())
		else:
			raise ValueError("One, and only one of dictionary and language may "
			"be passed to seed the word generator.")

	def _weighted_random_choice(self, choices):
		"""Provides a weighted random choice if the word generator is utilising
		a weighted library.

		:param choices: The choices to pick from.
		"""
		if self.weighted:
			max = sum(choices.values())
			pick = random.uniform(0, max)
			current = 0
			for key, value in choices.items():
				current += value
				if current > pick:
					return key
		else:
			return random.choice(choices)

	def split_word(self, word):
		"""Split a word into ``(vowels, not_vowels, more_vowels)`` triplets,
		adding :attr:`WordGenerator.MARKER` (which counts as a vowel) where
		needed to ensure that the word starts and ends with a 'vowel'.

		This returns a tuple of length 2, the first set of vowels followed by
		another tuple of 2 with the not vowels and more vowels.

		E.g: ``(vowels, (not_vowels, more_vowels)``.

		:param word: The word to split.
		"""
		word = WordGenerator.MARKER+word
		word += WordGenerator.MARKER

		for segment in self.regex.findall(word):
			key, *value = segment
			yield key, tuple(value)

	def _generate_word(self):
		"""Generate a single word. Don't use this, use :func:`generate_word()``
		instead.
		"""
		if not self.components:
			raise EmptyDictionaryError()

		word = ""
		current = self._weighted_random_choice(self.starts)
		while True:
			word += current
			if (current.endswith(WordGenerator.MARKER) and word != WordGenerator.MARKER):
				break
			next, current = self._weighted_random_choice(
				self.components[current])
			word += next
		word = word.strip(WordGenerator.MARKER)
		return word

	def generate_word(self, limit=None):
		"""Generate a single word.

		:param limit: Either a maximum length, or a tuple of ``(minimum,
		              maximum)``. Minimum is an absolute (no produced word will
		              be below the minimum), while maximum is a rough stopping
		              point (words may be longer).
		"""
		return next(self.generate(limit))

	def generate(self, limit, n=None):
		"""Generate random words.

		If you don't want your words limited, just iterate over the generator.
		If you want to limit your production, see itertools.islice.

		:param limit: Either a maximum length, or a tuple of ``(minimum,
		              maximum)``. Minimum is an absolute (no produced word will
		              be below the minimum), while maximum is a rough stopping
		              point (words may be longer).
		:param n: Produce n words, if ``None``, then produce infinitely.
		"""
		try:
			minimum, maximum = limit
		except TypeError:
			minimum = 0
			maximum = limit
		return itertools.islice((item for item in self if minimum < len(item) < maximum), n)

	def __iter__(self):
		"""Yields a random words."""
		while True:
			yield self._generate_word()

	def save(self, file):
		"""Save the library created from the seeds as JSON to the given file.
		This allows you to pre-process dictionaries and store the data in a
		simply compressed format, allowing quicker generation.

		:param file: The file to save to.
		"""
		components = {key: list(values.items()) for key, values in self.components.items()}
		starts = self.starts
		json.dump({"weighted": self.weighted, "starts": starts, "components": components}, file)

	def load(self, file):
		"""Load the library from a given JSON file.

		:param file: The file to load from.
		"""
		serialised = json.load(file)
		self.components = {key: {tuple(value): count for value, count in values} for key, values in serialised["components"].items()}
		self.starts = serialised["starts"]
		self.weighted = serialised["weighted"]

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="A generator for word-like "
	         "strings that follow the 'feel' of a given input language.")
	parser.add_argument("dictionary", type=argparse.FileType('r'),
	                    default=sys.stdin, nargs="?", metavar="FILE",
	                    help="The path to a dictionary file for a language - a "
	                         "list of newline separated words. "
	                         "(default: read from standard input)")
	parser.add_argument("-w", "--weighted", type=bool, default=True,
	                    metavar="BOOL",
	                    help="If true, a common segment in the language is"
	                         "more likely to show up in an output word. "
	                         "(default: %(default)s)")
	parser.add_argument("-n", "--number", type=int, default=1, metavar="N",
	                    help="The number of words to generate. "
	                         "(default: %(default)s)")
	parser.add_argument("--min", type=int, default=0, metavar="N",
	                    help="The minimum length of words to generate. "
	                         "(default: %(default)s)")
	parser.add_argument("-m", "--max", type=int, default=14, metavar="N",
	                    help="The rough maximum length of words to generate. "
	                         "(default: %(default)s)")
	parser.add_argument("-s", "--save", type=argparse.FileType('w'),
	                    metavar="FILE",
	                    help="Save the library to disc as JSON data. When "
	                         "saving, other operations will be ignored.")
	parser.add_argument("-o", "--output", action="store_const",
	                    const=sys.stdout, dest="save",
	                    help="Save the library, sending output to the standard "
	                         "output.")
	parser.add_argument("-l", "--load", type=argparse.FileType('r'),
	                    metavar="FILE",
	                    help="Load the library from JSON data on disc.")
	parser.add_argument('--version', action='version', version='%(prog)s 1.0')
	args = parser.parse_args()
	if args.load:
		generator = WordGenerator()
		generator.load(args.load)
	else:
		generator = WordGenerator(dictionary=args.dictionary, weighted=args.weighted)
	if args.save:
		generator.save(args.save)
	else:
		for word in generator.generate((args.min, args.max), args.number):
			print(word)

