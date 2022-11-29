#steppermotor + potentie
import cgitb ; cgitb.enable()
import spidev
import RPi.GPIO as GPIO
import time
#LCD scherm
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI
import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont



#poorten rasperry pi initialiseren
GPIO.setmode(GPIO.BCM)
#GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP)  Als je met een knop werkt is deze lijn nodig

#steppermotor
# #ingangen op het LED bordje
in1 = 18
in2 = 17
in3 = 27
in4 = 22

#poorten van PI op uit en laag zetten
GPIO.setup(in1, GPIO.OUT)
GPIO.output(in1,0)

GPIO.setup(in2, GPIO.OUT)
GPIO.output(in2, 0)

GPIO.setup(in3, GPIO.OUT)
GPIO.output(in3,0)

GPIO.setup(in4, GPIO.OUT)
GPIO.output(in4,0)

#code Potmeter
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=(1000000)
def read_spi(channel):
    spidata = spi.xfer2([1, (8 + channel) << 4,0])
    return ((spidata[1] & 3) << 8) + spidata[2]

#Code LCD
DC = 23 #data control
RST = 24 #reset
SPI_PORT = 0 #spi port 0
SPI_DEVICE = 1 #cs1 pin 26

disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
disp.begin(contrast=60)
disp.clear()
disp.display()
font = ImageFont.load_default()
draw = ImageDraw.Draw(image)


#poorten van ultrasonic
trig = 2
echo = 3

GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

#grenzen
max_height = 22
min_height = 4

#functies steppermotor
def fullstop(in1, in2, in3, in4):
    GPIO.output(in1,1)
    GPIO.output(in2,0)
    GPIO.output(in3,1)
    GPIO.output(in4,0)
    time.sleep(0.005)

    GPIO.output(in1,0)
    GPIO.output(in2,1)
    GPIO.output(in3,1)
    GPIO.output(in4,0)
    time.sleep(0.005)

    GPIO.output(in1,0)
    GPIO.output(in2,1)
    GPIO.output(in3,0)
    GPIO.output(in4,1)
    time.sleep(0.005)

    GPIO.output(in1, 1)
    GPIO.output(in2, 0)
    GPIO.output(in3, 0)
    GPIO.output(in4, 1)
    time.sleep(0.005)


def fullstop_reverse(in1, in2, in3, in4):
    GPIO.output(in4, 1)
    GPIO.output(in3, 0)
    GPIO.output(in2, 0)
    GPIO.output(in1, 1)
    time.sleep(0.005)

    GPIO.output(in4, 0)
    GPIO.output(in3, 0)
    GPIO.output(in2, 1)
    GPIO.output(in1, 1)
    time.sleep(0.005)

    GPIO.output(in4,0)
    GPIO.output(in3,1)
    GPIO.output(in2,1)
    GPIO.output(in1,0)
    time.sleep(0.005)

    GPIO.output(in4, 1)
    GPIO.output(in3, 1)
    GPIO.output(in2, 0)
    GPIO.output(in1, 0)
    time.sleep(0.005)


while True:
    #potmeter naar %
    channeldata = read_spi(0)
    pot_procent = (channeldata / 1023) * 100
    pot_procent = round(pot_procent, 1)

    #afstand
    GPIO.output(trig, True)
    time.sleep(0.0001)
    GPIO.output(trig, False)

    while GPIO.input(echo) == 0:
        pass
    PulseStart = time.time()

    while GPIO.input(echo) == 1:
        pass
    PulseEnd = time.time()

    PulseDuration = PulseEnd - PulseStart
    Distance = round((PulseDuration * 17150), 2)

    #steppermotor richting
    if channeldata > 525:
        fullstop(in1, in2, in3, in4)
    elif channeldata < 505:
        fullstop_reverse(in4, in3, in2, in1)

    #sterretjes
    if Distance < 5:
        sterretjes = ""
    elif 5 < Distance < 10:
        sterretjes = "*******"
    elif 10 < Distance < 20:
        sterretjes = "**************"

    #weergave op lcd
    draw.rectangle((0, 0, LCD.LCDWIDTH, LCD.LCDHEIGHT), outline=255, fill=255)
    draw.text((1, 0), 'Potmeter: ', font=font)
    draw.text((1, 8), (str(pot_procent) + "%"), font=font)
    draw.text((1, 16), (str("Afstand: ")), font=font)
    draw.text((1, 24), (str(Distance) + "cm"), font=font)
    draw.text((1, 32), sterretjes, font=font)
    disp.image(image)
    disp.display()

    time.sleep(0.05)

    disp.clear()
    disp.display()

    #print in terminal
    print("Afsand: {}".format(Distance))
    print("Potmeter: {}".format(pot_procent))