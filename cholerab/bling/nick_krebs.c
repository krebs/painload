#include <sysinit.h>

#include "basic/basic.h"
#include "basic/config.h"

#include "lcd/lcd.h"
#include "lcd/print.h"
#include "filesystem/ff.h"

#include "usetable.h"

#define IMAGEFILE "krebs.lcd"

void ram(void) {
    FIL file;
    int res;
    UINT readbytes;
    uint8_t state = 0;
    int dx, dy, dwidth;

    uint32_t framems = 100;

    res = f_open(&file, IMAGEFILE, FA_OPEN_EXISTING|FA_READ);
    if(res)
            return;

    /* calculate height */
    setExtFont(GLOBAL(nickfont));
    dwidth = DoString(0, 0, GLOBAL(nickname));
    dy = (RESY - getFontHeight());
    dx = (95 - dwidth)/2;

    getInputWaitRelease();
    while(!getInputRaw()) {
        lcdFill(0x55);

        res = f_read(&file, (char *)lcdBuffer, RESX*RESY_B, &readbytes);
        if (res)
            return;

        if (readbytes < RESX*RESY_B) {
            f_lseek(&file, 0);
            continue;
        }

        setExtFont(GLOBAL(nickfont));
        DoString(dx, dy, GLOBAL(nickname));

        lcdDisplay();

        if(framems < 100) {
            state = delayms_queue_plus(framems, 0);
        } else {
            getInputWaitTimeout(framems);
        }
    }

    if(state)
        work_queue();
}
