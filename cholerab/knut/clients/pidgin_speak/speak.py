#!/usr/bin/python
import string
CNOT="../cnot/index %s %s"
host="pornocauster"
def speakOwn(account, receiver,message):
    speak(account,receiver,message,"","");
def speak(account, sender, message, conversation, flags):
    bus = dbus.SessionBus()
    obj = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
    purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")
    import subprocess
    message = message.replace("'",'"')
    print message
    #cmd = "espeak -v de '%s'" % message
    cmd = CNOT % (host,message)
    subprocess.call(cmd,shell=True)
import dbus, gobject

from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

bus.add_signal_receiver(speak,
                    dbus_interface="im.pidgin.purple.PurpleInterface",
                    signal_name="ReceivedImMsg")

bus.add_signal_receiver(speakOwn,
                    dbus_interface="im.pidgin.purple.PurpleInterface",
                    signal_name="SentImMsg")
loop = gobject.MainLoop()
loop.run()
