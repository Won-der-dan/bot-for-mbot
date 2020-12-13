import time
import json
import random
import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait


def get_settings():
    with open('settings.json', 'r') as f:
        settings_dict = json.load(f)
    with open('session.json', 'r') as f:
        session_dict = json.load(f)
    return (settings_dict, session_dict)


def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver


def get_driver():
    # First, we try to take existing driver
    try:
        driver = create_driver_session(session_dict['session_id'], session_dict['url'])
        print(driver.current_url)
        driver.get("http://roswar.ru")
        print("existing driver opened")
    except Exception as e:
        print(e)
        driver = webdriver.Firefox()  #python
        url = driver.command_executor._url       #"http://127.0.0.1:60622/hub"
        session_id = driver.session_id            #'4e167f26-dc1d-4f51-a207-f761eaf73c31'
        print(url, session_id)
        with open("session.json", "w") as session_settings_file:
            json.dump({'session_id': session_id, "url": url}, session_settings_file, indent=4, sort_keys=True)
        print("new driver created")
        driver.get("http://roswar.ru")
    return driver


def check_element_class(element, class_name):
    return class_name in element.get_attribute('class')

def login():
    print('logging in')
    email_input = driver.find_element_by_id("email-input")
    password_input = driver.find_element_by_id("pwd-input")
    submit_button = driver.find_element_by_css_selector(".td-login")
    email_input.send_keys(settings_dict['email'])
    password_input.send_keys(settings_dict['password'])
    submit_button.click()
    if driver.current_url == "http://www.roswar.ru/login/":
        print("login failed")


def go_to_alley():
    print('going to alley')
    # find_and_click_iframe_elem("a.alley")
    driver.get('http://roswar.ru/alley')


def heal():
    try:
        find_and_click_iframe_elem("div.life i.plus-icon")
    finally:
        return


def fight(fight_type):
    print("going to fighting")
    go_to_alley()
    try:
        find_and_click_iframe_elem("div."+fight_type)
        find_and_click_iframe_elem("div.button-fight")
        time.sleep(5)
        go_to_alley()
    except:
        print("you're still on timeout")
    

def find_and_click_iframe_elem(selector):
    wait(driver, 300).until(EC.frame_to_be_available_and_switch_to_it("game-frame"))
    alley_button = driver.find_element_by_css_selector(selector)
    time.sleep(5)
    alley_button.click()    
    driver.switch_to.default_content()


def check_timeout():
    return False


def main_function():
    while True:
        if check_timeout():
            continue
        if (time.time() > pet_timeout):
            upgrade_pet()
        # if (time.time() > metro_timeout):
        #     go_to_metro()
        fight('f1')
        print('wait...')
        time.sleep(300 + random.randint(0, 500))
        if random.randint(0, 10) == 9:
            print('long wait...')
            time.sleep(1200)


def go_to_metro():
    print('going to metro')
    heal()
    # find_and_click_iframe_elem('a.square')
    driver.get('http://roswar.ru/square')
    find_and_click_iframe_elem('div#square-metro-button')
    try:
        find_and_click_iframe_elem('div#action-rat-fight div.button-big')
        find_and_click_iframe_elem('.button:first-of-type')
        metro_timeout = time.time() + 1200
        if "roswar.ru/fight" in driver.current_url:
            handle_group_fight()
        pass
    except:
        print("can't go to metro")
        metro_timeout = time.time() + 1200 
        pass

def handle_group_fight():
    print('entering group fight')
    while True:
        time.sleep(20)
        if driver.find_element_by_css_selector('div.result'):
            return
        


def upgrade_pet():
    # maybe contain timeout?
    time.sleep(5)
    driver.get('http://roswar.ru/petarena/train/228830/')  # maybe track petIds?
    # first, we get all the values and try training lowest one
    wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it("game-frame"))
    focus = int(driver.find_element_by_css_selector('li[rel~="focus"] > div > span.num').text)
    loyality = int(driver.find_element_by_css_selector('li[rel~="loyality"] > div > span.num').text)
    mass = int(driver.find_element_by_css_selector('li[rel~="mass"] > div > span.num').text)
    button = driver.find_element_by_css_selector('li[rel~="focus"] button')
    if check_element_class(button, 'disabled'):
        print('pet is on training')
        pet_timeout = time.time() + int(driver.find_element_by_css_selector('span#train').get_attribute('timer'))
        driver.switch_to.default_content()
        pass
    else:
        if mass <= loyality and mass <= focus:
            button = driver.find_element_by_css_selector('li[rel~="mass"] button')
        if loyality <= focus and loyality <= mass:
            button = driver.find_element_by_css_selector('li[rel~="loyality"] button')
        button.click()
        print('pet was trained')
        driver.switch_to.default_content()
        pass


(settings_dict, session_dict) = get_settings()
driver = get_driver()
type(driver)
driver.get('http://roswar.ru')
login()
metro_timeout = time.time()
pet_timeout = time.time()
time.sleep(5)
main_function()


