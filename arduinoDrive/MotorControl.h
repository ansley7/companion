#ifndef MOTORCONTROL_H
#define MOTORCONTROL_H
/**
 * A class to control one side of a Pololu MD03A motor driver, or equivalent.
 * 
 * Stores the A, B and PWM pin of the given motor, and presents a
 * simple interface to the user: forward, backward, halt and set
 * speed. 
 * 
 * TODO: Store inversion so forward() moves forward relative to
 * the robot instead of CW/CCW?
 * TODO: Add encoders for closed loop control?
 */
class MotorControl {
    private:
    byte inA_pin;
    byte inB_pin;
    byte pwm_pin;

    /*byte inA_dir;
      byte inB_dir;*/
    int pwm_val;

    public:
    /**
     * Constructs a motor object, with the A, B and PWM pins.
     * 
     * Sets each of the given pins to OUTPUT mode. 
     */
    MotorControl(byte inA_pin, byte inB_pin, byte pwm_pin)
      : inA_pin(inA_pin), inB_pin(inB_pin), pwm_pin(pwm_pin) {
      pinMode(this->inA_pin, OUTPUT);
      pinMode(this->inB_pin, OUTPUT);
      pinMode(this->pwm_pin, OUTPUT);
    }

    /**
     * Sets the speed for the motor to run at. 
     */
    void setPwm(int pwm_val) {
      this->pwm_val = pwm_val;
      analogWrite(this->pwm_pin, this->pwm_val);
    }

    /**
     * Sets the motor to turn clockwise at the speed set by
     * setPWM().
     * 
     * Clockwise ends up as forward for motors pointing 
     * right/on the right.
     */
    void forward() {
      digitalWrite(this->inA_pin, HIGH);
      digitalWrite(this->inB_pin, LOW);
    }

    /**
     * Sets the motor to turn counter clockwise at the speed set by
     * setPWM().
     * 
     * Counter clockwise ends up as backward for motors pointing 
     * right/on the right.
     */
    void backward() {
      digitalWrite(this->inA_pin, LOW);
      digitalWrite(this->inB_pin, HIGH);
    }

    /**
     * Sets the motor to stop moving. 
     * 
     * Does not zero the speed of the motor, so a subsequent 
     * call to forward() or backward() will resume at the previously
     * set speed. 
     */
    void halt() {
      digitalWrite(this->inA_pin, LOW);
      digitalWrite(this->inB_pin, LOW);
    }
};
#endif