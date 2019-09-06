import vlc
import time
import subprocess
import song_generator
import youtube_api
import youtube_dl

class YoutubeAudio:

    def __init__(self, keywords={'url': 'https://r3---sn-gvbxgn-tvfl.googlevideo.com/videoplayback?mm=31%2C29&mn=sn-gvbxgn-tvfl%2Csn-gvbxgn-tt1ee&id=o-AM-HnzfJmQOZ0O4T8JF4ED4xi3xw3E__-hul9wg3MrVY&ip=72.142.116.74&lmt=1547672095544426&dur=270.621&pl=20&mt=1553188146&source=youtube&mv=m&ei=3cWTXMKePJrtigSL-Z7oBw&keepalive=yes&ms=au%2Crdu&txp=5511222&sparams=clen%2Cdur%2Cei%2Cgir%2Cid%2Cinitcwndbps%2Cip%2Cipbits%2Citag%2Ckeepalive%2Clmt%2Cmime%2Cmm%2Cmn%2Cms%2Cmv%2Cpcm2cms%2Cpl%2Crequiressl%2Csource%2Cexpire&expire=1553209918&pcm2cms=yes&key=yt6&gir=yes&c=WEB&ipbits=0&initcwndbps=1930000&mime=audio%2Fwebm&itag=251&fvip=3&clen=4466844&requiressl=yes&signature=6EF4DE0B8540AAB24D49A5C2B28944C5AB7B73EE.2225A4AF696521DC1015D4E1D04C1B27BEB1E129&ratebypass=yes', 'name': 'gimme shelter', 'creator': 'DJ Robot'}):
        self.keywords = keywords
        self.player = None
        self.Media = None

        # vlc player control
        self.url = self.keywords['url']
        self.name = self.keywords['name']
        self.time = self.keywords['time']
        self.creator = self.keywords['creator']
        self.player = vlc.MediaPlayer(self.url)
        self.volume = 50


    def get_url(self):
        return self.keywords['url']

    def get_time(self):
        # duration = self.player.get_length() / 1000
        print("audio time: {0}".format(self.keywords['time']))

    def get_name(self):
        return self.keywords['name']

    def get_creator(self):
        return self.keywords['creator']

    def play_audio(self):
        print(self.keywords['url'])
        self.player.play()
        self.player.audio_set_volume(self.volume)

    def pause_audio(self):
        self.player.pause()

    def stop_audio(self):
        self.player.stop()

    def get_volume(self):
        return self.volume

    def set_volume(self, number):
        self.volume = number
        if 100 >= number >= 0:
            self.player.audio_set_volume(self.volume)
        else:
            return -1

    def is_playing(self):
        return self.player.is_playing()


class Playlist:

    def __init__(self):

        #replicate a simple queue two list
        # a list store songs to be played. where user's songs stored
        self.songlist = []
        self.playedlist = []

        # add a automatically generated song
        self.add_new_auto_song()

    def words_to_audio_data(self, keywords):

        print("keywords", keywords)
        # ytsearch = "ytsearch:'{0}'".format(keywords)
        # # execute youtube data retrieve cli this process takes 2-3 seconds
        # try:
        #     out = subprocess.check_output(["youtube-dl", "-4", "-g", "-e", "--get-duration","--get-id", ytsearch])
        # except subprocess.CalledProcessError as e:
        #     return 1, "song cannot be found"
        # audio_data = out.splitlines()
        # audio_name = audio_data[0].decode("utf-8")
        # audio_id = audio_data[1].decode("utf-8")
        # audio_url = audio_data[3].decode("utf-8")
        # audio_time = audio_data[4].decode("utf-8")

        ydl_opts = {
            'default_search': "ytsearch",
            'quiet': True,
            'nocheckcertificate': True

        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                # ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])
                result = ydl.extract_info(keywords, download=False)
        except (youtube_dl.utils.ExtractorError, youtube_dl.utils.DownloadError) as e:
            # return 1 if no song can be found by youtube-dl
            return 1, "Error {0} song cannot be found".format(e)

        audio_name = result['entries'][0]['title']
        audio_id = result['entries'][0]['id']
        audio_url = result['entries'][0]['formats'][0]['url']
        audio_time = result['entries'][0]['duration']

        return 0, audio_name, audio_url, audio_time, audio_id

    def add_song(self, keywords, creator):
        # this only add song
        song_data={}
        song_info = self.words_to_audio_data(keywords)

        # song_time = self.get_sec(song_info[3])

        song_data['name'] = song_info[1]
        song_data['url'] = song_info[2]
        song_data['id'] = song_info[4]
        song_data['time'] = song_info[3]
        song_data['creator'] = creator

        self.songlist.append(song_data)

        return song_data

    def get_song(self):
        # get the next song from beginning of the list
        # you can use it through youtube class to play it
        if len(self.songlist) > 1:

            # find the next user requested song
            while self.songlist[0]['creator'] == "DJ Robot":
                self.songlist.pop(0)

            # get song
            current_song = self.songlist.pop(0)

            # if the playlist is now empty add a random song
            if len(self.songlist) == 0:
                song_id = current_song['id']
                self.add_new_auto_song(youtube_id=song_id)
                print(self.songlist)

            # add the song to played list
            self.playedlist.append(current_song)
            return current_song

        elif len(self.songlist) == 1:
            # last song was auto generated
            current_song = self.songlist.pop(0)
            song_id = current_song['id']
            # no song left auto generate one
            self.add_new_auto_song(youtube_id=song_id)

            # return auto generated song
            return current_song

    def get_next_info(self, limit=5):
        """
        get infos of the up to limit (5) songs. Not info on current song
        :param limit:
        :return:
        """

        show_songs = []
        total_songs = len(self.songlist)
        for i in range(total_songs):
            if i == total_songs - 1:
                show_songs.append(self.songlist[i])
            elif i < total_songs - 1 and self.songlist[i]['creator'] != "DJ Robot":
                show_songs.append(self.songlist[i])

        return show_songs[:limit]


        # if len(self.songlist) > 1:
        #     if self.songlist[0]['creator'] == "DJ Robot":
        #         return self.songlist[1]
        #     else:
        #         return self.songlist[0]
        # elif len(self.songlist) == 1:
        #     return self.songlist[0]
        # else:
        #     return {"name":"no next song"}

    def get_playlist(self):
        # return the songs to be played
        print(self.songlist)

    def get_played(self):
        #return all the songs that played
        return self.playedlist

    def add_new_auto_song(self , youtube_id=''):
        # https://github.com/ZipBomb/spotify-song-suggestion
        # assume it will just be a rolling stones
        song = [1]
        new_song_data = {}
        keywords = ""
        # if song not found by youtube-dl generate a new song.
        while song[0] != 0:

            if len(youtube_id) !=0:
                keywords = youtube_api.youtube_search(youtube_id)
                print("found recommanded song",keywords)
            else:
                print("song not found, find a new song ")
                rand_artist, rand_song = song_generator.random_song()
                keywords = rand_song + " by " + rand_artist

            song = self.words_to_audio_data(keywords)

            print(song)
        new_song_data['url'] = song[2]
        new_song_data['name'] = song[1]
        new_song_data['time'] = song[3]
        new_song_data['id'] = song[4]
        new_song_data['creator'] = "DJ Robot"
        self.songlist.append(new_song_data)

    def get_sec(self, time_str):
        if ":" in time_str:
            m, s = time_str.split(':')
            return int(m) * 60 + int(s)
        else:
            # only seconds
            return int(time_str)

    # heydj request 'rolling stones' play first song it find
    # heydj skip to next song
    # heydj nowplaying return name of the current song
    # heydj nextup return only the name of next song
    # heydj stop will stop the songs



if __name__ == "__main__":

    while 1:


        # listen to request come in from slack

        #start
        pl = Playlist()
        #play first song
        song_data = pl.get_song()
        print(song_data)
        a = YoutubeAudio(song_data)
        a.play_audio()
        time.sleep(5)

        # add a song
        a = pl.words_to_audio_data('Piano Sonata In B-Flat Minor, MWV U 42 by Marc E. Bassy')
        print(a)

        time.sleep(5)
        # skip to next song
        print("skip to auto")
        a.stop_audio()
        song_data = pl.get_song()
        print(song_data)
        a = YoutubeAudio(song_data)
        a.play_audio()

    a = song_generator.random_song()
    print(a)


