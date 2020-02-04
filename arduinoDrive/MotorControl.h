class MotorControl {
    private:
    byte inA_pin;
    byte inB_pin;
    byte pwm_pin;

    /*byte inA_dir;
      byte inB_dir;*/
    int pwm_val;

    public:
    MotorControl(byte inA_pin, byte inB_pin, byte pwm_pin)
      : inA_pin(inA_pin), inB_pin(inB_pin), pwm_pin(pwm_pin) {
      pinMode(this->inA_pin, OUTPUT);
      pinMode(this->inB_pin, OUTPUT);
      pinMode(this->pwm_pin, OUTPUT);
    }

    void setPwm(int pwm_val) {
      this->pwm_val = pwm_val;
      analogWrite(this->pwm_pin, this->pwm_val);
    }

    void forward() {
      digitalWrite(this->inA_pin, HIGH);
      digitalWrite(this->inB_pin, LOW);
    }

    void backward() {
      digitalWrite(this->inA_pin, LOW);
      digitalWrite(this->inB_pin, HIGH);
    }

    void halt() {
      digitalWrite(this->inA_pin, LOW);
      digitalWrite(this->inB_pin, LOW);
    }
};
