import mraa
import sys
import socket
import fcntl
import struct
import json
from ubidots import ApiClient
import time
import pyupm_i2clcd as lcd
import math
HOST = ''  # Symbolic name meaning all available interfaces
PORT = 2211  # Arbitrary non-privileged port
CLIENT_PORT = 4000
CLIENT_IP = "192.168.96.151"
sensor_values = {}
B=3975
sys.stdout.write("Initializing UART...")
u=mraa.Uart(0)
u.setBaudRate(9600)
u.setMode(8, mraa.UART_PARITY_NONE, 1)
u.setFlowcontrol(False, False)
print("setting UART done")
# Initialize Jhd1313m1 at 0x3E (LCD_ADDRESS) and 0x62 (RGB_ADDRESS)
myLcd = lcd.Jhd1313m1(0, 0x3E, 0x62)
suffix = ':'
grocery_list = []
data_file = open("sensor_data.txt", "rw+")
car_parked = False
temperature = "0"
homeLocked = False
data_has_arrived = False
x = mraa.I2c(0)
x.address(0x77)
if x.readReg(0xd0) != 0x55:
    print("error")
x.writeReg(0xf4, 0x2e)
a=mraa.Aio(0)
led = mraa.Gpio(3)
led.dir(mraa.DIR_OUT)
motionSensor = mraa.Gpio(2)
motionSensor.dir(mraa.DIR_IN)
ldr = mraa.Aio(1)

knockSensor = mraa.Gpio(12)
knockSensor.dir(mraa.DIR_IN)
gasSensor = mraa.Aio(2)
buzzer = mraa.Gpio(6)
buzzer.dir(mraa.DIR_OUT)
buzzer.write(0)
led.write(0)
buzzer_going = False
led_mobile = False

try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg :
    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
print 'Socket bind complete' 
s.settimeout(0.001)
car_moving = False;
car_out_button = mraa.Gpio(4)
car_out_button.dir(mraa.DIR_IN)
data_json = {}
for i in range(0,5):
    try:
        print "Requesting Ubidots token"
        api = ApiClient('a1cc77700e5a0696bc8f9480fe78df55c73e982e')
        break
    except:
        print "No internet connection, retrying..."
        time.sleep(1)

def deleteContent(pfile):
    pfile.seek(0)
    pfile.truncate()

def write_date_in_file():
    deleteContent(data_file)
    #data_file.write("CarStatus: " + str(car_parked) + "\n")
    #data_file.write("GroceryList: " + str(grocery_list) + "\n")
    #data_file.write("Temperature: " + str(temperature) + "\n")
    #data_file.write("HomeLocked: " + str(homeLocked) + "\n")
    
    data_json["CarStatus"] = car_parked
    data_json["GroceryList"] = grocery_list
    data_json["Temperature"] = temperature
    data_json["HomeLocked"] = homeLocked
    json.dump(data_json, data_file)
    #print data

def prepareDataToSend():
    stringToSend = ""
    if car_parked == True:
        stringToSend = "T"
        if buzzer_going == True:
            stringToSend += "A"
        else:
            stringToSend += ","
    else:
        stringToSend = "F"
        if buzzer_going == True:
            stringToSend += "A"
        else:
            stringToSend += ","
    count = 0
    for st in grocery_list:
        if st == "Eggs":
            stringToSend += str("1") + ","
        elif st == "Milk":
            stringToSend += str("2") + ","
        elif st == "Bread":
            stringToSend += str("3") + ","
        elif st == "Butter":
            stringToSend += str("4") + ","
        elif st == "Cheeze":
            stringToSend += str("5") + ","
        elif st == "Vegetables":
            stringToSend += str("6") + ","
        elif st == "Meat":
            stringToSend += str("7") + ","
        elif st == "Juice":
            stringToSend += str("8") + ","
        elif st == "Oil":
            stringToSend += str("9") + ","
        count = count + 1
        if count == 4:
            exit
    #if count == 4:
    #    grocery_list[:] = []
    if count < 4:
        for index2 in range(count, 4):
            stringToSend += "-,"
    print stringToSend
    return (stringToSend, count)        

def get_ip_address(ifname):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def tag_value_check(tag):
    tag = tag.strip(':')
    print "Tag to compare : " + tag
    if tag == "54" or tag == "9":
        return True
    else:
        return False

def key_pad_value_check(value):
    value = value.strip(':')
    print "Value to compare : " + value
    if value == "1":
        grocery_list.append("Eggs")
    elif value == "2":
        grocery_list.append("Milk")
    elif value == "3":
        grocery_list.append("Bread")
    elif value == "4":
        grocery_list.append("Butter")
    elif value == "5":
        grocery_list.append("Cheeze")
    elif value == "6":
        grocery_list.append("Vegetables")
    elif value == "7":
        grocery_list.append("Meat")
    elif value == "8":
        grocery_list.append("Juice")
    elif value == "9":
        grocery_list.append("Oil")

while 1:
    if car_moving == False:
        #myLcd.clear()
        myLcd.setColor(255, 255, 0)
        myLcd.setCursor(0, 0)
        ip_address = get_ip_address('wlan0')
        myLcd.write(ip_address)
    strRec = ""
    #temperature = str(x.readWordReg(0xf6))
    if u.dataAvailable():
        strRec = u.readStr(3)
        print "Recieved on UART " + strRec
    if strRec.endswith(suffix):
        print "Got complete command"
        data_has_arrived = True
        if strRec.startswith("T"):
            print "Received a Tag"
            if tag_value_check(strRec.replace("T", "")) == True :
                u.writeStr("F")
                car_moving = True;
                print "Parking Car!"
                myLcd.clear()
                myLcd.setColor(255, 255, 0)
                myLcd.write("Parking Car!")
            else:
                print "Wrong Authentication"
                car_moving = False;
                myLcd.clear()
                myLcd.setColor(255, 0, 0)
                myLcd.write("Wrong Authentication")
        if strRec.startswith("K"):
            print "Received a KeyPad Value"
            key_pad_value_check(strRec.replace("K", ""))
            print grocery_list[len(grocery_list) - 1]
            data_has_arrived = True
    if strRec.startswith("1"):
        car_moving = False
        car_parked = True
        data_has_arrived = True
    if strRec.startswith("0"):
        car_moving = False;
        car_parked = False
        print "Car moved out!!"
        data_has_arrived = True
    if data_has_arrived == True :
        write_date_in_file()
        my_variable_temp = api.get_variable('57084dcb76254210850f1872')
        my_variable_temp.save_value({'value': temperature})
        my_variable_car = api.get_variable('57084e087625421217bffa8c')
        my_variable_alarm = api.get_variable('5708dbcb7625423c8abd9f8b')
        if car_parked == True :
            my_variable_car.save_value({'value': 1})
        else:
            my_variable_car.save_value({'value': 0})
        if buzzer_going == True:
            my_variable_alarm.save_value({'value': 1})
        else:
            my_variable_alarm.save_value({'value': 0})
        data_has_arrived = False
        addr = (CLIENT_IP, CLIENT_PORT)
        #file_data = data_file.read()
        (stringToSend, count) = prepareDataToSend()
        s.sendto(stringToSend , addr)
        print 'Message[' + str(addr[0]) + ':' + str(addr[1]) + '] - ' + stringToSend
        if count == 4:
            grocery_list[:] = []
    #if car_parked == True:
    data = ""
    try:
        d = s.recvfrom(1024)
        data = d[0]
    except socket.timeout:
        blabla = ""
        #print 'Socket Timeout'
    #print "Button Value: " + str(car_out_button.read())
    if data == "PO" or car_out_button.read() == 1:
        u.writeStr("B")
        print "Moving Car out!"
        myLcd.clear()
        myLcd.setColor(0, 255, 255)
        myLcd.write("Moving Car Out!")
        car_moving = True;
        data_has_arrived = True
    if data == "A0":
        myLcd.clear()
        myLcd.setColor(255, 255, 0)
        myLcd.write("ALARM Gone")
        buzzer.write(0)
        buzzer_going = False
        data_has_arrived = True
    if data == "ON":
        print data
        myLcd.clear()
        myLcd.setColor(255, 255, 0)
        myLcd.write("Light On!")
        led.write(1)
        led_mobile = True
    if data == "OFF":
        print data
        myLcd.clear()
        myLcd.setColor(0, 0, 0)
        myLcd.write("Light Off!")
        led.write(1)
        led_mobile = False
    raw_val = a.read()
    resistance=(1023-raw_val)*10000/raw_val
    temperature=1/((resistance/10000)/B+1/298.15)-273.15
    
    if led_mobile == False:
        if (motionSensor.read() == 1 and ldr.read() < 300):
            led.write(1)
        else:
            led.write(0)
    
    if knockSensor.read() == 0:
        myLcd.clear()
        myLcd.setColor(255, 0, 0)
        myLcd.write("!ALARM!")
        buzzer.write(1)
        buzzer_going = True
        data_has_arrived = True
        car_moving = False
    
    #print gasSensor.read()
    if gasSensor.read() > 350:
        myLcd.clear()
        myLcd.setColor(255, 0, 0)
        myLcd.write("!ALARM!")
        buzzer.write(1)
        buzzer_going = True
        data_has_arrived = True
        car_moving = False
    #print str(temperature)