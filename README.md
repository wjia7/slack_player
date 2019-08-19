# slack_player
A music player interact through slack

This is a music player that use youtube-dl through youtube to query music. 
The player use youtube api to find similar songs when asked



# TODO:

1. use mutithreading to add song to the list while song is playing? so song get played right after another

2. request auto stop at 6pm probably a good idea.

3. add interactive functionality https://api.slack.com/messaging/interactivity
    * add user from slack who requested each song
    * add a pause function
    * add voting function (approve/reject)

4. If auto d, finish current song before play next song

5. if no youtube video found. find a different one
