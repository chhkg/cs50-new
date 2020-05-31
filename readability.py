from cs50 import get_string

def main():
    text = get_string("Text: ")

    lc = count_letters(text);
    wc = count_words(text);
    sc = count_sentences(text);

    index = 0.0588 * (lc / wc) * 100 - 0.296 * (sc / wc) * 100 - 15.8

    if round(index) < 1:
        print("Before Grade 1")
    elif round(index) >= 16:
        print("Grade 16+")
    else:
        print(f"Grade {round(index)}")

def count_letters(paragraph):
    letter_c = 0
    for i in range(len(paragraph)):
        if (paragraph[i].isalpha()):
            letter_c += 1
    return letter_c

def count_words(paragraph):
    word_c = 1
    for i in range(len(paragraph)):
        if paragraph[i] == " ":
            word_c += 1
    return word_c

def count_sentences(paragraph):
    sentence_c = 0
    for i in range(len(paragraph)):
        if paragraph[i] in (".", "?", "!"):
            sentence_c += 1
    return sentence_c

main()