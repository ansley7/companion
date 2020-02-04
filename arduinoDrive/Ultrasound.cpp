#include "Arduino.h"
#include "Ultrasound.h"

Ultrasound::Ultrasound(int pin) : _pin(pin) {}

long Ultrasound::getDelay() {
  // Returns delay in ms

    pinMode(_pin, OUTPUT);
    digitalWrite(_pin, LOW);
    delayMicroseconds(2);
    digitalWrite(_pin, HIGH);
    delayMicroseconds(10);
    digitalWrite(_pin, LOW);

    pinMode(_pin, LOW);
    return pulseIn(_pin, HIGH);
}

long Ultrasound::getCm() {
    return msToCm(getDelay());
}

long Ultrasound::getInches() {
    return msToInches(getDelay());
}

static long Ultrasound::msToInches(long ms) {
    return ms / 74 / 2;
}

static long Ultrasound::msToCm(long ms) {
    return ms / 29 / 2;
}
