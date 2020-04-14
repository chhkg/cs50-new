#include "helpers.h"
#include "stdio.h"
#include "math.h"

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
/*
    int n = round((image[0][0].rgbtRed + image[0][0].rgbtGreen + image[0][0].rgbtBlue) / 3);
    printf("R is %i, Green is %i, Blue is %i, Average is %i\n", image[0][0].rgbtRed, image[0][0].rgbtGreen, image[0][0].rgbtBlue, n);
    image[0][0].rgbtRed = image[0][0].rgbtGreen = image[0][0].rgbtBlue = n;
    printf("R is %i, Green is %i, Blue is %i, Average is %i\n", image[0][0].rgbtRed, image[0][0].rgbtGreen, image[0][0].rgbtBlue, n);
*/

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int n = round((image[i][j].rgbtRed + image[i][j].rgbtGreen + image[i][j].rgbtBlue) / 3);
            image[i][j].rgbtRed = image[i][j].rgbtGreen = image[i][j].rgbtBlue = n;
        }
    }
    return;
}


// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int sRed = round(.393 * image[i][j].rgbtRed + .769 * image[i][j].rgbtGreen + .189 * image[i][j].rgbtBlue);
            int sGreen = round(.349 * image[i][j].rgbtRed + .686 * image[i][j].rgbtGreen + .168 * image[i][j].rgbtBlue);
            int sBlue = round(.272 * image[i][j].rgbtRed + .534 * image[i][j].rgbtGreen + .131 * image[i][j].rgbtBlue);

            if (sRed > 255)
            {
                image[i][j].rgbtRed = 255;
            }
            else if (sRed < 0)
            {
                image[i][j].rgbtRed = 0;
            }
            else
            {
                image[i][j].rgbtRed = sRed;
            }

            if (sGreen > 255)
            {
                image[i][j].rgbtGreen = 255;
            }
            else if (sGreen < 0)
            {
                image[i][j].rgbtGreen = 0;
            }
            else
            {
                image[i][j].rgbtGreen = sGreen;
            }

            if (sBlue > 255)
            {
                image[i][j].rgbtBlue = 255;
            }
            else if (sBlue < 0)
            {
                image[i][j].rgbtBlue = 0;
            }
            else
            {
                image[i][j].rgbtBlue = sBlue;
            }
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2; j++)
        {
            RGBTRIPLE tem = image[i][j];
            image[i][j] = image[i][width - 1 - j];
            image[i][width - 1 - j] = tem;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j] = image[i][j];
        }
    }

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int bRed = 0;
            int bGreen = 0;
            int bBlue = 0;
            float pixel = 0;

            //[i][j] pixel
            bRed += copy[i][j].rgbtRed;
            bGreen += copy[i][j].rgbtGreen;
            bBlue += copy[i][j].rgbtBlue;
            pixel++;

            //upper left pixel
            if (i - 1 >= 0 && j - 1 >= 0)
            {
                bRed += copy[i - 1][j - 1].rgbtRed;
                bGreen += copy[i - 1][j - 1].rgbtGreen;
                bBlue += copy[i - 1][j - 1].rgbtBlue;
                pixel++;
            }

            //upper pixel
            if (i - 1 >= 0)
            {
                bRed += copy[i - 1][j].rgbtRed;
                bGreen += copy[i - 1][j].rgbtGreen;
                bBlue += copy[i - 1][j].rgbtBlue;
                pixel++;
            }

            //upper right pixel
            if (i - 1 >= 0 && j + 1 < width)
            {
                bRed += copy[i - 1][j + 1].rgbtRed;
                bGreen += copy[i - 1][j + 1].rgbtGreen;
                bBlue += copy[i - 1][j + 1].rgbtBlue;
                pixel++;
            }

            //left pixel
            if (j - 1 >= 0)
            {
                bRed += copy[i][j - 1].rgbtRed;
                bGreen += copy[i][j - 1].rgbtGreen;
                bBlue += copy[i][j - 1].rgbtBlue;
                pixel++;
            }

            //right pixel
            if (j + 1 < width)
            {
                bRed += copy[i][j + 1].rgbtRed;
                bGreen += copy[i][j + 1].rgbtGreen;
                bBlue += copy[i][j + 1].rgbtBlue;
                pixel++;
            }

            //lower left pixel
            if (i + 1 < height && j - 1 >= 0)
            {
                bRed += copy[i + 1][j - 1].rgbtRed;
                bGreen += copy[i + 1][j - 1].rgbtGreen;
                bBlue += copy[i + 1][j - 1].rgbtBlue;
                pixel++;
            }

            //lower pixel
            if (i + 1 < height)
            {
                bRed += copy[i + 1][j].rgbtRed;
                bGreen += copy[i + 1][j].rgbtGreen;
                bBlue += copy[i + 1][j].rgbtBlue;
                pixel++;
            }

            //lower right pixel
            if (i + 1 < height && j + 1 < width)
            {
                bRed += copy[i + 1][j + 1].rgbtRed;
                bGreen += copy[i + 1][j + 1].rgbtGreen;
                bBlue += copy[i + 1][j + 1].rgbtBlue;
                pixel++;
            }

            image[i][j].rgbtRed = round(bRed / pixel);
            image[i][j].rgbtGreen = round(bGreen / pixel);
            image[i][j].rgbtBlue = round(bBlue / pixel);

/*
            {
                int bRed = round((image[i][j].rgbtRed + image[i][j + 1].rgbtRed
                + image[i + 1][j + 1].rgbtRed + image[i + 1][j].rgbtRed) / 4)
            }


            if (i != 0 && j != 0)
            {
                int bRed = round((image[i][j].rgbtRed + image[i][j + 1].rgbtRed + image[i][j - 1].rgbtRed
                + image[i - 1][j + 1].rgbtRed + image[i - 1][j].rgbtRed + image[i - 1][j - 1].rgbtRed
                + image[i + 1][j + 1].rgbtRed + image[i + 1][j].rgbtRed + image[i + 1][j - 1].rgbtRed) / 9)
            }
            else if (i = 0 && j != 0)
            {
                int bRed = round((image[i][j].rgbtRed + image[i - 1][j + 1].rgbtRed + image[i - 1][j].rgbtRed + image[i - 1][j - 1].rgbtRed + image[i][j + 1].rgbtRed + image[i][j - 1].rgbtRed + image[i + 1][j + 1].rgbtRed + image[i + 1][j].rgbtRed + image[i + 1][j - 1].rgbtRed) / 9)
            }
*/
        }
    }
    return;
}
