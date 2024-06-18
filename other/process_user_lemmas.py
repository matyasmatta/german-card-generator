
class UnprocessedLemmaFile:
    def __init__(self, source: str, output: str):
        self.source = source
        self.output = output
        self.words = self.read_file()
        self.print_words()

    def read_file(self):
        with open(self.source, "r") as f:
            lines = f.readlines() 
            words = [word for word in lines[0].split() if len(word) >= 4]
        return words

    def print_words(self):
        with open(self.output, "a") as f:
            for item in self.words:
                f.write(item+"\n")

if __name__ == "__main__":
    file = UnprocessedLemmaFile("other/in.txt", "other/out.txt")