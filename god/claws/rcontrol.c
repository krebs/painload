/*  +----------------------------------------------------------------------+
 *  | relay control program                                                |
 *  |   by mgr, 2007                                                       |
 *  |   last change: 2009-01-05                                            |
 *  |                                                                      |
 *  | This program is used to control the relay card version 1.0. For more |
 *  | information have a look at the project homepage.                     |
 *  | You will need libftdi in order to compile this tool.                 |
 *  |                                                                      |
 *  | NOTE: For some reason the -l option causes a program crash if I      |
 *  | compile this program with -O2. On top of that this code seems to     |
 *  | be quite optimal, the program size gets a little larger with -O2,    |
 *  | so I suggest you just compile it without optimization.               |
 *  +----------------------------------------------------------------------+
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <getopt.h>
#include <ctype.h>
#include <time.h>
#include <ftdi.h>       // libftdi

/* Notice that if you experiment with the baud rate, you will have to adapt
 * the firmware, too. Also I do not recommend it, as 9600 Bauds are completely
 * sufficient for this application. */
#define BAUD 9600

/* If you are using more than one FT232-based pieces of hardware at once, 
 * we need a way to uniquely address any given one. This is done by the
 * serial of the specific device which you can pass to this tool or specify
 * here. If no serial is specified (NULL), the first found device is opened. */
#define DEFAULT_FT_SERIAL   "A6TMRSS6"

#define VERSION             "1.0"

#define OPTION_ADDRESS      0x01
#define OPTION_INTERVAL     0x04
#define OPTION_CYCLIC       0x08
#define OPTION_ON           0x10
#define OPTION_OFF          0x20
#define OPTION_TOGGLE       0x40
#define OPTION_DEL_TIMERS   0x80
#define OPTION_LIST_DEVICES 0x200

#define EXIT_CODE_OK        0
#define EXIT_CODE_FAILURE   1

#include "communication.h"

/* function prototypes */
void usage(char* name);
void version(void);
const char* card_strerror(int error);
int valid_argument(const char* str);
void exit_gracefully(struct ftdi_context* ftdic, char exit_code);


int main(int argc, char **argv)
{
  int ret=0, int_argument=0, option_flags=0, long_index=0, i=0, num_ops=0;
  signed char c=0;
  unsigned char buf[COMMANDO_LENGTH], char_argument=0, operation=0;
  const char* ft_serial=DEFAULT_FT_SERIAL;
  double double_argument;
  char buf0[64], buf1[64], buf2[64];
  time_t start_time;

  //struct ftdi_eeprom eeprom;

  struct ftdi_context ftdic;
  struct ftdi_device_list *devlist=NULL, *curdev=NULL;

  static struct option long_options[] =
  {
     {"help",          0, 0, '?'},
     {"version",       0, 0, 'V'},
     {"on",            1, 0, 'o'},
     {"off",           1, 0, 'f'},
     {"toggle",        1, 0, 't'},
     {"set",           1, 0, 's'},
     {"status",        0, 0, 'S'},
     {"interval",      1, 0, 'v'},
     {"cyclic",        0, 0, 'c'},
     {"address",       1, 0, 'a'},
     {"delete-timers", 0, 0, 'd'},
     {"list-devices",  0, 0, 'l'},
     {0,               0, 0,  0 }
  };
  
  /* fetch the command line options */
  while ((c = getopt_long_only(argc, argv, "?Vo:f:t:s:Sv:ca:dl", long_options,
	                       &long_index)) != -1)
  {
    switch (c)
    {
      case 'o': case 'f': case 't':
	int_argument = atoi(optarg);

	if (int_argument > 6 || int_argument < 1 || !valid_argument(optarg))
	{
	  fprintf(stderr, "%s: -s: invalid value `%s' (1-6 is valid)\n",
			  *argv, optarg);
	  return EXIT_CODE_FAILURE;
	}

	char_argument = (unsigned char)int_argument;

	if (c == 't')
	{
	  operation = COMMAND_RELAY_TOGGLE;
	  option_flags |= OPTION_TOGGLE;
	} else if (c == 'o')
	{
	  operation = COMMAND_RELAY_ON;
	  option_flags |= OPTION_ON;
	} else
	{
	  operation = COMMAND_RELAY_OFF;
          option_flags |= OPTION_OFF;
        }
        
	num_ops++;

	break;
      
      case 's':
        int_argument = atoi(optarg);

	if (int_argument > (1 << 6)-1 || int_argument < 0 || !valid_argument(optarg))
	{
	  fprintf(stderr, "%s: -s: invalid value `%s'\n", *argv, optarg);
	  return EXIT_CODE_FAILURE;
	}

	char_argument = (unsigned char)int_argument;
	operation = COMMAND_RELAY_SET;
	num_ops++;
	break;
      
      case 'S':
	operation = COMMAND_GET_STATUS;
        num_ops++;
	break;
      
      case 'v':
	double_argument = atof(optarg);
        int_argument = (int)(double_argument*60) /10;
	
	if (int_argument < 1 || int_argument > (1 << 16)-1)
	{
          fprintf(stderr, "%s: -i: invalid interval `%s'\n", *argv, optarg);
	  return EXIT_CODE_FAILURE;
	}

        option_flags |= OPTION_INTERVAL;
	break;
      
      case 'c':
        option_flags |= OPTION_CYCLIC;
	break;  
      
      case 'd':
        operation = COMMAND_DEL_TIMERS;
	option_flags |= OPTION_DEL_TIMERS;
        num_ops++;
	break;	
      
      case 'a':
	if (strlen(optarg) != 8)
	{
	  fprintf(stderr, "%s: -s: invalid serial number `%s'\n", *argv, optarg);
	  return EXIT_CODE_FAILURE;
	}

        ft_serial = optarg;
	option_flags |= OPTION_ADDRESS;
	break;
      
      case 'l':
	option_flags |= OPTION_LIST_DEVICES;
	break;

      case 'V':
	version();
	break;
      case '?': default:
        usage(*argv);
	break;
    }
  }
  
  /* check whether the command line options are valid */
  if ((option_flags & OPTION_INTERVAL))
  {
    if (option_flags & OPTION_DEL_TIMERS)
    {
      fprintf(stderr, "%s: -d cannot be mixed with timing options\n", *argv);
      usage(*argv);
    }

    if (option_flags & OPTION_CYCLIC)
    {
      operation = COMMAND_RELAY_TIME_CYCLIC; 
    } else if (option_flags & OPTION_ON)
    {
      operation = COMMAND_RELAY_TIME_ON;
    } else if (option_flags & OPTION_OFF)
    {
      operation = COMMAND_RELAY_TIME_OFF;
    } else 
    {
      fprintf(stderr, "%s: -v: you must also specify an operation (-o or -f)\n", *argv);
      usage(*argv);
    }
  }

  if (!operation && !(option_flags & OPTION_LIST_DEVICES))
  {
    usage(*argv);
  }

  if (((option_flags & OPTION_DEL_TIMERS) && (operation != COMMAND_DEL_TIMERS)))
  {
    fprintf(stderr, "%s: invalid mixture of options\n", *argv);
    usage(*argv);
  }
  
  if (num_ops > 1)
  {
    fprintf(stderr, "%s: more than one operation specified\n", *argv);
    usage(*argv);
  }

  if (ftdi_init(&ftdic) < 0)
  {
      fprintf(stderr, "%s: unable to initialize FTDI context: %d (%s)\n", *argv, ret, 
		      ftdi_get_error_string(&ftdic));
      return EXIT_CODE_FAILURE;
  }
  
  /* list all found FT232 devices */
  if (option_flags & OPTION_LIST_DEVICES)
  {
    printf("scanning for FT232 devices...\n"
	   "you can address the devices using `%s -a <serial>'\n", *argv);

    if ((ret = ftdi_usb_find_all(&ftdic, &devlist, 0x0403, 0x6001)) < 0)
    {
       fprintf(stderr, "%s: unable to scan devices: %d (%s)\n", *argv, ret, 
		      ftdi_get_error_string(&ftdic));
       exit(EXIT_CODE_FAILURE);
    }
    
    if (ret == 0)
    {
      printf("  no devices found :(\n");
      return EXIT_CODE_OK;
    }
    
    for (i=0, curdev = devlist; curdev != NULL; i++)
    {
      if (ftdi_usb_get_strings(&ftdic, curdev->dev, buf0, sizeof(buf0)/sizeof(char),
			       buf1, sizeof(buf1)/sizeof(char), buf2, sizeof(buf2)/sizeof(char)) < 0)
      {
        fprintf(stderr, "unable to fetch information for device #%i: %s\n", i,
			ftdi_get_error_string(&ftdic));
        // continue caused an endless loop in case of an error
	break;
      }

      printf("\ndevice #%i%s:\n"
	     "  manufacturer: %s\n"
	     "  device:       %s\n"
	     "  serial:       %s\n", i, (i == 0 ? " (default)" : ""), 
	     (buf0 != NULL ? buf0 : "n/a"), (buf1 != NULL ? buf1 : "n/a"),
	     (buf2 != NULL ? buf2 : "n/a"));
      
      curdev = curdev->next;
    }
   
    ftdi_list_free(&devlist);
    return EXIT_CODE_OK;
  }

  /* Try to open the specified device. If that fails, we take a long shot
   * and open the first found FT232 device and assume its the relay card.
   * We don't do this if an address was specified with the -a option. */
  if ((ret = ftdi_usb_open_desc(&ftdic, 0x0403, 0x6001, NULL, ft_serial)) < 0)
  {
    fprintf(stderr, "%s: unable to open ftdi device: %d (%s)\n", *argv, ret, 
		    ftdi_get_error_string(&ftdic));
    exit(EXIT_CODE_FAILURE);
  }
  
  /* get rid of any data still floating around the buffer */
  ftdi_usb_reset(&ftdic);
  ftdi_usb_purge_buffers(&ftdic);


  if ((ret = ftdi_set_baudrate(&ftdic, BAUD)) < 0)
  {
    fprintf(stderr, "%s: unable to set baudrate: %d (%s)\n", *argv, ret, 
		    ftdi_get_error_string(&ftdic));
    exit_gracefully(&ftdic, EXIT_CODE_FAILURE);
  }
  
  if ((ret = ftdi_set_line_property(&ftdic, 8, 2, NONE)) < 0)
  {
    fprintf(stderr, "%s: unable to set line property: %d (%s)\n", *argv, ret,
		    ftdi_get_error_string(&ftdic));
    exit_gracefully(&ftdic, EXIT_CODE_FAILURE);
  }
 
  if ((ret = ftdi_setflowctrl(&ftdic, SIO_RTS_CTS_HS)) < 0) {
    fprintf(stderr, "%s: unable to setup flow control: %d (%s)\n", *argv, ret,
		    ftdi_get_error_string(&ftdic));
    exit_gracefully(&ftdic, EXIT_CODE_FAILURE);
  }

  /*if ((ret = ftdi_set_latency_timer(&ftdic, 10)) < 0)
  {
    fprintf(stderr, "%s: unable to set latency timer: %d (%s)\n", *argv, ret,
		    ftdi_get_error_string(&ftdic));
    exit_gracefully(&ftdic, EXIT_CODE_FAILURE);
  }*/
 
  buf[0] = operation;
  buf[2] = 0; buf[3] = 0; buf[4] = 0;

  switch (operation)
  {
    case COMMAND_RELAY_SET:
      buf[1] = char_argument;
      break;
    
    case COMMAND_RELAY_ON: case COMMAND_RELAY_OFF:
    case COMMAND_RELAY_TOGGLE:
      buf[1] = (1 << (char_argument-1));
      break;
    
    case COMMAND_RELAY_TIME_ON:
    case COMMAND_RELAY_TIME_OFF:
    case COMMAND_RELAY_TIME_CYCLIC:
      buf[1] = char_argument-1;
      buf[2] = (int_argument & 0xff); // low byte
      buf[3] = (int_argument >> 8);   // high byte
      break;

    default:
      break;
  }
  
  /* These values might not make much sense are vital to the correct
   * funtion of this program, so better don't touch them. */
  ftdi_write_data_set_chunksize(&ftdic, 1);
  ftdi_read_data_set_chunksize(&ftdic,  4);
  
  /* send the command */
  if (ftdi_write_data(&ftdic, buf, COMMANDO_LENGTH) != COMMANDO_LENGTH)
  {
    fprintf(stderr, "%s: unable to send command: %s\n", *argv, 
		    ftdi_get_error_string(&ftdic));
    exit_gracefully(&ftdic, EXIT_CODE_FAILURE);
  }
 
  /* Read the card's response. */
  start_time = time(NULL); 
  while ((ret = ftdi_read_data(&ftdic, buf, 1)) == 0) {
    usleep(500);
    if (time(NULL)-start_time >= 2) {
      fprintf(stderr, "%s: unable to read card response, the operation might have "
      		      "failed\n", *argv);
      exit_gracefully(&ftdic, EXIT_FAILURE);
    }
  }
  
  if (operation == COMMAND_GET_STATUS && buf[0] <= ((1 << 7)-1))
  {
     printf("relay status: %i (0b%s%s%s%s%s%s)\n", buf[0],
            (buf[0] & (1 << 5)) ? "1" : "0", 
	    (buf[0] & (1 << 4)) ? "1" : "0",
	    (buf[0] & (1 << 3)) ? "1" : "0",
            (buf[0] & (1 << 2)) ? "1" : "0",
	    (buf[0] & (1 << 1)) ? "1" : "0",
	    (buf[0] & (1 << 0)) ? "1" : "0");
     exit_gracefully(&ftdic, EXIT_CODE_OK);
  }

  if (buf[0] != RESPONSE_OK)
  {
    fprintf(stderr, "%s: relay card returned: %s\n", *argv, card_strerror(buf[0]));
    exit_gracefully(&ftdic, EXIT_FAILURE);
  }
  
  /* we can exit now */
  exit_gracefully(&ftdic, EXIT_CODE_OK);
  return 0; // to make the compiler happy
}

void exit_gracefully(struct ftdi_context* ftdic, char exit_code)
{
  ftdi_usb_purge_buffers(ftdic);
  ftdi_usb_close(ftdic); 
  ftdi_deinit(ftdic);
  
  exit(exit_code);
}

int valid_argument(const char* str)
{
  int i;

  for (i=0; i<strlen(str); i++)
  {
    if (!isdigit(str[i]) && (str[i] != '.'))
      return 0;
  }

  return 1;
}

const char* card_strerror(int error)
{
  const char* message = "no error";
  
  switch (error)
  {
    case RESPONSE_OK:
      message = "all fine";
      break;
    case RESPONSE_INVALID_COMMAND:
      message = "invalid command";
      break;
    case RESPONSE_INVALID_ARGUMENT:
      message = "invalid command argument";
      break;
    case RESPONSE_TRANSMISSION_ERROR:
      message = "transmission error";
      break;
  }

  return message;
}

void usage(char *name)
{
  printf("\nrelay control program usage ==================================================\n"
	 "  -?/--help .............. dump this screen\n"
	 "  -V/--version ........... echo some program information\n"
	 "  -o/--on <num>: ......... switch relay <num> on\n"
	 "  -f/--off <num>: ........ switch relay <num> off \n"
	 "  -t/--toggle <num>: ..... toggle relay <num> \n"
	 "  -s/--set <mask>: ....... set the status of all relays to <mask>\n"
	 "  -S/--status: ........... get the current relay status\n"
	 "  -v/--interval <units> .. specify a timing interval (in minutes)\n"
	 "  -c/--cyclic: ........... makes a timing operation (-v) cyclic\n"
         "  -a/--address <serial> .. addresses a specific card if multiple are installed\n"
	 "  -d/--delete-timers ..... deletes all active timers\n"
	 "  -l/--list-devices ...... lists all found FT232 devices\n\n");
  exit(0);
}

void version(void)
{
  printf("\nThis is the relay control program version %s ($Revision: 26 $)\n"
	 "----------------------------------------------------------------\n"
	 "  written by Michael Gross, 2007\n"
	 "  binary compiled: %s %s\n\n"
	 "This program can be redistributed under the terms of the GNU GPL version 2\n"
	 "or later. For more information about this software and the hardware, visit\n"
	 "my homepage at http://www.coremelt.net. As usual with free software, there\n"
	 "is ABSOLUTELY NO WARRANTY. For details, refer to the GPL.\n\n", VERSION, 
	 __DATE__, __TIME__);
  
  exit(0);
}
