#!/home/pi/DFRobotUPS/.venv/bin/python3
# coding=utf-8
import datetime
from enum import Enum
import os
from signal import signal,SIGINT
import smbus
import sys
from time import sleep

class Status(Enum):
    DISCHARGING = -1
    STEADY = 0
    CHARGING = 1

class Main(object):
    def __init__(self):
        # define I2C addressing on I2C bus 1, address 0x10
        self.bus = smbus.SMBus(1)
        self.addr = 0x10

        # set up means to break out of program
        signal(SIGINT, self.QuitGracefully)
        self.deviceStatus = Status.STEADY

        shutdownRequested = False
        upsVer = self.ReadUpsVersion()
        sys.stdout.write("UPS version 0x{0:02x}\n".format(upsVer))
        lastBattery = self.ReadBatteryCharge()
        update = datetime.datetime.now().strftime("%d-%b-%y %H:%M:%S") +' battery={:.2f}% '
        sys.stdout.write(update.format(lastBattery))
        sys.stdout.flush()

        self.lastMessage = datetime.datetime(2020, 1, 1, 0, 0, 0, 0, tzinfo=None)

        while(True):
            battery = self.ReadBatteryCharge()

            if (battery >= 99.50):
                self.deviceStatus = Status.STEADY

            elif (lastBattery > battery):
                timeSinceLastMessage =  (datetime.datetime.now(None) - self.lastMessage).total_seconds()
                messageInterval = (battery // 10) * 60
                if (timeSinceLastMessage > messageInterval):
                    print()
                    message = "UPS battery discharging. Battery level={0:.2f}%".format(battery)
                    os.system("wall " + message)
                    self.lastMessage = datetime.datetime.now(None)

                if (battery < 15.0 and not shutdownRequested):
                    os.system('sudo shutdown -h +3')
                    shutdownRequested = True

                self.deviceStatus = Status.DISCHARGING

            elif (lastBattery < battery):
                if (self.deviceStatus == Status.DISCHARGING):
                    print()
                    message = "UPS battery charging. Battery level={0:.2f}%".format(battery)
                    os.system("wall " + message)
                    self.lastMessage = datetime.datetime.now(None)

                if (shutdownRequested):
                    os.system('sudo shutdown -c "Shutdown due to low battery is cancelled" ')
                    shutdownRequested = False

                self.deviceStatus = Status.CHARGING

            lastBattery = battery
            self.ShowProgress()
            now = datetime.datetime.now()

            if (now.second % 60 == 0):
                print()
                update = now.strftime("%d-%b-%y %H:%M:%S") +' battery={0:.2f}% '
                sys.stdout.write(update.format(battery))
                sys.stdout.flush()
            sleep(1)

    def QuitGracefully(self, signalNumber=0, stackFrame=0):
        print()
        sys.exit(0)
	
    def ReadUpsVersion(self):
        try:
            ver = self.bus.read_byte_data(self.addr, 0x02)
            ver = 0x00 if ver == 0xdf else ver
            return ver
        except IOError:
            # try again if exception
            return 0x00   

    def ReadBatteryCharge(self):
        try:
            # compute battery life percentage according to formula set by board manufacturer
            socH = self.bus.read_byte_data(self.addr, 0x05)
            socL = self.bus.read_byte_data(self.addr, 0x06)
            battery = ((socH << 8) + socL) * 0.003906
            return battery
        except IOError:
            # try again if exception
            return self.ReadBatteryCharge()

    def ShowProgress(self):
        output = {
            Status.DISCHARGING: "-",
            Status.STEADY: ".",
            Status.CHARGING: "+"
        }
        sys.stdout.write(output[self.deviceStatus])
        sys.stdout.flush()

# program entry point. it all starts here.
if __name__ == '__main__':
    main = Main()

