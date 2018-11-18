/****************************************************************************
Author: Peter Neal      Date: 22/6/18
Arduino Nano code for Big Face Robotics Robot Head MK 2
****************************************************************************/
#include <Servo.h>

#define BUFFERSIZE 64
char databuffer[BUFFERSIZE];
int serialcounter = 0;

#define SonarSensorPin PD4
#define Panminms 500
#define Panmaxms 2500
#define Tiltminms 600
#define Tiltmaxms 2400

int Pancentrems = ((Panmaxms - Panminms)/2) + Panminms;
int Tiltcentrems = ((Tiltmaxms - Tiltminms)/2) + Tiltminms;

Servo PanServo;
Servo TiltServo;

unsigned long previousMicros = 0;
unsigned long prevBatteryMillis = 0;

int Panms = Pancentrems;
int Tiltms = Tiltcentrems;
int ServoSpeed = 5;

int PanAngle = 0;
int TiltAngle = 0;

int PanSp = Pancentrems;
int TiltSp = Tiltcentrems;

int Batteryreading;
int BatteryinputPin = A0;

const int speakerPin = 19;

// Set RGB LED pin numbers
const int RedledPin =    11;// the number of the LED pin
const int GreenledPin =  5;
const int BlueledPin =   6;

// Variables will change :
int RedledValue = 0;             // ledState used to set the LED
int GreenledValue = 0; 
int BlueledValue = 150; 

void setup() {

    Serial.begin(115200);

    /******************************************************************
     Initialise Servos and set to home positions                
    ******************************************************************/
    PanServo.attach(9);
    TiltServo.attach(10);
  
    PanServo.writeMicroseconds(Panms);
    TiltServo.writeMicroseconds(Tiltms);

    delay(300);

    Batteryreading = analogRead(BatteryinputPin);

    pinMode(speakerPin, OUTPUT); // Set buzzer - pin 19 as an output


    // Start-up sequence
    SetLEDValue(255,0,0);
    PlayTone(2);
    delay(100);
    SetLEDValue(0,0,0);
    delay(100);
    SetLEDValue(0,255,0);
    PlayTone(2);
    delay(100);
    SetLEDValue(0,0,0);
    delay(100);
    SetLEDValue(0,0,150);
    PlayTone(2);



    

}

void loop() {

    //keep an eye out for serial data
    while(Serial.available() > 0)  // if something is available from serial port
    { 
        char c=Serial.read();      // get it
        databuffer[serialcounter] = c; //add it to the data buffer
        serialcounter++;
        if(c=='\n'){  //newline character denotes end of message
            serialcounter = 0; //reset serialcounter ready for the next message
            interpretcommand();
            break;
        }           
    }
    
        unsigned long currentMicros = micros();
        
    if((currentMicros - previousMicros > (6000/ServoSpeed))) //use this to determine frequency of servo loop
    {
        // save the last time pid loop was called
        previousMicros = currentMicros;

        if (PanSp>Panms){
           Panms += 1;
           PanServo.writeMicroseconds(Panms);
        }
        else if (PanSp<Panms){
            Panms -= 1;
            PanServo.writeMicroseconds(Panms);
          
        }

        if (TiltSp>Tiltms){
           Tiltms += 1;
           TiltServo.writeMicroseconds(Tiltms);
        }
        else if (TiltSp<Tiltms){
            Tiltms -= 1;
            TiltServo.writeMicroseconds(Tiltms);
          
        }

    }

        unsigned long CurrentMillis = millis();
    if((CurrentMillis - prevBatteryMillis > 1000)) //use this to determine frequency of battery sampling loop. Sample every 1 second
    {
        prevBatteryMillis = CurrentMillis;
        Batteryreading = analogRead(BatteryinputPin);
        
    }
    

    
}

   
void interpretcommand()
{
   
   int Svalue; //Set
   int Vvalue; //Value
   int Gvalue; //Get
 
   Svalue = findchar('S');
   switch(Svalue){
   case(0):{
       Vvalue = findchar('V');
       RedledValue = Vvalue;
       SetLEDValue(RedledValue,GreenledValue,BlueledValue);
       break;}  
   case(1):{
       Vvalue = findchar('V');
       GreenledValue = Vvalue;
       SetLEDValue(RedledValue,GreenledValue,BlueledValue);
       break;} 
   case(2):{
       Vvalue = findchar('V');
       BlueledValue = Vvalue;
       SetLEDValue(RedledValue,GreenledValue,BlueledValue);
       break;}
   case(3):{
       Vvalue = findchar('V');
       PanAngle = Vvalue;
       PanSp = map(PanAngle,-900,900,Panminms,Panmaxms);
       break;}
   case(4):{
       Vvalue = findchar('V');
       TiltAngle = Vvalue;
       TiltSp = map(TiltAngle,-900,900,Tiltminms,Tiltmaxms);
       break;}
   case(5):{
       Vvalue = findchar('V');
       if ((PanAngle + Vvalue) < 900 && (PanAngle + Vvalue) > -900){  //Restrain movement when incrementing
           PanAngle = PanAngle + Vvalue; }//Increment pan angle by Vvalue
       PanSp = map(PanAngle,-900,900,Panminms,Panmaxms);
       break;}
   case(6):{
       Vvalue = findchar('V');
       if ((TiltAngle + Vvalue) < 450 && (TiltAngle + Vvalue) > -900){ //Restrain movement when incrementing
           TiltAngle = TiltAngle + Vvalue;}
       TiltSp = map(TiltAngle,-900,900,Tiltminms,Tiltmaxms);
       break;}
   case(7):{
       Vvalue = findchar('V');
       ServoSpeed = Vvalue;
       break;}
   case(8):{
       Vvalue = findchar('V');
       PlayTone(Vvalue);
       break;}
       
      
     }    
   Gvalue = findchar('G');
   switch(Gvalue){
   case(0):{
       Serial.println(map(Panms,(Panminms-1),Panmaxms,-900,900)); //Use slightly different values to map ms back to an angle.
                                                                 //Removes rounding errors with the map function.
       break;}
   case(1):{
       Serial.println(map(Tiltms,(Tiltminms-1),Tiltmaxms,-900,900));
       break;}
   case(2):{
       Serial.println(readsonar());
       break;}
    case(3):{
       Serial.println(Batteryreading/10);
       break;}
    case(4):{
       Serial.println(ServoSpeed);
       break;}
   }
     
}   




int findchar(char a)
{
  int charindex;
  String value;
  //Find the index of the character being looked for
  for(int i = 0; i<BUFFERSIZE; i++)
  {
    if(databuffer[i] == '\n')
    {
      return -1; //no character found so return -1
    }   
    if(databuffer[i] == a)
    {
      charindex = i;
      break;
    }
  }
  
  //extract characters following character of interest as a string and convert to a value
  for(int i = charindex+1; i<BUFFERSIZE; i++)
  {
    value += (databuffer[i]);
  }
  int data = value.toInt();
  return data;
  
}

void SetLEDValue(int Red, int Green, int Blue){

    analogWrite(RedledPin, 255-Red);
    analogWrite(GreenledPin, 255-Green);
    analogWrite(BlueledPin, 255-Blue);
}

int readsonar() //Read sonar sensor
{
  
  //read head sonar sensor 
  pinMode(SonarSensorPin, OUTPUT);
  digitalWrite(SonarSensorPin, LOW);             // Make sure pin is low before sending a short high to trigger ranging
  delayMicroseconds(2);
  digitalWrite(SonarSensorPin, HIGH);            // Send a short 10 microsecond high burst on pin to start ranging
  delayMicroseconds(10);
  digitalWrite(SonarSensorPin, LOW);             // Send pin low again before waiting for pulse back in
  pinMode(SonarSensorPin, INPUT);
  int duration = pulseIn(SonarSensorPin, HIGH);  // Reads echo pulse in from SRF05 in micro seconds
  int sonardist = duration/58;      // Dividing this by 58 gives us a distance in cm
  
  return sonardist;
  
}
// Series of tones for the robot to play
void PlayTone(int Tonenumber)
{ 
    switch(Tonenumber){
    case(0):{
        for(int i=100; i<600; i=i+10){
        tone(speakerPin, i, 10);
        delay(10); }
        for(int i=200; i<1000; i=i+50){
        tone(speakerPin, i, 100);
        delay(20);}
        break;
    }
    case(1):{
        tone(speakerPin, 300, 100);
        delay(100);
        tone(speakerPin, 200, 100);
        delay(100);
        tone(speakerPin, 100, 100);
        delay(100);
        break;
    }
    case(2):{
        tone(speakerPin, 500, 150);
        break;
    }
    case(3):{
        tone(speakerPin, 500, 40);
        delay(40);
        tone(speakerPin, 400, 40);
        delay(40);
        tone(speakerPin, 300, 40);
        delay(40);
        tone(speakerPin, 400, 20);
        delay(20);
        tone(speakerPin, 300, 20);
        delay(20);
        tone(speakerPin, 500, 20);
        delay(20);
        break;
    }
  
}
}
