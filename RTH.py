from time import sleep, asctime
import board
import adafruit_dht
dht = adafruit_dht.DHT22(board.D27, use_pulseio=False)
       
def RTHupdate(RT,RH,screen, red):
    reading = False
    while reading == False:
        try:
            RT.append(dht.temperature*9/5 +  32) # C -> F
            RH.append(dht.humidity)
            reading = True
        except:
            sleep(3)
            reading = False 
    T = round(sum(RT)/len(RT),1) # continuous average of measurements
    H = round(sum(RH)/len(RH),1)
    if T > 80:
        red.on()
    else:
        red.off()
    screen.lcd_display_string('%sF   %s%% RH' % (T,H),1)
    screen.lcd_display_string(asctime()[4:-8],2)
    sleep(5)
    return RT, RH, T