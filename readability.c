#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

int count_letters(string paragraph);
int count_words(string paragraph);
int count_sentences(string paragraph);

int main(void)
{
    string text = get_string("Text: ");

    int lc = count_letters(text);
    int wc = count_words(text);
    int sc = count_sentences(text);

    float index = 0.0588 * ((float) lc / (float) wc) * 100 - 0.296 * ((float) sc / (float) wc) * 100 - 15.8;

    if (round(index) < 1)
    {
        printf("Before Grade 1\n");
    }
    else if (round(index) >= 16)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %.0f\n", round(index));
    }



//    printf("%i letters\n", lc);
//    printf("%i words\n", wc);
//    printf("%i sentences\n", sc);
}


int count_letters(string paragraph)
{
    int letter_c = 0;

    for (int i = 0; i < strlen(paragraph); i++)
    {
        if (isalpha(paragraph[i]))
        {
            letter_c++;
        }
    }
    return letter_c;
}

int count_words(string paragraph)
{
    int word_c = 1;

    for (int i = 0; i < strlen(paragraph); i++)
    {
        if (paragraph[i] == ' ')
        {
            word_c++;
        }
    }
    return word_c;
}

int count_sentences(string paragraph)
{
    int sentence_c = 0;

    for (int i = 0; i < strlen(paragraph); i++)
    {
        if (paragraph[i] == '.' || paragraph[i] == '?' || paragraph[i] == '!')
        {
            sentence_c++;
        }
    }
    return sentence_c;
}