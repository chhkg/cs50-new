#include <cs50.h>
#include <stdio.h>
#include <math.h>

int main(void)
{
    float change;
    do
    {
        change = get_float("Change owed: ");
    }
    while (change < 0);
    int c = round(change * 100);
    int q = c / 25;
    int d = c % 25 / 10;
    int n = c % 25 % 10 / 5;
    int p = c % 25 % 10 % 5;
    printf("%i\n", q + d + n + p);
}
