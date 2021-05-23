import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

EMAIL = ""
PASSWORD = ""
# -> https://chromedriver.chromium.org/downloads
URL_Chromedriver = ""

class Lernsax:
    def __init__(self):
        self.blacklist = ['LernSax - Aufgabe lesen', "<!--\nvar refresh_url='", 'wws', "130837.php?sid=54297534803754603562168726872412856153254109Sd57f2288';\nvar auto_refresh=0;", '-->', '<!--\nww.focus();\n', '-->', '\xa0', 'Aufgabe lesen', 'www.lernsax.de']
        self.params = ["Titel", "Zugewiesen von", "Fällig"]

        # teacher -> subject
        self.faecher = {
            'H. Fleischer': "Info",
            'kohlhoff.heiner' : "PHY",
            'Evelyn Zinner' : "GEO",
            'Claudia Kämke' : "MA",
            'roeber.max' : "MU",
            'Regine Richter' : "FRZ",
            'Felix Kollender' : "GRW",
            'thieme.heike' : "EN",
            'Matthias Dirks' : "CHE",
            'Irene Ullrich' : "BIO",
            'Alex Hanicke' : "ETH",
            'steinert.kerstin' : "DE",
            'lange.maja' : "KU",
            'R. Hengst' : "INFO",
            'bergmann.anne' : "RELI",
            "frenzel.uwe" : "SPORT",
            'Dirk Köhler' : "INFO"
        }

        try:
            self.fileForSync = open('sync.txt', 'r+')
        except:
            open('sync.txt', 'w').close()
            self.fileForSync = open('sync.txt', 'r+')

        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(executable_path=URL_Chromedriver, options=options)

    def scrape(self):
        # ----- Open browser and navigate to "Aufgaben" -----
        print('[INFO] Starting Selenuim')
        self.driver.get('https://www.lernsax.de/wws/9.php#/wws/100001.php')
        self.login()
        link = self.driver.find_element_by_link_text('Aufgaben')
        link.click()

        # ----- Get Tasks -----
        html = bs4.BeautifulSoup(self.driver.page_source, features="html.parser")
        links = html.find_all(self.hasAttrs)
        links_a = [l.get('data-popup') for l in links]

        # ----- Open each task and fork informations -----
        print('[INFO] Start forking each task')
        tasks = []
        for link in links_a:
            self.driver.get(f'https://www.lernsax.de/wws/{link}&enableautogrow=1')
            try:
                # If: h2 -> Error Page
                self.driver.find_element_by_tag_name('h2')
            except:
                # Fork plain text and structure it
                content = bs4.BeautifulSoup(self.driver.page_source, features="html.parser")
                text = "/".join(content.findAll(text=True))
                single_items = list(text.split('/'))
                items = []
                for k, i in enumerate(single_items):
                    if i in self.blacklist:
                        continue
                    if ".php" in str(i) or "<!--" in str(i) or i == '':
                        continue
                    items.append(i)

                # ----- Create task with known parameters -----
                task = {}
                for p in self.params:
                    try:
                        if p == "Fällig":
                            # Notion needs the time in a special format: YYYY-MM-DD + '-T' + HH:MM:SS + 'Z'
                            idx = items.index(p)
                            date = items[idx + 1]
                            try:
                                date, time = date.split(' ')
                            except:
                                time = "00:00"
                            day, month, year = date.split('.')
                            task.update({p: f"{year}-{month}-{day}T{time}:00Z"})

                            # After "Erledigt" comes the description for the task
                            idx = items.index("Erledigt")
                            task.update({'text': ' \n '.join(items[(idx+2):])})
                        else:
                            idx = items.index(p)
                            task.update({p: items[idx+1]})

                    except:
                        pass

                # ----- Change name of the teacher to subject's name -----
                for teacher in self.faecher.keys():
                    try:
                        if task['Zugewiesen von'] == teacher:
                            task.update({'Fach': self.faecher[teacher]})
                            task.pop("Zugewiesen von")
                    except:
                        pass

                # ----- Search in list of already synced tasks -----
                inList = False
                for line in self.fileForSync.readlines():
                    if task['Titel'] in line:
                        inList = True

                if inList:
                    if task['Titel'] != 'Biologie_05 Gruppe 1':
                        tasks.append(task)

                    # ----- Write to synced tasks -----
                    try:
                        self.fileForSync.write(f"Titel: {task['Titel']} <Bis:{task['Fällig']}> \n")
                    except KeyError:
                        self.fileForSync.write(f"Titel: {task['Titel']} <Bis: XX> \n")

        self.fileForSync.close()
        return tasks


    def login(self):
        print('[INFO] Logging in...')
        frame = self.driver.find_element_by_id('main_frame')
        self.driver.switch_to.frame(frame)
        email = self.driver.find_element_by_id('login_login')
        email.clear()
        email.send_keys(EMAIL)
        password = self.driver.find_element_by_name('login_password')
        password.clear()
        password.send_keys(PASSWORD)
        password.send_keys(Keys.ENTER)


    def hasAttrs(self, tag):
        """
        :param tag:
        :return: bool
        returns if tag has "data-popup" in it and href with href=#
        """
        return tag.has_attr('data-popup') and tag.has_attr('href') and tag.get('href') == '#'

