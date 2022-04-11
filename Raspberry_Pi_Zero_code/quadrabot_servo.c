// quadrabot_servo.c custom C code for quadrabot walking robots that use PCA9685 servo functions
// developed by Enmore April 2019

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>   // added so that usleep(microseconds) can be used
#include <PCA9685.h>  // include the PCA9865 custom library
#include "quadrabot_servo.h"

// globals
int __fd;    // needed for cleanup()
int __addr;  // needed for cleanup()
int debug = 0;

int fd;
int addr = 0x40;
// Example for a second device. Set addr2 to device address (if set to 0x00 no second device will be used)
int fd2;
int addr2 = 0x00;

int adpt = 1;
int frequency = 50;

int START_REG = 0x06;

// servo PWM 'on values' which are always zero for every servo
unsigned int fwdON[16] =
  {   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0};

// servo PWM 'off values' for each of the 16 channels: N.B. only a maximum of 12 servos used for a quadrabot (hip, knee and ankle)
unsigned int fwdOFF[16][16] = {       /* each row is the 16 time slices for an individual servo/channel */
  {   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0},  /* servo 0 not used for 8DOF*/
  {   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0},  /* servo 1 not used for 8DOF*/
  {   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0},  /* servo 2 not used for 8DOF*/
  {   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0},  /* servo 3 not used for 8DOF*/
  { 250, 350, 450, 520, 520, 520, 496, 473, 450, 425, 400, 375, 350, 317, 283, 250},  /* servo 4 fwdBRH */
  { 270, 290, 310, 330, 350, 387, 424, 460, 460, 350, 270, 205, 205, 205, 227, 249},  /* servo 5 fwdBLH */
  { 240, 540, 540, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240},  /* servo 6 fwdBRL */
  { 415, 415, 415, 415, 415, 415, 415, 415, 415, 110, 110, 415, 415, 415, 415, 415},  /* servo 7 fwdBLL */
  { 230, 203, 176, 150, 150, 230, 310, 450, 450, 450, 403, 356, 310, 290, 270, 250},  /* servo 8 fwdFRH */
  { 230, 230, 270, 310, 350, 375, 400, 425, 450, 487, 524, 560, 560, 450, 350, 230},  /* servo 9 fwdFLH */
  { 405, 405, 405, 405, 405, 110, 110, 405, 405, 405, 405, 405, 405, 405, 405, 405},  /* servo 10 fwdFRL */
  { 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 540, 540, 240},  /* servo 11 fwdFLL */
  {   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0},  /* servo 12 not used for 8DOF*/
  {   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0},  /* servo 13 not used for 8DOF*/
  {   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0},  /* servo 14 not used for 8DOF*/
  {   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0}   /* servo 15 not used for 8DOF*/
};


// ************************************************************
// this simple 'connection' function included for test purposes
// ************************************************************
void connect_servo()
{
    printf("Connected to the quadrabot PCA9685 servo C library...\n");
}


// ***************************
// PWM module clean up routine
// ***************************
void PWMcleanup() {
  // attempt to turn off all PWM
  PCA9685_setAllPWM(__fd, __addr, _PCA9685_MINVAL, _PCA9685_MINVAL);
} // PWMcleanup


// ********************************
// routine to turn off all channels
//*********************************
void intHandler(int dummy) {
  // turn off all channels
  PCA9685_setAllPWM(fd, addr, _PCA9685_MINVAL, _PCA9685_MINVAL);
  exit(dummy);
} // intHndler


// ***********************************
// PCA9685 PWM hardware set up routine
// ***********************************
int PWMsetup(unsigned char mod_addr, unsigned int freq) {

  int ret;     // returned value from PCA9685_dumpAllRegs
  int afd;     // returned 'file descriptor' from PCA9685_openI2C
  int result;  // returned value from PCA9685_initPWM
  
  afd = PCA9685_openI2C(adpt, mod_addr);
  if (debug) {
    printf ("I2C file descriptor is %d  \n ", afd);
  }	// if debug

  result = PCA9685_initPWM(afd, mod_addr, freq);
  if (debug) {
    printf ("PWM set up result is %d  \n ", result);
  } // if debug

  if (debug) {
    // display all used pca registers 
    ret = PCA9685_dumpAllRegs(afd, mod_addr);
    if (ret != 0) {
      fprintf(stderr, "PWMsetup(): PCA9685_dumpAllRegs() returned %d\n", ret);
      return -1;
    } // if ret
  } // if debug

  return afd;
} // PWMsetup

// *****************************
// routine to set a single servo
// *****************************
int setServo(int fd, int channel, int value, int waittime) {
  // fd is the I2C file descriptor - typically 3
  // channel is the servo# 0-15
  // value is the PWM off setting 0-4096 but for a SG90 servo is usually in the range 160-560
  // waittime is a time in ms to wait after the servo is set - usually zero
  int uwait = waittime*1000; // convert ms to microseconds for the usleep function

  // calculate the register# to be set
  int setreg = START_REG+4*channel;
  
  if (debug) {
    printf ("parameters for setting a single servo \n ");
	printf ("passed thru I2C file descriptor is %d  \n ", fd);
	printf ("channel being set is %d  \n ", channel);
	printf ("=>register being set is %d  \n ", setreg); 
	printf ("off value being set is %d  \n ", value); 
  } // if debug

  // just use the standard PCA9685_setPWMVal function with set/default values
  PCA9685_setPWMVal(fd, addr, setreg, 0, value);
  usleep(uwait);  //wait after setting each servo - typically used to slow down for debug to see what is happening
  
}


// *************************************************************************************
// routine to go foward for one full 16-time slice cycle, where all 16 channels (servos)
//  are set at once i.e. 16 times for all 16 time slices in a single cycle
// *************************************************************************************
int setGoFwd(int fd) {
  int i, j;  // j columns, i rows
  unsigned int OFFvals[16];

  // loop through each row extracting the columns into a separate array for column 1 then increase the column number
  for ( j = 0; j < 16; j++ ) {

    for ( i = 0; i < 16; i++ ) {
      OFFvals[i] = fwdOFF[i][j];
    }
    if (debug) {
      for ( i = 0; i < 16; i++ ) {
	    printf ("%d ", OFFvals[i]);
      }
      printf ("\n");
    } // if debug

    // just use the standard PCA9685_setPWMVals function with set/default values
    PCA9685_setPWMVals(fd, addr, fwdON, OFFvals);
	usleep(150000);  //wait 150ms after setting each time slice to allow servo movement to complete

  }  
}