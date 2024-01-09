#include <bits/time.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <termios.h>
#include <unistd.h>


#ifndef DEBUG
#define DEBUG 0
#endif

const double g = 9.81;
const double PI = M_PI;
// m
const double R_RIM = 0.2;
const double R_DEFL = 0.1575;
// radians
const double ALPHA = 0.24702365;

struct state {
    double t0;
    double tRim;
    
    double Theta0;
    double DotTheta0;
    double dDotTheta0;

    double dotPhi;
};

void _GetBallSplits(double* ballSplit1, double* ballSplit2) {
    struct timespec ts0, ts1, ts2;

    getchar();
    clock_gettime(CLOCK_REALTIME, &ts0);
    printf("1. \n");

    getchar();
    clock_gettime(CLOCK_REALTIME, &ts1);
    printf("2. \n");
    
    getchar();
    clock_gettime(CLOCK_REALTIME, &ts2);
    printf("3. \n");
    
    *ballSplit1 = (double)(ts1.tv_sec - ts0.tv_sec) + (double)(ts1.tv_nsec - ts0.tv_nsec) / 1e9;
    *ballSplit2 = (double)(ts2.tv_sec - ts1.tv_sec) + (double)(ts2.tv_nsec - ts1.tv_nsec) / 1e9;
}
void _GetWheelSplits(double* wheelSplit) {
    struct timespec ts0, ts1;

    getchar();
    clock_gettime(CLOCK_REALTIME, &ts0);
    printf("1. \n");

    getchar();
    clock_gettime(CLOCK_REALTIME, &ts1);
    printf("2. \n");
    
    
    *wheelSplit = (double)(ts1.tv_sec - ts0.tv_sec) + (double)(ts1.tv_nsec - ts0.tv_nsec) / 1e9;
}

void GetInitialConditions(
        double ballSplit1,
        double ballSplit2, 
        double wheelSplit, 
        double p,
        struct state* spin) {

    if (DEBUG)
        printf("Splits (%f, %f, %f)\n", ballSplit1, ballSplit2, wheelSplit);

    // radians/s
    double speedLap1= p * (2 * PI) / ballSplit1;

    spin->t0 = 0;
    spin->Theta0 = 0;
    spin->DotTheta0 = p * (2 * PI) / ballSplit2;
    spin->dDotTheta0 = (spin->DotTheta0 - speedLap1) / ballSplit2;
    spin->dotPhi = (2 * PI) * wheelSplit;


    if (DEBUG)
        printf("Parameters (%f, %f, %f)\n", spin->Theta0, spin->DotTheta0, spin->dDotTheta0);
}

double RimMotion(struct state* spin) {
    double squareRoot = sqrt((g * tan(ALPHA))/R_RIM);
    double plus = spin->DotTheta0 + squareRoot;
    double minus = spin->DotTheta0 - squareRoot;
    plus = (-1/spin->dDotTheta0) * plus;
    minus = (-1/spin->dDotTheta0) * minus;

    // for now use plus case
    spin->tRim = plus;

    // theta leaving rim
    return sqrt((g * tan(ALPHA))/R_RIM);

}

double HittingDeflector(
        struct state* spin, 
        double dotThetaRim, 
        double dt) {

    double t = spin->tRim;
    double r = R_RIM;
    double dotR = 0;
    double dDotR = 0;

    // ??
    double dDotThetaRim = spin->dDotTheta0;

    while (r > R_DEFL) {

        dotThetaRim += dDotThetaRim * dt;
        dDotR += (
                r * dotThetaRim * dotThetaRim * cos(ALPHA) 
                - g * sin(ALPHA));
        dotR += dDotR * dt;
        r += dotR * dt;
        t += dt;
    }

    return t;
}

int GetSector(struct state* spin, double t_defl, int N) {
    double theta_defl = (
            spin->Theta0 + 
            spin->DotTheta0 * t_defl +
            spin->dDotTheta0 * t_defl * t_defl * 0.5
            );

    // Just for getting deflector
    if (!spin->dotPhi) {
        theta_defl = fmod(theta_defl, 2 * PI);
        return (int)(N * theta_defl / (2 * PI));
    }
    else {
        // FINISH
        return -1;
    }
}

void _EncodeSector(int result) {

}

int Predict(
        int N, double dt, int p, 
        double ballSplit1, double ballSplit2, double wheelSplit) {

    struct state spin;


    // Change for hardware integration
    if (!ballSplit1 || !ballSplit2)
        _GetBallSplits(&ballSplit1, &ballSplit2);
    if (!wheelSplit)
        _GetWheelSplits(&wheelSplit);

    GetInitialConditions(ballSplit1, ballSplit2, wheelSplit, p, &spin);

    double dotThetaRim = RimMotion(&spin);
    double t_defl = HittingDeflector(&spin, dotThetaRim, dt);
    int result = GetSector(&spin, t_defl, N);
    
    _EncodeSector(result);
    printf("Sector: %d", result);
    return result;

}


int main(int argc, char *argv[]) {
    // Default values
    int N = 8; // Default number of sectors
    double dt = 0.01; // Time increment for time stepping
    double p = 1.0; // Number of spins in each split
    double ballSplit1 = 0, ballSplit2 = 0, wheelSplit = 0;

    if (argc == 4 && !strcmp(argv[1], "--cli")) {
        // CLI mode without --wheel
        ballSplit1 = atof(argv[2]);
        ballSplit2 = atof(argv[3]);
        wheelSplit = -1;
    }
    else if (argc == 7 && !strcmp(argv[1], "--cli") && !strcmp(argv[2], "--wheel")) {
        // CLI mode with --wheel
        N = atoi(argv[3]);
        wheelSplit = atof(argv[4]);
        ballSplit1 = atof(argv[5]);
        ballSplit2 = atof(argv[6]);
    }
    else {
        fprintf(stderr, "Usage:\n"
                        "  %s\n"
                        "  %s --cli <ballSplit1> <ballSplit2>\n"
                        "  %s --cli --wheel <N> <wheelSplit> <ballSplit1> <ballSplit2>\n", 
                        argv[0], argv[0], argv[0]);
        return 1;
    }

    Predict(N, dt, p, ballSplit1, ballSplit2, wheelSplit);
    return 0;
}
