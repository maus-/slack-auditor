# Slack API Auditor

Provides a quick method of collecting Slack access logs and integration logs, then forwards them via Logstash.


### How this works
The auditor is a Python script being executed by Logstash on a set interval. The script will reach out to the Slack API and gather [team.accessLogs](https://api.slack.com/methods/team.accessLogs) and [team.integrationLogs](https://api.slack.com/methods/team.integrationLogs) and output them to stdout, which Logstash collects. Logstash then tags with a proper timestamp and forwards to the service of your [choosing](https://www.elastic.co/guide/en/logstash/current/output-plugins.html). 

### How to Deploy
There's a multitude of ways to implement this but here's a quick walkthrough of getting started:

1. Clone this repo and install the required dependencies, `pip install -r scripts/requirements.txt`

2. Create OAuth Token For Slack
Follow the directions here [Creating oAuth Tokens for Slack Apps](https://api.slack.com/tutorials/slack-apps-and-postman), and generate a token with the "admin" scope.

3. [Install Logstash](https://www.elastic.co/guide/en/logstash/2.4/installing-logstash.html) (We tested/built on 2.4 but it should work on later versions, if you see an issue send a pr)

4. Adjust Logstash config to point to Elasticsearch / splunk as an output instead of rubydebug. Although you might want to leave it there while you test.

5. Set the following enviornment variables `SLACK_TOKEN` with your Slack token and your `SLACK_AUDIT_PATH` with the absolute path poiting to the audit script in the scripts directory you cloned.

6. Run Logstash. 

7. Profit.


### Caveats

I've only tested this on teams that are using the paid-for Slack. I don't know if these methods are available to the free api.

The Slack team.accesslog and team.integraiton log methods actually limit the results to a maximum value page of 100. So with 1000 events per page you can only grab the last 100,000 events. However you could work around this by grabbing the date of the last entry on the 100th page and pass that on to the before parameter and repeat the process. Really only usefull for backfilling events or if you have a tremendously high volume of events happening on 30 minute intervals. 
