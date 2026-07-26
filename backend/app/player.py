import vlc
MUSIC_PATH = "song.mp3"

instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new(MUSIC_PATH)
player.set_media(media)

is_paused = False