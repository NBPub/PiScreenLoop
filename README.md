# Pi Screen Loop

A collection of python scripts to populate a scrolling display on a 16x2 LCD screen and to update a homepage file.

<img src="https://raw.githubusercontent.com/NBPub/PiScreenLoop/main/logo.svg" title="PiScreen">

## Acknowledgements

 - Driver for LCD screen provided by [DenisFromHR](https://gist.github.com/DenisFromHR/cc863375a6e19dce359d), who sourced code from this [blog post](https://www.recantha.co.uk/blog/?p=4849)
 - [Adafruit_Python_DHT](https://github.com/adafruit/Adafruit_Python_DHT) used for DH22 temperature and humidity sensor 
 - [GPIOzero](https://gpiozero.readthedocs.io/en/stable/) used for other GPIO devices (lights, buttons)
 - Other Python libraries:
   - [python-dotenv](https://github.com/theskumar/python-dotenv)
   - [Jinja2](https://jinja.palletsprojects.com/en/)
   - [psutil](https://github.com/giampaolo/psutil)
   - [requests](https://requests.readthedocs.io/), basic [urllib](https://docs.python.org/3/library/urllib.html) could be used instead
       - [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) and [Selenium](https://www.selenium.dev/) utilized in *currently unused* [snow.py](/snow.py) scripts
   
   
## Equipment

**Device**: Raspberry Pi 2B

**GPIO peripherals**: DHT22, LCD1602, basic LED light(s)+button(s)

## Code

I use a [cron job](https://en.wikipedia.org/wiki/Cron) to run [main.py](/main.py) with each restart.

```bash
crontab -e

@reboot sleep 30; cd <path_to_directory> && python main.py
```

URLs, API keys, and tokens are supplied to the scripts via `<path_to_directory>/.env`. This file is not provided in this repository. 
See [example.env](/example.env) to get an idea of how various API calls are performed. 
Links to the API services are also provided.

----

**Main Purpose** - loop through functions and populate screen

  0. Initialize GPIO connections, Assign functions to button | [main.py](/main.py)
  1. Streaming clock display or [random quote](https://github.com/lukePeavey/quotable) via API | [clock.py](/clock.py)
  2. Statistics for [Pi-Hole](https://pi-hole.net/), via API | [HoleStat](/stats.py#L135)
  3. Local system statistics, via psuitil | [PiStat](/stats.py#L26)
  4. External server statistics, via API using psutil | [ServerStat](/stats.py#L152)
  5. AQI information, via EPA AirNow API | [AQI](/stats.py#L103)
  6. Local weather forecast, via weather.gov API | [forecast](/stats.py#L42)
  7. Room temperature and humidity via DHT22 | [RHT update](/RTH.py)
  8. Errors within the loop are [written](/main.py#L125) to `error_log.txt`, and the loop continues
  
*certain API calls are limited in frequency, for example, AQI information is only queried once per hour*

**[text_scroll](https://github.com/NBPub/PiScreenLoop/blob/main/stats.py#L10)** provides a horizontal "scroll" feature to display long text blocks, and has tunable parameters. 
The screen only hits 16 characters across.

----

**Secondary Purpose** - if computer "DOOM" is powered on, add information to homepage.html file

  0. At end of above loop, check DOOM availability via Syncthing API | [doom_check]()
  1. If available, query [docker API](https://github.com/NBPub/PiScreenLoop/blob/main/stats.py#L196) and [RSS API](https://github.com/NBPub/PiScreenLoop/blob/main/stats.py#L182) for container/update information
      - also add a [random cat](https://github.com/NBPub/PiScreenLoop/blob/main/stats.py#L226) image! See [Cat Data Pages](https://cat-data-pages.onrender.com/)
  2. Add pertinent information into HTML file via Jinja2 template, Syncthing syncs local file with DOOM
  3. DOOM uses the HTML file as a homepage. It's up to date with relevant information.

*Similar to `.env`, the actual template file is not provided in this repository; it would be included as `<path_to_directory>/templates/<template_name>.html`. A very basic example is provided: [example_jinja](/example_jinja.html)*

 