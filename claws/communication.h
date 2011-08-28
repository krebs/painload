/* These are the command codes of the relay card. If you change something here you must
 * recompile the firmware and the control tool. */
#ifndef _COMMUNICATION_H
#define _COMMUNICATION_H

#define COMMAND_RELAY_ON           0x01
#define COMMAND_RELAY_OFF          0x02
#define COMMAND_RELAY_TOGGLE       0x04
#define COMMAND_RELAY_SET          0x08
#define COMMAND_RELAY_TIME_ON      0x10
#define COMMAND_RELAY_TIME_OFF     0x20
#define COMMAND_RELAY_TIME_CYCLIC  0x40
#define COMMAND_GET_STATUS         0x80
#define COMMAND_DEL_TIMERS         0x81
#define COMMAND_SETUP_REMOTE       0x82


#define RESPONSE_OK                 0xff
#define RESPONSE_INVALID_COMMAND    0xfe
#define RESPONSE_INVALID_ARGUMENT   0xfd
#define RESPONSE_TRANSMISSION_ERROR 0xfc

#define COMMANDO_LENGTH    4

#endif
