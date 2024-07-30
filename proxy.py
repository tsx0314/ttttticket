import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import zipfile
import os

def proxy_chrome(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%(host)s",
            port: parseInt(%(port)d)
          },
          bypassList: ["foobar.com"]
        }
      };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%(user)s",
                password: "%(pass)s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
    );
    """ % {
        "host": PROXY_HOST,
        "port": PROXY_PORT,
        "user": PROXY_USER,
        "pass": PROXY_PASS,
    }

    # Ensure the extension directory exists
    extension_dir = 'extension'
    if not os.path.exists(extension_dir):
        os.makedirs(extension_dir)

    pluginfile = os.path.join(extension_dir, 'proxy_auth_plugin.zip')

    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    co = Options()
    co.add_argument('--disable-gpu')
    co.add_argument('--disable-infobars')
    co.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    co.add_extension(pluginfile)

    # Initialize the undetected ChromeDriver
    options = uc.ChromeOptions()
    driverPath = './chromedriver.exe'
    driver = uc.Chrome(options=options,driver_executable_path=driverPath)

    return driver