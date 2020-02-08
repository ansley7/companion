#include <Arduino_FreeRTOS.h>
#include "Ultrasound.h"
#include "MotorControl.h"

// Configurations
// The pwm for the motors
byte spd = 60;
// The distance in cm at which we try to avoid an object
const int STOP_DIST_CENTER = 15;
const int STOP_DIST_SIDE = 10;

/*  2DIAG, 2INA, 2INB, 2PWM, 2CS, VIN, GND, 5VIN, GND, VIN, 1CS, 1PWM, 1INB, 1INA, 1DIAG  */
// Motor ports
const int m_left_a = 11;
const int m_left_b = 10;
const int m_left_p = 6;
const int m_right_a = 13;
const int m_right_b = 2; // port 12 is kinda messed up so we moved to 2
const int m_right_p = 5;

// Ultrasonic ports
const int us_left_port = 7;
const int us_right_port = 8;
const int us_center_port = 4;

// State variables for the robot
// The most recent distance read from each ultrasonic
long leftDist=0, rightDist=0, centerDist=0;
// Whether to drive right now or not
bool do_drive = false;
// The number of iterations the loop polling the sensors had done
// used to lower spam in the console. 
int iter = 0;

// Construct the motor controllers
MotorControl mLeft(m_left_a, m_left_b, m_left_p);
MotorControl mRight(m_right_a, m_right_b, m_right_p);

// Construct the ultrasonics
Ultrasound usLeft(us_left_port);
Ultrasound usRight(us_right_port);
Ultrasound usCenter(us_center_port);

void setup() {
  Serial.begin(9600);
  xTaskCreate(drive,        (const portCHAR *) "Driving",         128, NULL, 1, NULL);
  xTaskCreate(updateOrders, (const portCHAR *) "Updating Orders", 128, NULL, 2, NULL);
  xTaskCreate(pollSensors,  (const portCHAR *) "Polling Sensors", 128, NULL, 3, NULL);
  halt(); // so we dont move when we start i guess. inA or inB might start high for some reason
}

/**
 * Polls the ultrasonic sensors and updates the distances each is reading.
 * Executed and scheduled by FreeRTOS. 
 */
void pollSensors(void *pvParameters) {
  while (1) {
    // get the distance each sensor is reading, in cm
    leftDist = usLeft.getCm();
    rightDist = usRight.getCm();
    centerDist = usCenter.getCm();

    iter += 1;
    // don't flood too much, only print every so often
    // 
    if (iter % 10 == 0) {
      iter = 0;
      // print the distances
      Serial.print("Dist: [");
      Serial.print(leftDist);
      Serial.print(", ");
      Serial.print(centerDist);
      Serial.print(", ");
      Serial.print(rightDist);
      Serial.println("]");

      // print whether each sensor detected an object
      Serial.print("Stop: [");
      Serial.print(leftDist <= STOP_DIST_SIDE);
      Serial.print(", ");
      Serial.print(centerDist <= STOP_DIST_CENTER);
      Serial.print(", ");
      Serial.print(rightDist <= STOP_DIST_SIDE);
      Serial.println("]");
    }

    // delay by 150ms
    vTaskDelay(150 / portTICK_PERIOD_MS);
  }
}

void drive(void *pvParameters) {
  while (1) {
    // freeroam. it just go (tm)
    if (do_drive) {
      // check if there's something in front of us
      if (centerDist <= STOP_DIST_CENTER) {
        // There is something in front of us, avoid
        // check if there's more space on the right
        if (leftDist < rightDist) {
          // more space on the right
          right();
        } else {
          // more space on the left
          left();
        }
      } else if (leftDist <= STOP_DIST_SIDE) {
        // nothing in front but something on the left
        right();
      } else if (rightDist <= STOP_DIST_SIDE) {
        // nothing in front but something on the right
        left();
      } else {
        // nothing to avoid, power on
        forward();
      }
    } else {
      // dont drive
      halt();
    }

    // delay by 50ms
    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}

/**
 * Updates the state of the robot with commands coming over serial.
 */
void updateOrders(void *pvParameters) {
  while (1) {
    if (Serial.available() > 0) {
      switch (Serial.read()) {
        case 'g':
          do_drive = true; 
          break;
        case 's':
          do_drive = false;
          break;
        default:
          break;
      }
    }

    // delay by 50ms
    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}

void loop() {
  // everything is run by RTOS, no need to use loop
}

/**
 * Sets the speed for the left and right motor.
 * Direction is set independently, so speed is unsigned.
 */
void set_speed(const unsigned int left, const unsigned int right) {
  mLeft.setPwm(left);
  mRight.setPwm(right);
}

/**
 * Stops both sides of the robot.
 */
void halt() {
  mLeft.halt();
  mRight.halt();
}

/**
 * Sets the speed of the robot, and sets each motor's direction so
 * the robot moves forward.
 */
void forward() {
  set_speed(spd, spd);
  mLeft.backward();
  mRight.forward();
}

/**
 * Sets the speed of the robot, and sets each motor's direction so
 * the robot moves backward.
 */
void backward() {
  set_speed(spd, spd);
  mLeft.forward();
  mRight.backward();
}

/**
 * Sets the speed of the robot, and sets each motor's direction so
 * the robot turns in place to the left.
 */
void left() {
  set_speed(spd, spd);
  mLeft.forward();
  mRight.forward();
}

/**
 * Sets the speed of the robot, and sets each motor's direction so
 * the robot turns in place to the right.
 */
void right() {
  set_speed(spd, spd);
  mLeft.backward();
  mRight.backward();
}
