#include "system.h"
#include "conf.h"
#include "logger.h"
#include "net.h"
#include "route.h"
#include "utils.h"
#include "xalloc.h"

int device_fd = -1;
char *device = NULL;
char *iface = NULL;


bool setup_device(void) {
          device = xstrdup("null");
                  iface = xstrdup("null");
                          device_fd = -1;

                                  return true;
}

void close_device(void) {
          free(device);
                  free(iface);
}

bool read_packet(vpn_packet_t *packet) {

          return true;
}

bool write_packet(vpn_packet_t *packet) {
                  return true;
}

void dump_device_stats(void) {
}
