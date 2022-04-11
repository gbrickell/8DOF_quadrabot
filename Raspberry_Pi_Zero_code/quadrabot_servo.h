void connect_servo();
void PWMcleanup();
void intHandler(int dummy);
int PWMsetup(unsigned char mod_addr, unsigned int freq);
int setServo(int fd, int channel, int value, int waittime);
int setGoFwd(int fd);