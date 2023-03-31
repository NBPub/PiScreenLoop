# GPIO: LCD screen, button, light
import LCDdriver
screen = LCDdriver.lcd()
from gpiozero import LED, Button
red = LED(21)
butt = Button(14, hold_time=2)

# python
from subprocess import check_call
from time import sleep, time, asctime
from pathlib import Path

# local scripts
from stats import PiStat, AQI, HoleStat, HoliPiStat, pi_stat_formatter, doom_check, \
                  docker_grab, container_updates, cat_image, forecast, swag_stat
from RTH import RTHupdate
from clock import clocker
# from snow import hoodoo, bachelor, conditions

# template engine for homepage, not in repo for now
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment( 
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)
template = env.get_template('template_jinja.html')

# power button functions
def indicator():
    screen.lcd_clear()
    red.blink(on_time=0.4,off_time=0.2,n=5)
    screen.lcd_display_string('Hold button to',1)
    screen.lcd_display_string('shut\'r down',2)
    sleep(3)
def shutdown():
    screen.lcd_clear()
    red.blink(on_time=0.8,off_time=0.2,n=5)
    screen.lcd_display_string('Shutting down',1)
    screen.lcd_display_string('in 3 seconds',2)
    sleep(3)
    screen.lcd_clear()
    screen.lcd_display_string('z Z z Sleepy',1)
    screen.lcd_display_string('Cat z Z z Z z',2)
    sleep(2)
    check_call(['sudo', 'poweroff'])

# wrapper for temperature display function, continuous average up to 3 readings
def tempdisplay():
    RT = []
    RH = []        
    for _ in range(3):
        RT,RH, T = RTHupdate(RT,RH, screen, red)
    if 'T' in locals():
        return T # room temperature for homepage
    else:
        return 22 # error code?

# pre-allocate variables
lastAQI = None
aqistat = None
lastcat = time()-600
cat = None
swagstat = (None,None,-1)

while True:
    butt.when_pressed = indicator
    butt.when_held = shutdown
    try:
        # Screen Cycle
        clocker(screen) # scrolling clock or quote
        piholestat = HoleStat(screen,red) # queries blocked
        raspistat = PiStat(screen) # CPU / RAM / Temp
        holistat = HoliPiStat(screen,red) # load, CPU / RAM / Temp
        red.off()
        
        if lastAQI != int(asctime()[11:13]): # AQI+weather, update every hour
            aqiHTML, lastAQI, aqistat = AQI(screen,red, None, None, [])
            red.off()
            W_now, W_later, W_HTML = forecast(screen, None, None, {})
        else:
            aqiHTML, lastAQI, aqistat = AQI(screen, red, aqistat, lastAQI, aqiHTML)
            red.off()
            W_now, W_later, W_HTML = forecast(screen, W_now, W_later, W_HTML)

        inside_temp = tempdisplay() # RTH and time, return final temp
        
        # Check for Doom connection, update homepage AKA basecamp
        if doom_check():
            updates = container_updates() # RSS feeds for container updates
            dockerstat = docker_grab() # container status
            # Update Server stats once per hour
            if swagstat[2] != int(asctime()[11:13]):
                swagstat = swag_stat()
            raspistat = pi_stat_formatter(raspistat) # scroll bar stats
            holistat = pi_stat_formatter(holistat) # scroll bar stats

            if cat == None or time() - lastcat > 600:
                cat, lastcat = cat_image() # cat image every 10 minutes
            
            # styling for RT display, use match later
            if inside_temp > 78:
                color = 'danger'
            elif inside_temp < 70:
                color = 'info'
            elif inside_temp == 22:
                color = 'dark'
            else:
                color = 'success'
            RT_HTML = [color, str(int(inside_temp))]
                
            # write data to HTML for homepage    
            with open(Path(Path.cwd(),'homepage.html'), 'w', encoding='utf-8') as page:
                page.write(template.render(\
    aqiHTML=aqiHTML, W_HTML=W_HTML, RT_HTML=RT_HTML, updates=updates, swagstat=swagstat, cat=cat,
    holistat=holistat, dockerstat=dockerstat, raspistat=raspistat, piholestat=piholestat,
                                           ))   

        # restart loop
        screen.lcd_display_string('‿( ́ ̵ _-`)‿',1)
        screen.lcd_display_string(' ╭∩╮（︶︿︶）╭∩╮ ',2)
        red.off()
        continue
    except Exception as e:
        # print(e)
        with open("error_log.txt","a") as file:
            file.write(f'\t{asctime()[:-5]}\n{e}\n')
        # print(asctime()[:-5],'\n\t',e)
        continue
                

# ~~Stuff for Snow weather / mountain conditions~~
# ~OUTSIDE loop~
# h_depth = [None]*2
# b_depth = [None]*4
# weather = [None]*15
# ~INSIDE loop~
# from time import asctime
# minute = asctime()[14:16]
# hour = asctime()[11:13]
# day = asctime()[8:10]   
# weather = conditions(screen, weather, hour, minute)
# h_depth = mount1(screen, h_depth, day, hour)
# b_depth = mount2(screen, b_depth, day, hour)
