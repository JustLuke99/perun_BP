#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#define I0 1e-12       //deklarace globalne promenne
#define UT 0.0258563        //deklarace globalne promenne

double ShockleyhovaRovnice(double u0, double r, double up)      //funkce vypocita Shockleyhovu rovnici
{
    double a = exp(1.0);       //vypocita Eulerovo cislo
    double b = up/UT;       //vypocita U_p/ut (ze vzorecku)
    double ShockVysledek = I0 * (pow(a,b) - 1) - (u0 - up) / r;     //vypocet vzorecku I0*(e^(up/ut)-1)-((u0-Up)/r)

    return ShockVysledek;      //vrati vypocitanou Shockleyhovu rovnici
}

double diode(double u0, double r, double eps) //funkce pro vypocitani up
{
    double a = u0;
    double b = 0.0;
    double stred = a / 2;       //vypocitani stredu funkce
    double ShockRovnice = ShockleyhovaRovnice(u0, r, stred);        //vyvolani funkce "ShockleyhovaRovnice"
    while (fabs(a - b) > eps)        //cyklus se bude opakovat dokud absolutni hodnota (a - b) nebude mensi nez eps
    {
        if (ShockleyhovaRovnice(u0, r, a) * ShockRovnice < 0)       //porovnava cisla(znamenka) s 0 a tím vybira stranu od stredu
        {
            b = stred;
        }
        else
        {
            a = stred;
        }
        if (fabs(a - b) > eps)       //kdyz (a - b) bude vyssi nez eps tak se urci novy stred, ktery se dosadi do rovnice
        {
            stred = (a + b) / 2;
            ShockRovnice = ShockleyhovaRovnice(u0, r, stred);
        }
    }
    return stred;
}

double Ip(double U_p)       //funkce Ip pro vypocitani Ip
{
    double I_p = I0 * (pow(exp(1.0),U_p/UT) - 1);       //vypocitani vzorecku I0*e^(Up/Ut)-1
    return I_p;     //vrati vypocitany Ip
}

int main(int argc, char *argv[])
{
    if(argc < 4 || argc > 4)       //kdyz argc se nebude rovnat 4 tak se vypise "..." a program se ukonci
    {
        printf("error: invalid arguments");
        return 3;
    }
    char *zbytek;
    double u0 = strtod(argv[1], &zbytek);       //kontrola jestli se v nactene hodnote nenachazi jiny znak nez cislo
    if(zbytek[0] != '\0')
    {
        printf("error: invalid arguments");
        return 0;
    }
    double r = strtod(argv[2], &zbytek);
    if(zbytek[0] != '\0')
    {
        printf("error: invalid arguments");
        return 1;
    }
    double eps = strtod(argv[3], &zbytek);
    if(zbytek[0] != '\0')
    {
        printf("error: invalid arguments");
        return 2;
    }
    if(u0 < 0 || r < 0 || eps < 0)       //kdyz u0, r nebo eps bude mensi 0 tak se vypise "..." a program se ukonci
    {
        printf("error: invalid arguments");
        return 4;
    }
    if(eps < 1e-15)     //ochrana proti preteceni double
    {
        eps = 1e-15;
    }
    double U_p = diode(u0, r, eps);     //vyvolani funkce "diode", ktera vypocita Up
    double I_p = Ip(U_p);       //vyvolani funkce Ip, ktera vypocita Ip diody
    printf("Up=%g V\nIp=%g A", U_p, I_p);       //vypisou se finalni hodnoty Up a Ip

    return 0;
}