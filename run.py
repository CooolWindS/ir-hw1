from flask import Flask
from flask import render_template
from flask import request
import lib

app = Flask(__name__)
song_name = 'RESET'

@app.route("/index")
@app.route("/")
def home():
    return render_template('base.html')

@app.route("/search_form")
def search_form():
    return render_template('search_form.html')

@app.route("/result_list",  methods=['POST'])
def result_list():
    global song_name
    song_name = request.values['song_name']

    #TODO: 對 song_name 的搜尋結果
    # 結巴使用應該在此

    list = ["result1", "result2", "result3"]

    return render_template("result_list.html", list=list, song_name = song_name)

@app.route("/songs")
def songs():

    # TODO: 資料庫中所有的歌曲
    song_list = lib.read_songlist()

    return render_template("songs.html", list=song_list)

@app.route("/lyrics/<name>")
def lyrics(name):

    # TODO: 顯示 name 的歌詞
    lyric = lib.read_lyric()
    
    return render_template("lyrics.html", result = name, lyric = lyric)

if __name__ == "__main__":
    app.run()
