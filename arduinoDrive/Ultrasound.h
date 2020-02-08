#ifndef Ultrasound_h
#define Ultrasound_h

#include "Arduino.h"

/**
 * A class that can attached to a pin that is connected to an
 * ultrasonic sensor, and abstracts the functionality into nice
 * getters. 
 */
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
