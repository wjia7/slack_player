import time
import re
import sys
import music_player2
import global_vars
import slack
# from slackclient import SlackClient


import logging
logging.basicConfig()

SLACK_BOT_TOKEN=global_vars.SLACK_BOT_TOKEN
# bot channel
SLACK_DEFAULT_CHANNEL=global_vars.SLACK_DEFAULT_CHANNEL
# instantiate Slack client
slack_client = slack.WebClient(SLACK_BOT_TOKEN)
rtmclient = slack.RTMClient(token=SLACK_BOT_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


@slack.RTMClient.run_on(event='message')
def say_message(**payload):
    print("what is here",payload)
    data = payload['data']
    command = data['text']

    global CURRENT_SONG

    if command.startswith("request"):

        print(command)
        search_keywords = command[8:]
        print(search_keywords)

        user = data['user']
        # if current_song.is_playing() and current_song.get_creator() != "auto":
        if CURRENT_SONG.is_playing():
            # if there is a song playing wait till it's finish
            song_data = pl.add_song(search_keywords)
            response = "Ok I have added {} to queue".format(song_data['name'])
        else:
            # else play that song.
            CURRENT_SONG.stop_audio()
            pl.add_song(search_keywords)
            song_data = pl.get_song()
            print(song_data)
            CURRENT_SONG = music_player2.YoutubeAudio(song_data)
            CURRENT_SONG.play_audio()
            response = "Now playing {}".format(song_data['name'])

        print("current play list",pl.get_playlist)
        webclient = payload['web_client']
        webclient.chat_postMessage(channel=SLACK_DEFAULT_CHANNEL, text=response)

    if command.startswith("nowplaying"):
        response = "currently playing: {0}".format(CURRENT_SONG.get_name())
        webclient = payload['web_client']
        webclient.chat_postMessage(channel=SLACK_DEFAULT_CHANNEL, text=response)

    if command.startswith("skip"):
        CURRENT_SONG.stop_audio()
        song_data = pl.get_song()
        print(song_data['name'])
        current_song = music_player2.YoutubeAudio(song_data)
        current_song.play_audio()
        response = "Now playing: {0}".format(current_song.get_name())
        webclient = payload['web_client']
        webclient.chat_postMessage(channel=SLACK_DEFAULT_CHANNEL, text=response)

    if command.startswith("nextup"):
        song_list = pl.get_next_info(limit=5)
        s_list = ""
        for s in song_list:
            s_list = s_list + "{}\n".format(s['name']+"\n")
        response = "Coming up: \n" + s_list
        webclient = payload['web_client']
        webclient.chat_postMessage(channel=SLACK_DEFAULT_CHANNEL, text=response)

    if command.startswith("help"):
        response = "You can ask me the following: \n" \
                   "request - request a song \n" \
                   "skip - skip to the next track \n" \
                   "nowplaying - report back what is currently playing \n" \
                   "nextup - report back what is coming up \n" \
                   "stop - close the app \n"
        webclient = payload['web_client']
        webclient.chat_postMessage(channel=SLACK_DEFAULT_CHANNEL, text=response)

    if command.startswith("stop"):
        response = "stop music"
        webclient = payload['web_client']
        webclient.chat_postMessage(channel=SLACK_DEFAULT_CHANNEL, text=response)
        sys.exit()


# start the song
pl = music_player2.Playlist()
song_data = pl.get_song()
print(song_data['name'])
CURRENT_SONG = music_player2.YoutubeAudio(song_data)
# play the first auto song right away.
CURRENT_SONG.play_audio()
response = "Now playing: {0}".format(CURRENT_SONG.get_name())
slack_client.chat_postMessage(channel=SLACK_DEFAULT_CHANNEL, text=response)

# start the interaction
rtmclient.start()

# #TODO find a way to check when the song is finished and start playing a new song. Below doesn't work
# while True:
#     print("song status: ",CURRENT_SONG.is_playing())
#     if not CURRENT_SONG.is_playing():
#         time.sleep(3)
#         CURRENT_SONG.stop_audio()
#         song_data = pl.get_song()
#         print(song_data['name'])
#         current_song = music_player2.YoutubeAudio(song_data)
#         current_song.play_audio()
#         response = "Now playing: {0}".format(current_song.get_name())
#         print("channel: ", SLACK_DEFAULT_CHANNEL)
#         slack_client.chat_postMessage(channel=SLACK_DEFAULT_CHANNEL, text=response)



#TODO need a way to pass the state of the song across state of slack client