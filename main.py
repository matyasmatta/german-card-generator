import re
from wiktionaryparser import WiktionaryParser
import csv
from tqdm import tqdm
# Due to issues with the wiktionaryparser, a custom one needs to be used from user @pragma-
# You need to install it via "pip install -e /workspaces/german-card-generator/WiktionaryParser" in Terminal

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

def format_translation(translation: str):
    if "(" in translation:
        current_translation = translation.split(" ")
        search = False
        searched_item = str()
        for item in current_translation:
            if "(" in item and ")" in item:
                searched_item = item[1:-1]
                search = False
                break
            elif "(" in item:
                searched_item += item + " "
                search = True
            elif ")" in item:
                searched_item += item
                search = False
                break
            elif search:
                searched_item += item + " "
        searched_item = searched_item.replace("(", "").replace(")","")
        searched_item = searched_item.strip()
            
        return translation.replace(f"({searched_item})", ""), searched_item
    else:
        return translation, None

def get_translation(word: dict) -> str:
    def handle_duplicates(definitions: list) -> list:
        return list(set(definitions))
    
    def handle_additionals(additionals: list) -> str:
        try:
            for item in additionals:
                if not item:
                    return None
                else:
                    if "transitive" in item:
                        return item
                    elif len(item.split(" ")) < 2:
                        return item
            return None
        except:
            return None

    def convert_into_html(definitions: list) -> str:
        def correct_verb(temporary_hold: str) -> str:
            temporary_hold = temporary_hold.strip()
            if "to " in temporary_hold:
                result = ""
                for item in temporary_hold.split(" "):
                    if "to " in result:
                        if item == "to":
                            pass
                        else:
                            result += item+" "
                    else:
                        result += item+" "
                result = result.strip()
                return result
            else:
                return temporary_hold
            
        def correct_hold(hold: str) -> str:
            result = hold.strip().replace("  ", " ")
            result = result[:-1] if result.endswith(",") else result
            return result
            
        html_list = "<ul>" 
        temporary_hold = ""
        for item in definitions:
            temporary_hold += correct_verb(item) + ", "
            if len(temporary_hold.split(" ")) > 5: # the higher this integer, the fewer HTML lists in the result
                temporary_hold = correct_hold(correct_verb(temporary_hold))
                html_list += f"  <li>{temporary_hold}</li>" if temporary_hold not in html_list else ""
                final_hold = temporary_hold
                temporary_hold = ""
            else:
                final_hold = correct_hold(temporary_hold)

        try:
            if not final_hold in html_list:
                html_list += f"  <li>{final_hold}</li>"
        except:
            raise ValueError("There was some error inside the convert_into_html() function, please inspect.")
        if html_list.count("<li>") <= 1:
            return final_hold.strip()
        else:
            html_list += "</ul>"
            return html_list

    definitions = []
    for item in word[0]['definitions']:
        for i in range(len(item['text'])):
            if i == 0:
                pass
            else:
                if len(item['text'][i].split(" ")) > 20:
                    pass
                else:
                    definitions.append(item['text'][i])
    definitions2, additionals = [], []
    for item in definitions:
        translation, additional = format_translation(item)
        definitions2.append(translation)
        additionals.append(additional)

    definitions2 = handle_duplicates(definitions2)
    if len(definitions2) > 1:
        definitions2 = convert_into_html(definitions2)
    else:
        definitions2 = str(definitions2[0])

    return definitions2, handle_additionals(additionals)

def format_wordtype(wordtype: str) -> str:
    map = {
        "noun": "N",
        "verb": "V",
        "adjective": "Adj",
        "adverb": "Adv",
        "conjunction": "Conj",
        "preposition": "Prep",
        "pronoun": "Pron",
        "numeral": "Num" 
    }
    return map[wordtype]

def determine_gender(word: list) -> str:
    original_string = word[0]['definitions'][0]['text'][0].replace("\xa0", " ")
    if word[0]['definitions'][0]['partOfSpeech'].split(" ")[0] != "noun":
        return None
    try:
        current_string = original_string.replace(original_string.split(" ")[0]+" ", "")
        if current_string.split(" ")[1] == "or":
            return "m/f"
        else:
            splitted = current_string.split(" ")[0]
            if any(gender in splitted for gender in ("m", "f", "n")):
                return current_string.split(" ")[0]
            else:
                return None
    except:
        return None

def push_data(data: list, output) -> bool:
    with open(output, "a",  encoding="utf8", newline="") as f:
        csv.writer(f).writerow(data)

def format_lemma(lemma: str, wordtype: str, gender: str) -> str:
    match wordtype:
        case "N":
            match gender:
                case "m":
                    return f"der {lemma}"
                case "f":
                    return f"die {lemma}"
                case "n":
                    return f"das {lemma}"
        case _:
            return lemma

def process_lemmas(file: str) -> bool:
    with open(file, "r") as f:
        items = f.readlines()
    for item in tqdm(items):
        data = get_lemma(item.replace("\n",""))
        if data: push_data(data, "out.csv")

def get_lemma(lemma):
    try:
        parser = WiktionaryParser()
        word = parser.fetch(lemma, "german")
        wordtype = format_wordtype(word[0]['definitions'][0]['partOfSpeech'].split(" ")[0])
        formatted_translation, meaning_hint = get_translation(word)
        gender = determine_gender(word)
        formatted_lemma = format_lemma(lemma, wordtype, gender)
        return [formatted_lemma, formatted_translation, wordtype, meaning_hint, gender] if formatted_lemma else None
    except:
        return None

process_lemmas("out.txt")