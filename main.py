import re
from wiktionaryparser import WiktionaryParser

def clean_text(text: str) -> str:
    text = text.split("\t")[0]
    # Remove content within brackets along with the brackets
    text = re.sub(r'\([^)]*\)', '', text)
    # Remove underdot accent marks while keeping umlaut marks
    text = re.sub(r'[\u0323]', '', text)
    # Remove stuff after comma
    text = text.split(",")[0].replace("|", "")
    # Remove article for nouns
    text = re.sub(r'^(der|die|das)\s+', '', text, flags=re.IGNORECASE)
    if len(text.split(" ")) > 2:
        return ""
    else:
        return text.strip().replace("/n", "").replace(" sich", "")

def format_source(file: str, output) -> list:
    with open(file, "r") as f:
        lines = f.readlines()
        lemmas = [clean_text(item) for item in lines]
        lemmas = sorted(list(set(lemmas)))
    
    if output: 
        with open(output, "w", encoding="utf8") as file:
            for item in lemmas:
                file.write("%s\n" % item)
    
    return lemmas