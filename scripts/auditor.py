from datetime import datetime
from dateutil.parser import *
import slack
import dateutil
import tzlocal
import os
import sys
import time
import json

class SlackAuditor(object):
    """
        SlackAuditor:
        This lib provides a set of abstractions to gather access logs and integration logs for a Slack Team.
        You could use a logstash config such as the one we provide in this project to send these events to ELK
        or Splunk or whatever. You need to have the enviornment variable SLACK_TOKEN set to your api token.
    """
    def __init__(self):
        """
            In order to create a proper token with required scope follow the guide here:
            https://api.slack.com/tutorials/slack-apps-and-postman you'll need the 'admin' scope
        """
        with open(getenv(
                 'AUDIT_CONFIG_PATH',
                 '/usr/share/logstash/scripts/config/config.json')) as config_data:
            self.config = json.load(config_data)
        self.integration_sincedb_path = '{}/integration_sincedb'.format(self.config['sincedb_path'])
        self.access_sincedb_path = '{}/access_sincedb'.format(self.config['sincedb_path'])
        self.sc = SlackClient(self.config['slack_token'])
        self.integration_sincedb = self._check_sincedb(self.integration_sincedb_path)
        self.access_sincedb = self._check_sincedb(self.access_sincedb_path)

    def _check_sincedb(self, sincedb_path):
        """
            SinceDB is a logstash concept but we're just putting something primitive in here.
        """
        if os.path.isfile(sincedb_path):
            sincedb = float(open(sincedb_path, 'r').read())
            return datetime.utcfromtimestamp(sincedb)
        else:
            self._write_sincedb(sincedb_path)
            sincedb = float(open(sincedb_path, 'r').read())
            return datetime.utcfromtimestamp(sincedb)

    def _write_sincedb(self, sincedb_path):
            sincedb = open(sincedb_path, 'w')
            sincedb.write(str(time.mktime(datetime.now().timetuple())))

    def _unix_to_pretty_utc(self, date):
        """
            Convert the Unix Timestamps to UTC / Pretty Format
        """

        utc_time = datetime.utcfromtimestamp(date)
        return utc_time.strftime("%Y-%m-%d %H:%M:%S")

    def _check_max(self, pages):
       """
           The Slack access logs api has a max page limit of 100 pages, despite taunting you with
           more logs / events.
       """
       if pages > 100:
           return 100
       return pages

    def get_access_logs(self):
       """
           This function will return all slack access logs formatted in a list of hashes.
       """
       results = []
       page = 1
       logs = self.sc.api_call("team.accessLogs", )
       results.extend(logs['logins'])
       max_pages = self._check_max(logs['paging']['pages'])
       while page < max_pages:
           page += 1
           logs = self.sc.api_call("team.accessLogs", json={'count':'1000', 'page':page})
           results.extend(logs['logins'])
       return results

    def get_integration_logs(self):
       """
           This function will return all Slack integration logs formatted as a list of hashes.
       """
       results = []
       page = 1
       logs = self.sc.api_call("team.integrationLogs", json={'count':'1000'})
       results.extend(logs['logs'])
       max_pages = self._check_max(logs['paging']['pages'])
       while page < max_pages:
           page += 1
           logs = self.sc.api_call("team.integrationLogs",json={'count':'1000', 'page':page})
           results.extend(logs['logs'])
       return results

    def get_latest_login_events(self):
        """
            This gets all the login events and compares the datetime to what we have already indexed.
            Anything thats newer than the last timestamp stored in the /tmp/sincedb_login will be sorted
            and returned
        """
        logs = self.get_access_logs()
        results = []
        for log in logs:
            if datetime.utcfromtimestamp(log['date_first']) > self.access_sincedb:
                log['date_first'] = self._unix_to_pretty_utc(log['date_first'])
                log['date_last'] = self._unix_to_pretty_utc(log['date_last'])
                results.append(log)
        results.sort(key=lambda item:item['date_first'], reverse=False)
        self._write_sincedb(self.access_sincedb_path)
        return results

    def get_latest_integration_events(self):
        logs = self.get_integration_logs()
        results = []
        for log in logs:
            if datetime.utcfromtimestamp(float(log['date'])) > self.integration_sincedb:
                log['date'] = self._unix_to_pretty_utc(float(log['date']))
                results.append(log)
        results.sort(key=lambda item:item['date'], reverse=False)
        self._write_sincedb(self.integration_sincedb_path)
        return results

if __name__ == "__main__":
    audit = SlackAuditor()

    if sys.argv[1] == 'login':
      print(json.dumps(audit.get_latest_login_events()))

    if sys.argv[1] == 'integration':
      print(json.dumps(audit.get_latest_integration_events()))
