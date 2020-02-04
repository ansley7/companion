#include <Arduino_FreeRTOS.h>
#include "Ultrasound.h"
#include "MotorControl.h"

byte spd = 60;
const int STOP_DIST_CENTER = 15;
const int STOP_DIST_SIDE = 10;

long leftDist, rightDist, centerDist;

const int m_left_a = 11;
const int m_left_b = 10;
const int m_left_p = 6;
const int m_right_a = 13;
const int m_right_b = 12;
const int m_right_p = 5;

const int us_left_port = 7;
const int us_right_port = 8;
const int us_center_port = 4;

MotorControl mLeft(m_left_a, m_left_b, m_left_p);
MotorControl mRight(m_right_a, m_right_b, m_right_p);

Ultrasound usLeft(us_left_port);
Ultrasound usRight(us_right_port);
Ultrasound usCenter(us_center_port);

void setup() {
  Serial.begin(9600);
  //xTaskCreate(drive,        (const portCHAR *) "Driving",         128, NULL, 1, NULL);
  //xTaskCreate(updateOrders, (const portCHAR *) "Updating Orders", 128, NULL, 2, NULL);
  //xTaskCreate(pollSensors,  (const portCHAR *) "Polling Sensors", 128, NULL, 3, NULL);
  halt(); // so we dont move when we start i guess. inA or inB might start high for some reason
}

/**
 * Polls the ultrasonic sensors and updates the distances each is reading.
 * Executed and scheduled by FreeRTOS. 
 */
void pollSensors(void *pvParameters) {
  while (1) {
    leftDist = usLeft.getCm();
    rightDist = usRight.getCm();
    centerDist = usCenter.getCm();

    vTaskDelay(150 / portTICK_PERIOD_MS);
  }
}

void drive(void *pvParameters) {
  while (1) {
    // freeroam. it just go (tm)
    if (centerDist <= STOP_DIST_CENTER) {
      if (leftDist < rightDist) {
        left();
      } else {
        right();
      }
    } else if (leftDist <= STOP_DIST_SIDE) {
      right();
    } else if (rightDist <= STOP_DIST_SIDE) {
      left();
    } else {
      forward();
    }

    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}

void loop() {
  leftDist = usLeft.getCm();
  rightDist = usRight.getCm();
  centerDist = usCenter.getCm();
  Serial.print("[");
  Serial.print(leftDist);
  Serial.print(", ");
  Serial.print(centerDist);
  Serial.print(", ");
  Serial.print(rightDist);
  Serial.println("]");

  Serial.print("[");
  Serial.print(leftDist <= STOP_DIST_SIDE);
  Serial.print(", ");
  Serial.print(centerDist <= STOP_DIST_CENTER);
  Serial.print(", ");
  Serial.print(rightDist <= STOP_DIST_SIDE);
  Serial.println("]");

  if (centerDist <= STOP_DIST_CENTER) {
    if (leftDist < rightDist) {
      left();
    } else {
      right();
    }
  } else if (leftDist <= STOP_DIST_SIDE) {
    right();
  } else if (rightDist <= STOP_DIST_SIDE) {
    left();
  } else {
    forward();
  }

  delay(20);
}

void set_speed(const unsigned int left, const unsigned int right) {
  mLeft.setPwm(left);
  mRight.setPwm(right);
}

void halt() {
  mLeft.halt();
  mRight.halt();
}

void forward() {
  set_speed(spd, spd);
  mLeft.forward();
  mRight.backward();
}

void backward() {
  set_speed(spd, spd);
  mLeft.backward();
  mRight.forward();
}

void left() {
  set_speed(spd, spd);
  mLeft.backward();
  mRight.backward();
}

void right() {
  set_speed(spd, spd);
  mLeft.forward();
  mRight.forward();
}
