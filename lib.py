

def read_songlist():
    fp = open('static/song.txt', "r")
    song_list = []
    for line in iter(fp):
        song_list.append(line)
    fp.close()

    return(song_list)

def read_lyric():
    fp = open('static/lyric.txt', "r", encoding="utf-8")
    lyric = fp.read()
    fp.close()
    return(lyric)
