const int PIN_CLK = 18;
const int PIN_DT = 19;
const int PIN_SW = 21;

const int8_t transitions[16] = {
  0, -1, 1, 0,
  1, 0, 0, -1,
  -1, 0, 0, 1,
  0, 1, -1, 0
};

uint8_t previousState;
int8_t quarterSteps = 0;
long position = 0;
bool lastRawButton = HIGH;
bool stableButton = HIGH;
unsigned long buttonChangedAt = 0;

void setup() {
  pinMode(PIN_CLK, INPUT_PULLUP);
  pinMode(PIN_DT, INPUT_PULLUP);
  pinMode(PIN_SW, INPUT_PULLUP);
  Serial.begin(115200);
  delay(300);
  previousState = (digitalRead(PIN_CLK) << 1) | digitalRead(PIN_DT);
  lastRawButton = digitalRead(PIN_SW);
  stableButton = lastRawButton;
  Serial.println("ENCODER TEST: CLK=18 DT=19 SW=21; 115200 baud");
}

void loop() {
  uint8_t state = (digitalRead(PIN_CLK) << 1) | digitalRead(PIN_DT);
  if (state != previousState) {
    quarterSteps += transitions[(previousState << 2) | state];
    previousState = state;
    if (quarterSteps >= 4 || quarterSteps <= -4) {
      position += quarterSteps > 0 ? 1 : -1;
      Serial.print("ROTATE ");
      Serial.println(position);
      quarterSteps = 0;
    }
  }

  bool rawButton = digitalRead(PIN_SW);
  if (rawButton != lastRawButton) {
    buttonChangedAt = millis();
    lastRawButton = rawButton;
  }
  if (millis() - buttonChangedAt >= 30 && rawButton != stableButton) {
    stableButton = rawButton;
    Serial.println(stableButton == LOW ? "BUTTON DOWN" : "BUTTON UP");
  }
}
