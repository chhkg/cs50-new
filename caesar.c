#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

int main(int argc, string argv[])
{
    if (argc != 2)
    {
        printf("missing command-line argument\n");
        return 1;
    }

    for (int i = 0; i < strlen(argv[1]); i++)
    {
        if (! isdigit(argv[1][i]))
        {
        printf("Usage: ./caesar\n");
        return 1;
        }
    }

    int k = atoi(argv[1]);

    string plaintext = get_string("plaintext: ");
    printf("ciphertext: ");

    for (int j = 0; j < strlen(plaintext); j++)
    {
        if (isalpha(plaintext[j]) && isupper(plaintext[j]))
        {
            printf("%c", ((plaintext[j] - 64 + k) % 26 + 64));
        }
        else if (isalpha(plaintext[j]) && islower(plaintext[j]))
        {
            printf("%c", ((plaintext[j] - 96 + k) % 26 + 96));
        }
        else
        {
            printf("%c", plaintext[j]);
        }
    }

    printf("\n");
}