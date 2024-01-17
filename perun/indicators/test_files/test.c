#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int rows;
    int cols;
    unsigned char *cells;
} Map;

void tiskHelp()
{
    printf("--test zkontroluje, ze soubor dany druhym argumentem programu obsahuje radnou definici\n--rpath hleda pruchod bludistem na vstupu na radku R a sloupci C. Pruchod hleda pomoci pravidla prave ruky (prava ruka vzdy na zdi).\n--lpath hleda pruchod bludistem na vstupu na radku R a sloupci C, ale za pomoci pravidla leve ruky.\n");
}

Map inicializaceMapy(Map *mapa,char *argv[])
{
    if(argv[2] == NULL)
    {
        mapa->rows = -42;
        return *mapa;
    }
    FILE * fp = fopen(argv[2], "r");
    if(fp == NULL)
    {
        mapa->rows = -42;
        return *mapa;
    }
    char Prevod[3];
    char kontrola;
    for(int i = 0; i < 2;i++)
    {
        Prevod[i] = -42;
        fscanf(fp, "%s", &Prevod[i]);
        if(Prevod[i] == -42)
        {
            mapa->rows = -42;
            return *mapa;
        }
        kontrola = Prevod[i];
        if((int)kontrola > 57 || (int)kontrola < 48)
        {
            mapa->rows = -42;
            return *mapa;
        }
        if(i == 0)
        {
            mapa->rows = atol(&Prevod[i]);
        }
        if(i == 1)
        {
            mapa->cols = atol(&Prevod[i]);
        }
    }
    mapa->cells = malloc(mapa->rows * mapa->cols * sizeof(unsigned char));

    return *mapa;
}

Map nacteniMapy(Map *mapa, char *argv[])
{
    char Prevod[mapa->rows*mapa->cols+1];
    char kontrola;
    int i = 0;
    FILE * fp = fopen(argv[2], "r");
    while(fscanf(fp, "%s", &Prevod[i]) != EOF)
    {
        kontrola = Prevod[i];
        if((int)kontrola > 57 || (int)kontrola < 48)
        {
            mapa->rows = -42;
            return *mapa;
        }
        if(i >= 2)
        {
            mapa->cells[i-2] = Prevod[i];
        }
        i++;
    }
    if(mapa->rows * mapa->cols != i - 2)
    {
        mapa->rows = -42;
        return *mapa;
    }
    return *mapa;
}

Map uvolneniMapy(Map *mapa)
{
    free(mapa->cells);
    mapa->cells = NULL;
    mapa->rows = 0;
    mapa->cols = 0;

    return *mapa;
}

bool isborder(Map *mapa, int r, int c, int border)
{
    char cisloNaPozici = mapa->cells[mapa->cols*(r-1)+c-1];
    printf("", cisloNaPozici);
    if(border == 0)
    {
        if(cisloNaPozici == '1' || cisloNaPozici == '3' || cisloNaPozici == '5' || cisloNaPozici == '7')
        {
            return true;
        }
    }
    if(border == 1)
    {
        if(cisloNaPozici == '2' || cisloNaPozici == '3' || cisloNaPozici == '6' || cisloNaPozici == '7')
        {
            return true;
        }
    }
    if(border == 2)
    {
        if(cisloNaPozici == '4' || cisloNaPozici == '5' || cisloNaPozici == '6' ||  cisloNaPozici == '7')
        {
            return true;
        }
    }

    return false;
}

bool kontrolazZdi(Map *mapa)
{
    for(int i = 1;i < mapa->rows;i++)
    {
        for(int j = 1; j < mapa->cols;j++)
        {
            bool A = isborder(mapa, i, j, 1);
            bool B = isborder(mapa, i, j+1, 0);
            if(A != B)
            {
                return false;
            }
            if(i % 2 == 0)
            {
                if(i != mapa->rows)
                {
                    if(j % 2 == 0)
                    {
                        bool A = isborder(mapa, i, j, 3);
                        bool B = isborder(mapa, i-1, j, 3);
                        if(A != B)
                        {
                            return false;
                        }
                    }
                    else
                    {
                        bool A = isborder(mapa, i, j, 3);
                        bool B = isborder(mapa, i+1, j, 3);
                        if(A != B)
                        {
                            return false;
                        }
                    }
                }
                else
                {
                    bool A = isborder(mapa, i, j, 3);
                    bool B = isborder(mapa, i-1, j, 3);
                    if(A != B)
                    {
                        return false;
                    }
                }
            }
        }
    }

    return true;
}

int start_border(Map *map, int r, int c, int leftright)
{
    printf("%i, %i, %i\n",r,c,leftright);

    return 0;
}

int main(int argc, char *argv[])
{
    Map mapa;
    if(strcmp(argv[1], "--help") == 0)
    {
        if(argc > 2)
        {
            fprintf( stderr, "error: spatny pocet argumentu\n");
            return 1;
        }
        tiskHelp();
    }
    if(strcmp(argv[1], "--test") == 0)
    {
        mapa = inicializaceMapy(&mapa, argv);
        if(mapa.rows == -42)
        {
            fprintf(stderr, "Invalid");
            return 2;
        }
        mapa = nacteniMapy(&mapa, argv);
        if(mapa.rows == -42)
        {
            fprintf(stderr, "Invalid");
            return 3;
        }
        bool Zed = kontrolazZdi(&mapa);
        if(Zed == false)
        {
            fprintf(stderr, "Zdi nesouhlasi");
            return 4;
        }
        else
        {
            printf("Zdi souhlasi\n");
        }
        mapa = uvolneniMapy(&mapa);
        printf("Valid");
    }
    if(strcmp(argv[1], "--lpath") == 0)
    {
        mapa = inicializaceMapy(&mapa, argv);
        mapa = nacteniMapy(&mapa, argv);
        int pozice1 = atol(argv[2]);
        int pozice2 = atol(argv[3]);
        int zacatecniPozice = start_border(&mapa, pozice1, pozice2, 0);
        printf("baf\n");

        mapa = uvolneniMapy(&mapa);
    }
    if(strcmp(argv[1], "--rpath") == 0 || strcmp(argv[1], "--lpath") == 0)
    {
        int ruka;
        if(strcmp(argv[1], "--rpath") == 0)
        {
            ruka = 0;
        }
        else
        {
            ruka = 1;
        }
        mapa = inicializaceMapy(&mapa, argv);
        mapa = nacteniMapy(&mapa, argv);
        int pozice1 = atol(argv[2]);
        int pozice2 = atol(argv[3]);

        int zacatecniPozice = start_border(&mapa, pozice1, pozice2, ruka);


        mapa = uvolneniMapy(&mapa);
    }

    return 0;
}
