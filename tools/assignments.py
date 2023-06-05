import configparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Any


class Assignment:
    def __init__(self, portal_id: str, portal_pw: str, config_path='../resources/config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.user_id = portal_id
        self.user_pw = portal_pw
        self.login_url = config['PORTAL']['LOGIN_URL']
        self.assignment_url = config['PORTAL']['ASSIGNMENT_URL']

    def run(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> str:
        data = {
            'user_id': self.user_id,
            'user_password': self.user_pw,
            'id': 'EL2',
            'RelayState': '/local/sso/index.php',
            'anchor': ''
        }

        login_url = self.login_url
        try:
            with requests.Session() as s:
                s.post(login_url, data=data, verify=False)
                response = s.get(self.assignment_url)
                response.raise_for_status()
        except Exception:
            return ''

        soup = BeautifulSoup(response.content, 'html.parser')

        tasks = []

        for card in soup.find('div', 'cont').find_all('div', 'activity-card'):
            head = card.find('div', 'head').find('div')
            body = card.find('div', 'p-2').find_all('div')
            foot = card.find('div', 'foot')

            schedule = foot.text[5:]
            start, end = None, None
            if schedule != '':
                try:
                    start, end = (datetime.strptime(s.strip(), '%Y-%m-%d') for s in schedule.split('~'))
                except Exception:
                    pass

            task = {
                'type': head.text,
                'subject_name': body[0].text[6:],
                'name': body[1].text,
                'schedule': {
                    'start': start,
                    'end': end
                }
            }
            tasks.append(task)

        curr = datetime.now()
        assignments = []
        for task in tasks:
            if task['schedule']['start'] is not None:
                start, end = task['schedule']['start'], task['schedule']['end']
                if curr >= start and curr < end:
                    assignments.append(task)

        assignments = sorted(assignments, key=lambda x: x['schedule']['end'])

        for i in range(len(assignments)):
            assignments[i]['schedule']['start'] = str(assignments[i]['schedule']['start'])
            assignments[i]['schedule']['end'] = str(assignments[i]['schedule']['end'])

        return ','.join([str(assignment) for assignment in assignments])


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../resources/config.ini')
    assignment = Assignment(
        portal_id=config['PORTAL']['ID'],
        portal_pw=config['PORTAL']['PW']
    )

    print(assignment.run())
