#include <SoftwareSerial.h>

/*
  Implementes the Morse algorithm for a simple speaker
  
  @author Felix
  @date 07.05.2011
  */
int inByte = 0;
int i = 0;
int j = 0;
int char_avail =  0;

/* You can touch this: */
#define DIT_DELAY 50


/* But you cannot touch this: */
#define WORD_DELAY (DIT_DELAY * 7)
#define DIT_CYCLES (DIT_DELAY/2)
#define CHAR_DELAY (DIT_DELAY * 3)

#define dsym() delay(DIT_DELAY);
#define char_delay() delay(CHAR_DELAY);
#define word_delay() delay(WORD_DELAY);


static  char* latin_upper[] = {
  ". -\0" , /* A */
  "- . . .\0"
  "- . . .\0",
  "- . - .\0",
  "- . .\0",
  ".\0",
  ". . - .\0",
  "- - .\0",
  ". . . .\0",
  ". .\0",
  ". - - -\0",
  "- . -\0",
  ". - . .\0",
  "- -\0",
  "- .\0",
  "- - -\0",
  ". - - .\0",
  "- - . -\0",
  ". - .\0",
  ". . .\0",
  "-\0",
  ". . -\0",
  ". . . -\0",
  ". - -\0",
  "- . . -\0",
  "- . - -\0",
  "- - . .\0" /* Z */
};
static  char* numbers[] = {
  "- - - - -\0", /* 0 */
  ". - - - -\0",
  ". . - - -\0",
  ". . . - -\0",
  ". . . . -\0",
  ". . . . .\0",
  "- . . . .\0",
  "- - . . .\0",
  "- - - . .\0",
  "- - - - .\0"  /* 9 */
};

void setup() {                
  // initialize the digital pin as an output.
  // Pin 13 has an LED connected on most Arduino boards:
  pinMode(13, OUTPUT);     
  Serial.begin(9600);
}



void loop() {
  char_avail = Serial.available();
  
  if(char_avail > 0) {
    for (j = 0; j < char_avail;j++)
    {
      char on_line = Serial.read();
      to_beep(on_line);
      char_delay();
    }
  }
}

void to_beep(char data)
{
  char* mdata;
  if (data == ' ')
  {
    word_delay();
    Serial.println("word end");
    return;
  }
  else{
    if (data == '\n') {
      word_delay();
      Serial.println("EOL");
      return;
    } else
    if (data >= 'A' && data <= 'Z' )
      mdata = latin_upper[data-'A'];
    else
    if (data >= 'a' && data <= 'z' )
      mdata = latin_upper[data-'a'];
    else
    if (data >= '0' && data <= '9')
      mdata = numbers[data-'0'];
    else
    {
      Serial.print(data);
      Serial.println(": not implemented");
      return;
    }
  }
  
  Serial.println(mdata);
  int sdata = strlen( mdata);
  for( char i = 0; i < sdata; i ++)
  {

    char token = mdata[i];
    if (token == '.')
    {
      dit();
    }
    if (token == '-')
    {
      dah();
    }
    if (token == ' ')
    {
      dsym();
    }
   
  }
  
}
void dah() {
  for (int i=0;i<3;i++)
  {
    dit();
  }
}

void dit(){

  for (int i=0;i<DIT_CYCLES;i++) // Number of DIT Cycles , sleep 2 milliseconds in a cycle
  {
      digitalWrite(13, HIGH);   // set the LED on
      delay(1);            

      digitalWrite(13, LOW);    // set the LED off
      delay(1);             
  }
}


