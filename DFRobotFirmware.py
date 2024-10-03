import smbus
addr=0x10 #ups i2c address
bus=smbus.SMBus(1) #i2c-1
firmware=bus.read_byte_data(addr,0x02)
vcellH=bus.read_byte_data(addr,0x03)
vcellL=bus.read_byte_data(addr,0x04)
socH=bus.read_byte_data(addr,0x05)
socL=bus.read_byte_data(addr,0x06)

firmware = 0x00 if firmware == 0xdf else firmware
capacity=(((vcellH&0x0F)<<8)+vcellL)*1.25 #capacity
electricity=((socH<<8)+socL)*0.003906 #current electric quantity percentage

print("firmware=0x%02x" % firmware)
print("capacity=%dmV"%capacity)
print("electricity percentage=%.2f"%electricity)

list = bus.read_i2c_block_data(addr, 0x00)
print('[',", ".join("0x{:02x}".format(num) for num in list),']')
## the documentation
## https://wiki.dfrobot.com/UPS%20HAT%20for%20Raspberry%20Pi%20%20Zero%20%20SKU%3A%20DFR0528

