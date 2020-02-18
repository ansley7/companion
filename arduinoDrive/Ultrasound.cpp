#include "Arduino.h"
#include "Ultrasound.h"

/**
 * Constructs an ultrasonic object, use the given pin to measure
 * distance in front of the sensor at the pin.
 */
Ultrasound::Ultrasound(int pin) : _pin(pin) {}

/**
 * Returns the delay from when the ping was sent to when it was
 * received, in ms. 
 */
long Ultrasound::getDelay() {
    pinMode(_pin, OUTPUT);
    digitalWrite(_pin, LOW);
    delayMicroseconds(2);
    digitalWrite(_pin, HIGH);
    delayMicroseconds(10);
    digitalWrite(_pin, LOW);

    pinMode(_pin, LOW);
    return pulseIn(_pin, HIGH);
}

/**
 * Gets the distance between the sensor and the nearest object,
 * in cm.
 */
long Ultrasound::getCm() {
    return msToCm(getDelay());
}

/**
 * Gets the distance between the sensor and the nearest object,
 * in inches.
 */
long Ultrasound::getInches() {
    return msToInches(getDelay());
}

long Ultrasound::msToInches(long ms) {
    return ms / 74 / 2;
}

long Ultrasound::msToCm(long ms) {
    return ms / 29 / 2;
}
