from time import sleep, time, asctime
import requests
import json
from psutil import sensors_temperatures, virtual_memory, cpu_percent
from os import getloadavg, getenv
from dotenv import load_dotenv

load_dotenv()

def text_scroll(screen,text, clock):
    factor = 4 # divide strings into pieces, lower factor -> smaller pieces
    sleeptime = 0.6 # time to wait when scrolling through pieces
    for i in range(len(text) // factor):
        if clock == True:
            screen.lcd_display_string(asctime()[4:-5],1) # rolling clock display, to seconds
        end = i*factor+16
        if end > len(text):
            screen.lcd_display_string(text[-16:], 2) # break at end to prevent overlap
            sleep(sleeptime)
            break
        screen.lcd_display_string(text[i*factor:end], 2) # scroll through text on bottom line
        if i == 0 or i == len(text) // factor -1:
            sleep(1.5)
        sleep(sleeptime)

def PiStat(screen):
    stats =  {
        "temp": round(sensors_temperatures()['cpu_thermal'][0].current,2),
        "load": [round(val,2) for val in getloadavg()],
        "ram": virtual_memory().percent,
        "cpu": cpu_percent(),
    }
    
    RAMper  = '%s%%' % (stats["ram"])
    use = '%s%%' % (stats["cpu"])
    screen.lcd_clear()
    screen.lcd_display_string(f'CPU  {use} {round(stats["temp"],1)}C',1)
    screen.lcd_display_string(f'RAM  {RAMper}',2)
    sleep(5)
    return stats

def forecast(screen, now, later, HTML):
    if now == None or later == None or HTML == {}:
        headers = {'User-Agent': 'python-weather-screen'}
        
        # detailed forecast
        URL = getenv('forecast_URL')
        data = json.loads(requests.get(URL, headers=headers).content)['properties']
        keep = ['shortForecast', 'temperature', 'name', 'detailedForecast']
        now = {}
        later = {}
        for key in keep:
            now[key] = data['periods'][0][key]
            later[key] = data['periods'][1][key]
        del data
        
        # current forecast
        URL = getenv('forecast_hourly_URL')
        d = json.loads(requests.get(URL, headers=headers).content)['properties']['periods']
        for i, val in enumerate(d):
            if val['startTime'][11:13] == asctime()[11:13]:
                break
        del d
        
        now['screen1'] = f'{val["temperature"]}°F {val["shortForecast"]}'
        now['screen2'] = f'Wind {val["windSpeed"]} {val["windDirection"]}'
        now['temperature'] = val['temperature']
        del val
            
        # HTML for homepage AKA basecamp
        if now["temperature"] > 89:
            color = "danger"
        elif now["temperature"] < 50:
            color = "info"
        else:
            color = "warning"
        
        # HTML, first is outside temp for AQI badge
        HTML["badge"] = [color, str(now["temperature"])]
        
        # next two are detailed forecasts for scrolling text
        HTML["scrollNow"] = [now["name"], now["detailedForecast"]]
        HTML["scrollLater"] = [later["name"], later["detailedForecast"]]
        
    # LCD screen
    screen.lcd_clear()  
    # sometimes detailed forecast, else simple conditions
    if int(asctime()[15])%7 == 0 : 
        screen.lcd_display_string(now["name"],1)
        text_scroll(screen, now["detailedForecast"], False)
        screen.lcd_clear()
        screen.lcd_display_string(later["name"],1)
        text_scroll(screen, later["detailedForecast"], False)

    else:
        screen.lcd_display_string(now["screen1"],1)
        screen.lcd_display_string(now["screen2"],2)
        sleep(5)    
    screen.lcd_clear()    
    
    return now, later, HTML             

def AQI(screen,red, stats, hour, html):
    if stats == None: # update, get new stats, hour and html
        URL = f'{getenv("aqi_URL")}{getenv("aqi_key")}'
        response = json.loads(requests.get(URL).content)[0]
        stats = {
          "AQI": response['AQI'],
          "parameter": response['ParameterName'],
          "observed": f'{response["DateObserved"][-6:]}{response["HourObserved"]}:00',
        }
        del response
        if stats['AQI'] < 50:
            color = 'success'
        elif stats['AQI'] > 150:
            color = 'danger'
        else:
            color = 'warning'
        # HTML, color+value+"updated on" for AQI badge
        html.append(color)
        html.append(str(stats["AQI"]))
        html.append(stats["observed"])
        
        hour = int(asctime()[11:13])
        
    if stats['AQI'] > 100:
        red.blink(0.3)
    screen.lcd_clear()
    screen.lcd_display_string('AQI: %s ~ %s' % (stats['AQI'], stats['parameter']),1)
    screen.lcd_display_string(f'on: {stats["observed"]}', 2)
    sleep(5)
    
    return html, hour, stats
    
def HoleStat(screen,red):
    red.off()
    URL = f"{getenv('pihole_URL')}{getenv('pihole_token')}"
    hole = json.loads(requests.get(URL).content)
    keys = ['ads_blocked_today','dns_queries_today','ads_percentage_today',
            'unique_clients']
    holestats = {key:val for key,val in hole.items() if key in keys}
    del hole
    
    screen.lcd_clear()
    screen.lcd_display_string('%s / %s' % (holestats['ads_blocked_today'], holestats['dns_queries_today']),1) # ads today / queries today
    screen.lcd_display_string('%s%% blocked' % (round(holestats['ads_percentage_today'],2)),2) # ads percentage today
    sleep(5)
    return f'<li>{round(holestats["ads_percentage_today"],1)}% blocked of \
           {"{:,}".format(holestats["dns_queries_today"])} queries from \
           {holestats["unique_clients"]} clients</li></ul>'
    
def HoliPiStat(screen,red):
    URL = getenv("serverstat_URL")
    data = json.loads(requests.get(URL).content)
    if data['temp'] > 45:
        red.on()
    screen.lcd_clear()
    screen.lcd_display_string(f'LOAD  {data["load"][0]}  holi',1)
    screen.lcd_display_string(f' {data["load"][1]}     {data["load"][2]}',2)
    sleep(5)
    screen.lcd_clear()
    screen.lcd_display_string(f'CPU {data["cpu"]}%  {data["temp"]}C',1)
    screen.lcd_display_string(f'RAM {data["ram"]}%   holi',2)
    sleep(5)
    return data

def doom_check():
    try:
        URL = getenv("syncthing_URL")
        headers = {'X-API-Key': getenv("syncthing_key")}
        doom_id = getenv("syncthing_ID")
        # Query local SyncThing API
        st_connections = json.loads(requests.get(URL,headers=headers).content)['connections']
        # Returns DOOM connection status
        if doom_id in st_connections and st_connections[doom_id]['connected']:
            return True
        else:
            return False
    except:
        return False
        
def container_updates():
    # Query minifluxRSS API for container updates
    headers = {'X-Auth-Token': getenv("miniflux_key")}
    # Unread
    URL = getenv("miniflux_unread_URL")
    unread = json.loads(requests.get(URL,headers=headers).content)['total']
    color = 'success' if unread == 0 else 'danger'
    # Starred
    URL = getenv("miniflux_starred_URL")
    starred = json.loads(requests.get(URL,headers=headers).content)['total']
    
    return [color, unread, starred]

# . . . should move HTML Jinja template    
def docker_grab():
    # Query holipi Portainer API, return container info
    try:
        URL = getenv("portainer_URL")
        headers = {"X-API-Key": getenv("portainer_key")}
    
        docker = json.loads(requests.get(URL, headers=headers).content)[0]["Snapshots"][0]
        return f'<li>Containers: {docker["RunningContainerCount"]}&nbsp; ┼ &nbsp; \
                 Stopped: {docker["StoppedContainerCount"]}&nbsp; ┼ &nbsp; \
                 Stacks: {docker["StackCount"]}&nbsp; ┼ &nbsp; \
                 Images: {docker["ImageCount"]}</li></ul>'
    except:
        return '<li> ~ </li></ul>'
        
def pi_stat_formatter(stats):
    # Takes dictionary (integers and list of integers) and formats for HTML
    temp = f'{stats["temp"]} °C &nbsp;&nbsp; ┼ &nbsp;&nbsp;'
    CPU = f'{stats["cpu"]}% CPU &nbsp;&nbsp; ┼ &nbsp;&nbsp;'
    RAM = f'{stats["ram"]}% RAM &nbsp;&nbsp; ┼ &nbsp;&nbsp;'
    load = " &#9959; ".join([str(val) for val in stats["load"]])
    
    if stats["temp"] < 42:
        color = 'success'
    elif stats["temp"] > 45:
        color = 'danger'
    else:
        color = 'warning'
    
    return f'<ul class="text-{color}"><li>{temp} {CPU} {RAM} {load}</li>'

def cat_image():
    URL = getenv("cat_URL")
    try:
        cat = json.loads(requests.get(URL).content)['URL']
        return cat, time()
    except:
        return "https://cdn2.thecatapi.com/images/4kl.gif", time()
        # https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Giraffa_camelopardalis_head_%28Profil%29.jpg/640px-Giraffa_camelopardalis_head_%28Profil%29.jpg
        # https://cdn2.thecatapi.com/images/XIK3w04V9.jpg
        
def swag_stat():
    URL = getenv("fail2ban_URL")
    r = requests.get(URL)
    try:
        if r.status_code != 200:
            return (None,None, int(asctime()[11:13]))
        else:
            data = json.loads(requests.get(URL).content)
            right = f"<b>Ig:</b> {data['home']['ignores']}<br><b>Fte:</b> {data['outside']['filtrate']}"
            left = f"{data['home']['data']}<br>{data['outside']['data']}"
        return (left, right, int(asctime()[11:13]))
    except:
        return (None,None, int(asctime()[11:13]))