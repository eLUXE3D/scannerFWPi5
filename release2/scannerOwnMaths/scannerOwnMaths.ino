
//VERTICAL MOTOR=0
//HORIZONTAL MOTOR=1

//SERIAL
char DELIMITER = ':';
String command;
char *valString = malloc(5);

//MOTOR SETUP
int MOTOR_V_DIR_PIN=16;//A2
int MOTOR_V_STEP_PIN=17;//A3
int MOTOR_H_DIR_PIN=18;//A4
int MOTOR_H_STEP_PIN=19;//A5
int MAG_SENSOR_PIN=21;//A7
unsigned int DIR_WAIT=2;//usec  - //1.2 usec? minimum according to datasheet
unsigned int STEP_PULSE=5;//usec - //1.9 usec minimum according to datasheet
unsigned int STEP_WAIT=2;//usec - //1.9 usec minimum according to datasheet
//total delay should be >4usec so 250kHz not exceeded, I need about 10kHz, so 100usec per pulse
int motorNumber=0;//or 1;
float countsPerRev[2] = {200.0f*32.0f,400.0f*32.0f};
float degreesToMotorStepsCoeff[2]={countsPerRev[0]/360.0f,countsPerRev[1]/360.0f};
float minMoveSpeed=32.0f;//steps per sec - to prevent motor speed=0 and therefore jam by delay=infinity. 32 is about 2 deg per sec

void forwardstepV();
void backwardstepV();
void forwardstepH();
void backwardstepH();
float calcSpeed(float startAngle, float endAngle, float currentAngle, float accel, float topSpeed, bool clockwiseMovement);

//MOTOR STATE
int currentAngleSteps[2]={0,0};
int startAngleSteps[2];
int endAngleSteps[2];
float maxSpeed[2]={200.0f,200.0f};//steps per sec
float accel[2]={200.0f,200.0f};//steps per sec per sec
bool clockwiseMovement[2]={true, true};
unsigned long lastStepTime[2]={0, 0};
unsigned long stepInterval[2]={0, 0};
bool stepTimeCalculated[2]={false,false};

void setup() {
  //test serial connect
  Serial.begin(9600);
  //sendReply("USB Test");
  //MOTOR INITIALISATION
  pinMode(MOTOR_V_STEP_PIN, OUTPUT);
  pinMode(MOTOR_V_DIR_PIN, OUTPUT);
  pinMode(MOTOR_H_STEP_PIN, OUTPUT);
  pinMode(MOTOR_H_DIR_PIN, OUTPUT);
  digitalWrite(MOTOR_V_STEP_PIN, LOW);
  digitalWrite(MOTOR_H_STEP_PIN, LOW);
  digitalWrite(MOTOR_V_DIR_PIN, LOW);
  digitalWrite(MOTOR_H_DIR_PIN, LOW);
}

void loop() {
  command= getCommand();
  actOnCommand(command);
  //MOTOR CONTROL
  bool runningV=true;
  bool runningH=true;
  lastStepTime[0]=micros();//initialise for first step
  lastStepTime[1]=micros();//initialise for first step
  stepTimeCalculated[0]=false;//initialise for first step
  stepTimeCalculated[1]=false;//initialise for first step
  while((runningV) || (runningH)) { 
      runningV=runMotor(0);
      runningH=runMotor(1);
  }
  //sendReply("DONE");
  sendReply(command);
}

String getCommand() {//don't send CR from PC else it messes up
  char dataByte=' ';
  String inputBuffer = "";

  while(true) {
    if (Serial.available()) {
        dataByte=(char)Serial.read();
        if(dataByte==DELIMITER) break;
        inputBuffer += dataByte;
    }
    delay(1);//needed
  }
  //delay(2);//test
  return inputBuffer;
}

void sendReply(String message) {
    Serial.print(message+":");
    delay(1);//very probably not needed
}

void actOnCommand(String completeCommand) {
  float floatValue;
  float floatValueZero;
  float floatValueOne;
  long motorSteps;
  float motorStepsFloat;
  
  //MOVE COMMANDS
  if(completeCommand.startsWith("MOTOR_NO")) {//takes an angle
     motorNumber=int(completeCommand.substring(8,completeCommand.length()).toInt());//note toInt gives a long
  }
  if(completeCommand.startsWith("MOVE_TO_")) {//takes an angle
     floatValue=completeCommand.substring(8,completeCommand.length()).toFloat();
     startAngleSteps[motorNumber]=currentAngleSteps[motorNumber];
     endAngleSteps[motorNumber]=angleToMotorSteps(floatValue,motorNumber);
     if(startAngleSteps[motorNumber]<endAngleSteps[motorNumber]) clockwiseMovement[motorNumber]=true; else clockwiseMovement[motorNumber]=false;
  }
  if(completeCommand.startsWith("MOVE_BY_")) {//takes an angle
     floatValue=completeCommand.substring(8,completeCommand.length()).toFloat();
     startAngleSteps[motorNumber]=currentAngleSteps[motorNumber];
     endAngleSteps[motorNumber]=startAngleSteps[motorNumber]+angleToMotorSteps(floatValue,motorNumber);
     if(startAngleSteps[motorNumber]<endAngleSteps[motorNumber]) clockwiseMovement[motorNumber]=true; else clockwiseMovement[motorNumber]=false;
  }
  if(completeCommand.startsWith("MOV_TO_M")) {//takes 2 angles e.g. MOV_TO_M1.8&4.0:
     int separatorPosition=completeCommand.indexOf('&');
     floatValueZero=completeCommand.substring(8,separatorPosition).toFloat();
     floatValueOne=completeCommand.substring(separatorPosition+1,completeCommand.length()).toFloat();
     
     startAngleSteps[0]=currentAngleSteps[0];
     endAngleSteps[0]=angleToMotorSteps(floatValueZero,0);
     if(startAngleSteps[0]<endAngleSteps[0]) clockwiseMovement[0]=true; else clockwiseMovement[0]=false;

     startAngleSteps[1]=currentAngleSteps[1];
     endAngleSteps[1]=angleToMotorSteps(floatValueOne,1);
     if(startAngleSteps[1]<endAngleSteps[1]) clockwiseMovement[1]=true; else clockwiseMovement[1]=false;
  }
  if(completeCommand.startsWith("MOV_BY_M")) {//takes 2 angles e.g. MOV_TO_M1.8&4.0:
     int separatorPosition=completeCommand.indexOf('&');
     floatValueZero=completeCommand.substring(8,separatorPosition).toFloat();
     floatValueOne=completeCommand.substring(separatorPosition+1,completeCommand.length()).toFloat();
     
     startAngleSteps[0]=currentAngleSteps[0];
     endAngleSteps[0]=startAngleSteps[0]+angleToMotorSteps(floatValueZero,0);
     if(startAngleSteps[0]<endAngleSteps[0]) clockwiseMovement[0]=true; else clockwiseMovement[0]=false;

     startAngleSteps[1]=currentAngleSteps[1];
     endAngleSteps[1]=startAngleSteps[1]+angleToMotorSteps(floatValueOne,1);
     if(startAngleSteps[1]<endAngleSteps[1]) clockwiseMovement[1]=true; else clockwiseMovement[1]=false;
  }
  //SPEED & ACCEL SETUP
  if(completeCommand.startsWith("MAX_SPD_")) {//set top move speed
     floatValue=completeCommand.substring(8,completeCommand.length()).toFloat();
     motorStepsFloat=angleToMotorStepsFloat(floatValue, motorNumber);
     maxSpeed[motorNumber]=motorStepsFloat;
  }
  if(completeCommand.startsWith("ACCEL___")) {//set move accel
    floatValue=completeCommand.substring(8,completeCommand.length()).toFloat();
    motorStepsFloat=angleToMotorStepsFloat(floatValue, motorNumber);
    accel[motorNumber]=(motorStepsFloat);
   }
  //INIT
  if(completeCommand.startsWith("SET_POS_")) {
    floatValue=completeCommand.substring(8,completeCommand.length()).toFloat();
    motorSteps=angleToMotorSteps(floatValue, motorNumber);
    currentAngleSteps[motorNumber]=motorSteps;
    endAngleSteps[motorNumber]=motorSteps;
  }
  //MAG SENSOR
  if(completeCommand.startsWith("GET_MAG_")) {
      int val = analogRead(MAG_SENSOR_PIN);  // read the input pin
      sprintf(valString, "%04d", val);
      command=valString;
      //sendReply(valString);
  }
  if(completeCommand.startsWith("MAG_LEV_")) {
      int val = analogRead(MAG_SENSOR_PIN);//TODO if want to use ard to level.
  }
}

long angleToMotorSteps(float angle, int motorNo) {
  long motorSteps = (long)round(angle*degreesToMotorStepsCoeff[motorNo]);
  return motorSteps;
}

float angleToMotorStepsFloat(float angle, int motorNo) {
  float motorStepsFloat = angle*degreesToMotorStepsCoeff[motorNo];
  return motorStepsFloat;
}

bool runMotor(int motorNumber) {
  if(currentAngleSteps[motorNumber]==endAngleSteps[motorNumber]) return false;//finished

  //calc step interval
  if (!stepTimeCalculated[motorNumber]) {
      float speedV=calcSpeed((float)startAngleSteps[motorNumber],(float)endAngleSteps[motorNumber], (float)currentAngleSteps[motorNumber], (float)accel[motorNumber], (float)maxSpeed[motorNumber], clockwiseMovement[motorNumber]);//speed in steps per sec
      stepInterval[motorNumber]=(unsigned int)(1000000.0f/abs(speedV));
      stepTimeCalculated[motorNumber]=true;
  }
  
  //get time
  unsigned long currentTime = micros();

  //if time for a step 
  if (currentTime -lastStepTime[motorNumber] >  stepInterval[motorNumber]) {
    //step forwards or backwards
    if (motorNumber==0) {//vertical
          if (clockwiseMovement[0]) forwardstepV(); else backwardstepV();
    }
    if (motorNumber==1) {//horiz
          if (clockwiseMovement[1]) forwardstepH(); else backwardstepH();
    }
    lastStepTime[motorNumber]=currentTime;
    stepTimeCalculated[motorNumber]=false;
  }
  return true;//keep running
}

    
float calcSpeed(float startAngle, float endAngle, float currentAngle, float accel, float topSpeed, bool clockwiseMovement) {
  //do all calc in motor steps, cast to float all step ints when calling
  float halfWayAngle=startAngle+(endAngle-startAngle)/2;//put in setup
  float v;
      
  if(clockwiseMovement) {
    if(currentAngle>halfWayAngle) {
      //deaccelarate
      float midPointVsqrd=minMoveSpeed*minMoveSpeed+2*accel*(halfWayAngle-startAngle);
      v=sqrt(midPointVsqrd-2*accel*(currentAngle-halfWayAngle));
    } else {
      //accelerate
      //v^2=u^2+2as
      v=sqrt(minMoveSpeed*minMoveSpeed+2*accel*(currentAngle-startAngle));
    }
  } else {
    if(currentAngle<halfWayAngle) {
       //deaccelarate
       float midPointVsqrd=minMoveSpeed*minMoveSpeed+2*accel*(startAngle-halfWayAngle);
       v=sqrt(midPointVsqrd-2*accel*(halfWayAngle-currentAngle));
    } else {
      //accelerate
      //calc velocity
      //v^2=u^2+2as
      v=sqrt(minMoveSpeed*minMoveSpeed+2*accel*(startAngle-currentAngle));
    } 
  }

  if(v<minMoveSpeed) v=minMoveSpeed;
  if(v>topSpeed) v=topSpeed;

  return v;
}

void forwardstepV() {
    digitalWrite(MOTOR_V_DIR_PIN, LOW);
    delayMicroseconds(DIR_WAIT);
    digitalWrite(MOTOR_V_STEP_PIN, HIGH);
    delayMicroseconds(STEP_PULSE);
    digitalWrite(MOTOR_V_STEP_PIN, LOW);
    delayMicroseconds(STEP_WAIT);
    currentAngleSteps[0]++;
    //sendReply("+");
}
void backwardstepV() {
    digitalWrite(MOTOR_V_DIR_PIN, HIGH);
    delayMicroseconds(DIR_WAIT);
    digitalWrite(MOTOR_V_STEP_PIN, HIGH);
    delayMicroseconds(STEP_PULSE);
    digitalWrite(MOTOR_V_STEP_PIN, LOW);
    delayMicroseconds(STEP_WAIT);
    currentAngleSteps[0]--;
    //sendReply("-");
}

void forwardstepH() {
    digitalWrite(MOTOR_H_DIR_PIN, HIGH);
    delayMicroseconds(DIR_WAIT);
    digitalWrite(MOTOR_H_STEP_PIN, HIGH);
    delayMicroseconds(STEP_PULSE);
    digitalWrite(MOTOR_H_STEP_PIN, LOW);
    delayMicroseconds(STEP_WAIT);
    currentAngleSteps[1]++;
}
void backwardstepH() {
    digitalWrite(MOTOR_H_DIR_PIN, LOW);
    delayMicroseconds(DIR_WAIT);
    digitalWrite(MOTOR_H_STEP_PIN, HIGH);
    delayMicroseconds(STEP_PULSE);
    digitalWrite(MOTOR_H_STEP_PIN, LOW);
    delayMicroseconds(STEP_WAIT);
    currentAngleSteps[1]--;
}
