import json

from connection import *
from scraping import Lernsax


# Database ID of your Notion database
databaseID = ""

if __name__ == '__main__':
    print('[INFO] Start scraping from Lernsax')
    tasks = Lernsax().scrape()
    if tasks:
        c = Connection()
        for task in tasks:
            # ------ Cheacking if task has the needed params ------
            try:
                task['Fach']
            except KeyError:
                task.update({'Fach': task['Zugewiesen von']})

            try:
                task['Fällig']
            except KeyError:
                # If not: Random date
                task.update({'Fällig': '2050-05-28T13:15:00Z'})

            try:
                task['text']
            except KeyError:
                task.update({'text': ' '})

            # Data for the request to the Notion API
            data = {
                "parent": {"database_id": databaseID},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": task["Titel"]
                                }
                            }
                        ]
                    },
                    # Here your columns of your database: "$name": { "$type": { "name (start if date)": "asdf123" } }
                    "Fach": {
                        "select": {
                            "name": task['Fach']
                        }
                    },
                    "Fällig": {
                        "date": {
                            "start": task['Fällig']
                        }
                    },
                    "Status": {
                        "select": {
                            "name": "in progress"
                        }
                    },
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": task['text']
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            # Send Request
            print('[INFO] Sync new tasks...')
            c.insert(json.dumps(dict(data), indent=4))

    else:
        print('[RESULT] No new tasks to sync...')
