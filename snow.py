from bs4 import BeautifulSoup
from urllib.request import Request
from urllib.request import urlopen
from time import sleep, asctime
from selenium import webdriver

from os import getloadavg, getenv
from dotenv import load_dotenv
load_dotenv()

def mount1(screen, h_depth, day, hour):
    if h_depth[1] != day and int(hour)>6:
        screen.lcd_clear()
        screen.lcd_display_string('. . . . loading',1)
        screen.lcd_display_string(getenv('mountain1_name'),2)
        raw_request = Request(getenv('mountain1_URL'))
        raw_request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0')
        raw_request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        resp = urlopen(raw_request)
        raw_html = resp.read()
        soup = BeautifulSoup(raw_html, 'html.parser').pre
        h_depth = [soup.contents[0].split('\n')[3]]
        del raw_request, resp, raw_html, soup
        h_depth.append(asctime()[8:10]) # updated on day, s/t only one call per day
    
    screen.lcd_clear()
    screen.lcd_display_string(h_depth[0].rstrip("\r")[7:],1)
    screen.lcd_display_string(f"getenv('mountain1_name')  Snow",2)
    sleep(2)    
    return h_depth
    
def mount2(screen, b_depth, day, hour):
    if b_depth[3] != day and int(hour)>6:
        screen.lcd_clear()
        screen.lcd_display_string('. . . . loading',1)
        screen.lcd_display_string(getenv('mountain2_name'),2)
        driver = webdriver.Chrome()
        driver.get(getenv('mountain2_URL'))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        depths_tags = soup.find_all('h3',class_='amount ng-binding')
        durations_tags = soup.find_all('p',class_='duration ng-binding')
        depths = []
        durations = []
        b_depth = []
        keys = [3,4,8]
        
        for tag in depths_tags:
            depths.append(tag.text.strip())
        for tag in durations_tags:
            durations.append(tag.text.strip())
        for val in keys:
            b_depth.append(f'{durations[val]}   {depths[val]}')
        
        del depths_tags, durations_tags, soup, depths, durations, keys
        b_depth.append(asctime()[8:10]) # updated on day, s/t only one call per day

    for i in range(3):
        screen.lcd_clear()
        screen.lcd_display_string(b_depth[i],1)
        screen.lcd_display_string(f"{getenv('mountain2_name')}  Snow",2)
        sleep(2)
    return b_depth
    
    
def conditions(screen, weather, hour, minute):
    if weather[14] != hour and int(minute)>15:
        screen.lcd_clear()
        screen.lcd_display_string('. . . . loading',1)
        screen.lcd_display_string('mountain cond',2)
        # M2 info
        URL = getenv('mountain2_cond_URL')
        page = urlopen(Request(URL))
        soup = BeautifulSoup(page.read(), 'html.parser')
        F = soup.find('p',class_= 'myforecast-current-lrg').contents[0]
        C = soup.find('p',class_= 'myforecast-current-sm').contents[0]
        conditions = str(soup.find(id='current_conditions_detail').contents[1]).split('</td>')
        del URL, page, soup
        del conditions[4:10]
        del conditions[6:]
        
        weather = []
        weather.append(f"{getenv('mountain2_name')} Temp")
        weather.append(f'{F}  /  {C}')
        for i, val in enumerate(conditions):
            if i % 2 == 0:
                weather.append(val[val.find("<b>")+3:val.find("</b>")])
            else:
                weather.append(val[val.find("d>")+2:])
        if weather[6] == 'Last update': # check if wind chill is listed
            weather[7] = weather[7][18:32] # if not, keep last update but adjust text for screen
        
        # Hoodoo
        URL = getenv('mountain1_cond_URL')
        page = urlopen(Request(URL))
        soup = BeautifulSoup(page.read(), 'html.parser')
        F = soup.find('p',class_= 'myforecast-current-lrg').contents[0]
        C = soup.find('p',class_= 'myforecast-current-sm').contents[0]
        conditions = str(soup.find(id='current_conditions_detail').contents[1]).split('</td>')
        del conditions[4:]
        del URL, page, soup

        weather.append(f"{getenv('mountain1_name')} Temp")
        weather.append(f'{F}  /  {C}')
        for i, val in enumerate(conditions):
            if i % 2 == 0:
                weather.append(val[val.find("<b>")+3:val.find("</b>")])
            else:
                weather.append(val[val.find("d>")+2:])
                
        weather.append(asctime()[11:13]) # updated on hour, s/t only one call per hour
        
    for i in range(int(len(weather)/2)):
        screen.lcd_clear()
        screen.lcd_display_string(weather[2*i],1)
        screen.lcd_display_string(weather[2*i+1].replace('°',''),2)
        sleep(2)
    return weather