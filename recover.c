#include <stdio.h>
#include <cs50.h>
#include <stdlib.h>
#include <stdint.h>

int main(int argc, char *argv[])
{
    //Open memory card
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }

    FILE *file = fopen(argv[1], "r");
    if (!file)
    {
        return 1;
    }

    //Read 512 bytes into a buffer
    int counter = 0;
    uint8_t buffer[512];
    FILE *img = NULL;
    char filename[10];

    while (fread(buffer, sizeof(buffer), 1, file) == 1)
    {
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            //If first JPEG
            if (counter == 0)
            {
                //open a new file
                sprintf(filename, "%03i.jpg", counter);
                img = fopen(filename, "w");

                //write the array into the new file
                fwrite(buffer, sizeof(buffer), 1, img);
                counter++;
            }

            //if not first JPEG
            else
            {
                //close the file
                fclose(img);

                //open a new file
                sprintf(filename, "%03i.jpg", counter);
                img = fopen(filename, "w");

                //write the array into the new file
                fwrite(buffer, sizeof(buffer), 1, img);
                counter++;
            }
        }
        //Else, if already found new JPEG
        else
        {
            if (img != NULL)
            {
                fwrite(buffer, sizeof(buffer), 1, img);
            }
        }
    }

    //Close any remaining files
    fclose(file);
    fclose(img);

    return 0;
}