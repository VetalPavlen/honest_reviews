# browser_manager.py
import random
import zipfile
import os
from typing import Optional, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from loguru import logger
import undetected_chromedriver as uc  # Добавляем undetected-chromedriver


class BrowserManager:
    def __init__(self, config):
        self.config = config
        self.user_agents = self._load_user_agents()
        self.proxy_auth_plugins = {}

    def _load_user_agents(self) -> List[str]:
        """Загрузка актуальных User-Agent'ов из файла или базового набора"""
        try:
            with open('user_agents.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]

    def init_driver(self, proxy: Optional[str] = None) -> Optional[webdriver.Chrome]:
        """Инициализация драйвера с улучшенной защитой от детекта"""
        try:
            options = self._prepare_options(proxy)

            # Используем undetected_chromedriver если обычный не работает
            try:
                service = Service(executable_path=self.config.chromedriver_path)
                driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                logger.warning(f"Обычный драйвер не работает, пробуем undetected: {e}")
                driver = uc.Chrome(options=options)

            self._apply_stealth_settings(driver)
            return driver
        except Exception as e:
            logger.error(f"Критическая ошибка инициализации драйвера: {e}")
            return None

    def _prepare_options(self, proxy: Optional[str]) -> Options:
        """Подготовка настроек браузера"""
        options = Options()

        # Базовые настройки
        options.add_argument(f"user-agent={random.choice(self.user_agents)}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # Настройки для обхода детекта
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Настройки прокси
        if proxy:
            self._configure_proxy(options, proxy)

        return options

    def _configure_proxy(self, options: Options, proxy: str):
        """Конфигурация прокси с проверкой формата"""
        try:
            proxy_host, proxy_port = proxy.split(":")
            if hasattr(self.config, 'proxy_username') and hasattr(self.config, 'proxy_password'):
                proxy_auth = self._get_proxy_auth_extension(
                    proxy_host=proxy_host,
                    proxy_port=proxy_port,
                    proxy_user=self.config.proxy_username,
                    proxy_pass=self.config.proxy_password
                )
                options.add_extension(proxy_auth)
            else:
                options.add_argument(f"--proxy-server={proxy}")
        except ValueError:
            logger.error(f"Неверный формат прокси: {proxy}. Ожидается host:port")
            raise

    def _get_proxy_auth_extension(self, proxy_host: str, proxy_port: str,
                                  proxy_user: str, proxy_pass: str) -> str:
        """Создание/получение кэшированного плагина для аутентификации прокси"""
        cache_key = f"{proxy_host}:{proxy_port}:{proxy_user}"

        if cache_key not in self.proxy_auth_plugins:
            plugin_path = self._create_proxy_auth_extension(
                proxy_host, proxy_port, proxy_user, proxy_pass
            )
            self.proxy_auth_plugins[cache_key] = plugin_path

        return self.proxy_auth_plugins[cache_key]

    def _create_proxy_auth_extension(self, proxy_host: str, proxy_port: str,
                                     proxy_user: str, proxy_pass: str) -> str:
        """Создание расширения для аутентификации прокси"""
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 3,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "webRequest",
                "webRequestAuthProvider"
            ],
            "background": {
                "service_worker": "background.js"
            }
        }
        """

        background_js = """
        const config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
            }
        };

        chrome.proxy.settings.set({value: config, scope: 'regular'}, () => {});

        chrome.webRequest.onAuthRequired.addListener(
            function(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            },
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """ % (proxy_host, proxy_port, proxy_user, proxy_pass)

        proxy_auth_plugin = f'proxy_auth_{proxy_host}_{proxy_port}.zip'
        with zipfile.ZipFile(proxy_auth_plugin, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return os.path.abspath(proxy_auth_plugin)

    def _apply_stealth_settings(self, driver: webdriver.Chrome):
        """Применение настроек для скрытия автоматизации"""
        stealth_script = """
        // Скрытие WebDriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // Изменение свойств платформы
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });

        // Запрет обнаружения Chrome
        window.chrome = {
            app: {
                isInstalled: false,
            },
            webstore: {
                onInstallStageChanged: {},
                onDownloadProgress: {},
            },
            runtime: {
                PlatformOs: {
                    MAC: 'mac',
                    WIN: 'win',
                    ANDROID: 'android',
                    CROS: 'cros',
                    LINUX: 'linux',
                    OPENBSD: 'openbsd',
                },
                PlatformArch: {
                    ARM: 'arm',
                    X86_32: 'x86-32',
                    X86_64: 'x86-64',
                },
                PlatformNaclArch: {
                    ARM: 'arm',
                    X86_32: 'x86-32',
                    X86_64: 'x86-64',
                },
                RequestUpdateCheckStatus: {
                    THROTTLED: 'throttled',
                    NO_UPDATE: 'no_update',
                    UPDATE_AVAILABLE: 'update_available',
                },
                OnInstalledReason: {
                    INSTALL: 'install',
                    UPDATE: 'update',
                    CHROME_UPDATE: 'chrome_update',
                    SHARED_MODULE_UPDATE: 'shared_module_update',
                },
                OnRestartRequiredReason: {
                    APP_UPDATE: 'app_update',
                    OS_UPDATE: 'os_update',
                    PERIODIC: 'periodic',
                },
            },
        };
        """
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": stealth_script
        })