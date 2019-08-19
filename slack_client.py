import time
import re
import sys
from slackclient import SlackClient
import music_player2
import global_vars


import logging
logging.basicConfig()

SLACK_BOT_TOKEN=global_vars.SLACK_BOT_TOKEN
# bot channel
SLACK_DEFAULT_CHANNEL=global_vars.SLACK_DEFAULT_CHANNEL
# instantiate Slack client
slack_client = SlackClient(SLACK_BOT_TOKEN)
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
                return message, event["channel"], global_vars.SLACK_USER_MAP[event["user"]]
    return None, None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel, creator, pl, current_song):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format("play a song")

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!

    if command.startswith("request"):

        print(command)
        search_keywords = command[8:]
        print(search_keywords)

        # if current_song.is_playing() and current_song.get_creator() != "auto":
        if current_song.is_playing():
            # if there is a song playing wait till it's finish
            song_data = pl.add_song(search_keywords, creator)
            response = "Ok I have added {} to queue".format(song_data['name'])
        else:
            # else play that song.
            current_song.stop_audio()
            pl.add_song(search_keywords, creator)
            song_data = pl.get_song()
            current_song = music_player2.YoutubeAudio(song_data)
            current_song.play_audio()
            song_name = filter_title(song_data['name'])
            response = "*Now playing:* {0} \n*Picked by:* {1}".format(song_name, current_song.get_creator())

        print("current play list",pl.get_playlist)


    elif command.startswith("nowplaying"):
        response = "currently playing: {0}".format(current_song.get_name())

    elif command.startswith("skip"):
        current_song.stop_audio()
        song_data = pl.get_song()
        current_song = music_player2.YoutubeAudio(song_data)
        current_song.play_audio()
        song_name = filter_title(current_song.get_name())
        response = "*Now playing:* {0} \n*Picked by:* {1}".format(song_name, current_song.get_creator())

    elif command.startswith("nextup"):
        song_list = pl.get_next_info(limit=5)
        s_list = ""
        for s in song_list:
            s_list = s_list + "{}\n".format(s['name']+"\n")
        response = "Coming up: \n" + s_list

    elif command.startswith("help"):
        response = "You can ask me the following: \n" \
                   "request - request a song \n" \
                   "skip - skip to the next track \n" \
                   "nowplaying - report back what is currently playing \n" \
                   "nextup - report back what is coming up \n" \
                   "stop - close the app \n"

    elif command.startswith("stop"):
        response = "stop music"
        sys.exit()


    # Sends the response back to the channel
    print("internal channel", channel)
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response
    )
    return current_song, channel


def filter_title(song_n):
    # remove 1080p, video from song name
    song_name = song_n.lower()
    song_name = song_name.replace("video", '')
    song_name = song_name.replace("music", '')
    song_name = song_name.replace("official", '')
    song_name = song_name.replace("1080p", '')
    song_name = song_name.replace("lyrics", '')
    song_name = song_name.replace("(", '')
    song_name = song_name.replace(")", '')
    song_name = song_name.replace("]", '')
    song_name = song_name.replace("[", '')
    song_name = song_name.replace(",", '')
    re.sub(r'\s+', ' ', song_name)
    print("filter", song_name)
    return song_name

if __name__ == "__main__":

    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        # play the first auto song right away.
        pl = music_player2.Playlist()
        song_data = pl.get_song()
        # set default channel to SLACK_DEFAULT_CHANNEL
        channel = SLACK_DEFAULT_CHANNEL
        print(song_data['name'])
        current_song = music_player2.YoutubeAudio(song_data)
        current_song.play_audio()
        song_name = filter_title(current_song.get_name())
        response = "*Now playing:* {0} \n*Picked by:* {1}".format(song_name, "DJ Robot")
        slack_client.api_call("chat.postMessage", channel=channel, text=response)

        while True:
            command, channel, creator = parse_bot_commands(slack_client.rtm_read())

            if command:
                current_song, this_channel = handle_command(command, channel,creator, pl, current_song)

            if not channel:
                this_channel = SLACK_DEFAULT_CHANNEL

            # when no song is playing play auto song after 3 seconds
            if not current_song.is_playing():
                time.sleep(3)
                if not current_song.is_playing():
                    print("here")
                    current_song.stop_audio()
                    song_data = pl.get_song()
                    print(song_data['name'])
                    current_song = music_player2.YoutubeAudio(song_data)
                    current_song.play_audio()
                    song_name = filter_title(current_song.get_name())
                    response = "*Now playing:* {0} \n*Picked by:* {1}".format(song_name, current_song.get_creator())
                    print("channel: ", this_channel)
                    slack_client.api_call("chat.postMessage", channel=this_channel, text=response)

            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")


# *** created using https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
# TODO recovery from failure on play. bundle all play into a function with try catch and restart?
# TODO maybe if song length is longer than 8 min skip it
