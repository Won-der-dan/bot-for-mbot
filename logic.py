import time
import json
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait

def get_settings():
    with open('settings.json', 'r') as f:
        settings_dict = json.load(f)
        return settings_dict

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
    driver = webdriver.Firefox()  #python
    url = driver.command_executor._url       #"http://127.0.0.1:60622/hub"
    session_id = driver.session_id            #'4e167f26-dc1d-4f51-a207-f761eaf73c31'
    print(session_id)
    print(url)
    driver.get("http://roswar.ru")
    driver = create_driver_session(session_id, url)
    # driver.close()   # this prevents the dummy browser
    # driver.session_id = session_id
    return driver

def login():
    print('logging in')
    email_input = driver.find_element_by_id("email-input")
    password_input = driver.find_element_by_id("pwd-input")
    submit_button = driver.find_element_by_css_selector(".td-login")
    email_input.send_keys(settings_dict['email'])
    password_input.send_keys(settings_dict['password'])
    submit_button.click()

def go_to_alley():
    print('going to alley')
    find_and_click_iframe_elem("a.alley")

def fight(fight_type):
    print ("going to fighting")
    go_to_alley()
    find_and_click_iframe_elem("div."+fight_type)
    find_and_click_iframe_elem("div.button-fight")
    find_and_click_iframe_elem("i.icon-forward")
    go_to_alley()
    

def find_and_click_iframe_elem(selector):
    wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it("game-frame"))
    alley_button = driver.find_element_by_css_selector(selector)
    alley_button.click()    
    driver.switch_to.default_content()

driver = get_driver()
type(driver)
driver.get('http://roswar.ru')
settings_dict = get_settings()
login()
time.sleep(5)
go_to_alley()
fight('f1')


