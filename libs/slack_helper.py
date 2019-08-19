import time
import re
import sys
from slackclient import SlackClient



slack_template = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "This is a section block with a button."
        }
    },
    {
        "type": "actions",
        "block_id": "actionblock789",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Yeah"
                },
                "url": "https://api.slack.com/block-kit"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Nah"
                },
                "url": "https://api.slack.com/block-kit"
            }
        ]
    }
]

def current_playing_format():
    # slack response format for nowplaying
    print("test")
