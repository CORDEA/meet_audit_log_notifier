# Meet Audit Log Notifier

Notify audit log to Slack.

## Usage

- Deploy

```
$ gcloud app deploy
```

- Register your callback URL

```
$ python main.py register
```

- Unregister

```
$ python main.py unregister --id $ID --resource-id $RESOURCE_ID
```
