import time
import urllib.request
import json
from stats import text_scroll

def clocker(screen):
    screen.lcd_clear()
    if int(time.asctime()[15])%5 == 0 : # random quote feature, activates on 5th minute
        URL = 'https://api.quotable.io/random?maxLength=160'
        response = json.load(urllib.request.urlopen(URL))
        quote = '"%s"' % (response['content'])
        author = ' -%s' % (response['author'])
        text_scroll(screen, quote, True)
        screen.lcd_clear()
        text_scroll(screen, author, True)
        time.sleep(1.5)
        screen.lcd_clear()
    else:    
        for _ in range(6):
            screen.lcd_display_string(time.asctime()[4:-5],1) # rolling clock
            time.sleep(1)
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        