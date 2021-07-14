from selenium import webdriver
import chromedriver_autoinstaller

def selenium_setting(url="https://www.google.com"):
    chromedriver_autoinstaller.install()
    driver_options = webdriver.ChromeOptions()
    driver_options.headless = True
    driver_options.add_argument('--disable-gpu')
    driver_options.add_argument("--mute-audio")
    driver_options.add_argument('--log-level=3')
    driver_options.add_argument('--start-maximized')
    driver_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    # driver_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=driver_options)
    driver.get(url)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    driver.execute_script(
        "const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
    return driver