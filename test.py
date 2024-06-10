from wiktionaryparser import WiktionaryParser

parser = WiktionaryParser()
word = parser.fetch('plasma', 'english')
print(word)