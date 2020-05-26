// Implements a dictionary's functionality

#include <stdbool.h>
#include <strings.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <cs50.h>
#include <ctype.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
const unsigned int N = 65536;

// Set initial global variable of the number of words in dictionary
int word_count = 0;

// Hash table
node *table[N];

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    /*
    char *lower_word = malloc(sizeof(strlen(word) + 1));
    if (malloc(sizeof(strlen(word))) == NULL)
    {
        unload();
        return false;
    }
    else
    {
        for (int i = 0; i < (strlen(word)); i++)
        {
            if (isupper(word[i]))
            {
                lower_word[i] = tolower(word[i]);
            }
            else
            {
                lower_word[i] = word[i];
            }
        }
    }
    */

    node *cursor = table[hash(word)];

    while (cursor != NULL)
    {
        if (strcasecmp(cursor->word, word) == 0)
        {
            return true;
        }
        else
        {
            cursor = cursor->next;
        }
    }
    return false;
}

// Hashes word to a number

/*
//reference: https://www.reddit.com/r/cs50/comments/1x6vc8/pset6_trie_vs_hashtable/
unsigned int hash(const char *word)
{
    unsigned int hash = 0;
    for (int i = 0, n = strlen(word); i < n; i++)
    {
        hash = (hash << 2) ^ word[i];
    }
    return hash % N;
}
*/

// reference: https://stackoverflow.com/questions/7666509/hash-function-for-string
unsigned int hash(const char *word)
{
    unsigned long hash = 5381;
    int c = 0;

    while ((c = *word++))
    {
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
    }
    return hash % N;
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // open the dictionary file
    FILE *file = fopen(dictionary, "r");
    if (!file)
    {
        return false;
    }

    // read every string from the file
    char word[LENGTH + 1];

    while (fscanf(file, "%s", word) != EOF)
    {
        // allocate memory for words
        node *new_node = malloc(sizeof(node));

        // check if memory is successfully allocated
        if (new_node == NULL)
        {
            unload();
            return false;
        }
        else
        {
            strcpy(new_node->word, word);

            word_count++;

            // insert dictionary words into hash table at that location
            int h = hash(new_node->word);

            if (table[h] == NULL)
            {
                table[h] = new_node;
                new_node->next = NULL;
            }
            else
            {
                new_node->next = table[h];
                table[h] = new_node;
            }
        }
    }
    fclose(file);
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    return word_count;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    for (int h = 0; h < N; h++)
    {
        node *cursor = table[h];

        while (cursor != NULL)
        {
            node *tmp = cursor;
            cursor = cursor->next;
            free(tmp);
        }
        free(cursor);
    }
    return true;
}