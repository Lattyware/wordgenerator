# wordgenerator.py v1.0

A generator for word-like strings that follow the 'feel' of a given input
language.

## Requirements:

* [Python 3.x](http://www.python.org/)

## Usage:

This program functions both as a library and a command line application.

You will need a dictionary to use this program - a newline delimited list of
words to use as a source. Surprisingly good results can be obtained from very
small input dictionaries, but best results will be gained from a good, varied
selection from the language you wish to emulate. Linux users will often find
good samples in /usr/share/dict. british-english - distributed with this, is
taken from Arch Linux's
[words package](https://www.archlinux.org/packages/community/any/words/), and
the associated wbritish.copyright is taken from the same package and provides
information on copyright with regards to that file.

Saving as JSON means that you don't need to do the expensive parsing of the
dictionary again, and with large dictionaries will produce smaller files. If you
intend to use the generator with the same input dictionary multiple times, doing
this is highly reccomended.

### As a command line application:

For usage as a command line application, see the below explanation of arguments:

usage: wordgenerator.py [-h] [-w BOOL] [-n N] [--min N] [-m N] [-s FILE] [-o]
                        [-l FILE] [--version]
                        [FILE]

positional arguments:
  FILE                  The path to a dictionary file for a language - a list
                        of newline separated words. (default: read from
                        standard input)

optional arguments:
  -h, --help            show this help message and exit
  -w BOOL, --weighted BOOL
                        If true, a common segment in the language ismore
                        likely to show up in an output word. (default: True)
  -n N, --number N      The number of words to generate. (default: 1)
  --min N               The minimum length of words to generate. (default: 0)
  -m N, --max N         The rough maximum length of words to generate.
                        (default: 14)
  -s FILE, --save FILE  Save the library to disc as JSON data. When saving,
                        other operations will be ignored.
  -o, --output          Save the library, sending output to the standard
                        output.
  -l FILE, --load FILE  Load the library from JSON data on disc.
  --version             show program's version number and exit

### As a library:

Example usage:

```python
from wordgenerator import WordGenerator

generator = WordGenerator("british-english")
for word in generator.generate((10, 15), 10): #Generate 10 words of length 10-15.
	print(word)

with open("british-english.json", 'w') as file:
	generator.save(file) #Save the dictionary to a JSON file for quick usage later.
```

```python
from wordgenerator import WordGenerator
from itertools import islice

generator = WordGenerator()
with open("british-english.json", 'r') as file:
	generator.load(file) #Load from JSON.

for word in islice(generator, 25): #Get 25 words.
	print(word)
```

## Authors:

* Gareth Latty <gareth@lattyware.co.uk>

## Licence:

Copyright © 2012: Gareth Latty <gareth@lattyware.co.uk>

This script is provided under the GPLv3 licence, see LICENCE  or
http://www.gnu.org/licenses/ for more.