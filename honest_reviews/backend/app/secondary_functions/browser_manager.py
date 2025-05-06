from typing import Optional
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from loguru import logger
import zipfile
import tempfile


class BrowserManager:
    def __init__(self, config):
        self.config = config
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]

    def init_driver(self, proxy: Optional[str] = None) -> Optional[webdriver.Chrome]:
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(f"user-agent={random.choice(self.user_agents)}")

        if proxy:
            proxy_parts = proxy.split(":")
            if len(proxy_parts) == 2:
                options.add_argument(f"--proxy-server=http://{proxy}")
            elif len(proxy_parts) == 4:
                proxy_auth = self._create_proxy_auth_extension(*proxy_parts)
                options.add_extension(proxy_auth)
            else:
                logger.error(f"Неверный формат прокси: {proxy}")
                return None

        try:
            service = Service(executable_path=self.config.chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
            self._hide_automation(driver)
            return driver
        except Exception as e:
            logger.error(f"Ошибка при инициализации драйвера: {e}")
            return None

    def _create_proxy_auth_extension(self, proxy_host: str, proxy_port: str,
                                     proxy_user: str, proxy_pass: str) -> str:
        """Создание расширения для аутентификации прокси"""
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

        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt({proxy_port})
                }},
                bypassList: ["localhost"]
            }}
        }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_user}",
                    password: "{proxy_pass}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """

        # Создание временного файла для расширения
        pluginfile = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        with zipfile.ZipFile(pluginfile.name, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return pluginfile.name

    def _hide_automation(self, driver: webdriver.Chrome):
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
