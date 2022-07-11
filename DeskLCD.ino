#include <LiquidCrystal.h>

const int rs = 11, en = 10, d4 = 9, d5 = 8, d6 = 7, d7 = 6;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  pinMode(12, OUTPUT);
  digitalWrite(12, LOW);

  Serial.begin(9600);
  
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  
  lcd.clear();
}

unsigned int cursorPos = 0;
unsigned int linePos = 0;

void loop() {
  while (Serial.available()) {
    char inputChar = Serial.read();

    if (inputChar == 0) {
      continue;
    }

    Serial.print((int)inputChar);

    switch (inputChar) {

      // Programming chars
      case '~': // Clear Screen
        lcd.clear();
        lcd.setCursor(0, 0);
        cursorPos = 0;
        linePos = 0;
        break;
      case '`': // New Line
        lcd.setCursor(0, 1);
        cursorPos = 0;
        linePos = 1;
        break;
      case '_': // Backspace
        lcd.setCursor(cursorPos-- - 1, linePos);
        lcd.print(" ");
        lcd.setCursor(cursorPos, linePos);
        break;
      case '|': // non-delete backspace
        lcd.setCursor(cursorPos-- - 1, linePos);
        break;
      case '<': // set cursor 0,0
        lcd.setCursor(0, 0);
        cursorPos = 0;
        linePos = 0;
        break;
      case '>': // set cursor 0,1
        lcd.setCursor(0, 1);
        cursorPos = 0;
        linePos = 1;
        break;
       

        
      case 3: // Clear Screen
        lcd.clear();
        lcd.setCursor(0, 0);
        cursorPos = 0;
        linePos = 0;
        break;
      case '\0': // NULL
        break;
      case 13: // New Line
        lcd.setCursor(0, 1);
        cursorPos = 0;
        linePos = 1;
        break;
      case 127: // Backspace
        lcd.setCursor(cursorPos-- - 1, linePos);
        lcd.print(" ");
        lcd.setCursor(cursorPos, linePos);
        break;
      default:
        lcd.print(inputChar);
        cursorPos ++;
        break;
    }
  }
  
}
