#Slack API Audit

I love using Slack, however I don't love that I cant easily grab all access & integration logs for a particular team and store them easily. This project enables you to do just that.


### How this works
The way this works is a Python script being executed via Logstash on a set interval. The script will reach out to the Slack API and gather [team.accessLogs](https://api.slack.com/methods/team.accessLogs) and [team.integrationLogs](https://api.slack.com/methods/team.integrationLogs) and output them to stdout which logstash collects, tags with a proper timestamp and forwards to the service of your choosing. Typically Splunk or ElasticSearch.

### How to Deploy
There's a multitude of ways to implment this but a quick walkthrough of getting started.

1. Clone this repo and install the required dependencies, `pip install -r scripts/requirements.txt`

2. Collect OAuth Token For Slack
Visit [Creating oAuth Tokens for Slack Apps](https://api.slack.com/tutorials/slack-apps-and-postman), and generate a token with the "admin" scope.

3. [Install logstash](https://www.elastic.co/guide/en/logstash/2.4/installing-logstash.html) (We tested/built on 2.4 but it should work on later versions)

4. Adjust logstash config to point to elasticsearch / splunk as an output instead of rubydebug. Although you might want to leave it there while you test.

5. Set the following enviornment variables `SLACK_TOKEN` with your slack token and your `SLACK_AUDIT_PATH` with the absolute path poiting to the audit script in the scripts directory you cloned.

6. Run Logstash. Profit.


### Caveats

I've only tested this on teams that are using the paid for slack. I don't know if these methods are available to the free api.

As of writing this team.accessLogs and team.integrationLogs don't allow a "since" parameter only a "before", as such you end up making a lot more requests to the slack api than you need to.

The slack team.accesslog and team.integraiton log methods actually only limit your results to the last 100 pages regardless if you're a paid for slack account or if there is any more pages. You might be able to hack around this if you pass the before parameter to the api after you've reached 100 pages of results and repeat the request but at that point you're basically engineering around a half thought out api method, I'd rather slack just fix this.
