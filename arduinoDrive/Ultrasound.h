#ifndef Ultrasound_h
#define Ultrasound_h

#include "Arduino.h"

class Ultrasound {
    public:
    Ultrasound(int pin);
    long getCm();
    long getInches();
    static long msToInches(long ms);
    static long msToCm(long ms);

    private:
    long getDelay();
    int _pin;
};

#endif
