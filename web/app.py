import json
import jieba
import os
import math
import re

from flask import Flask, request, redirect, url_for, render_template

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
       
    return data

def read_song(song_id):
    global song_info_list
    
    song_path = song_info_list[song_id]['path']
    song_title = song_info_list[song_id]['title']
    
    with open(song_path, 'r', encoding='utf-8') as f:
        song_lyric = f.read()
    
    return {'id': song_id, 'title': song_title, 'content': song_lyric}


app = Flask(__name__)

dict_path = os.path.join(app.static_folder, 'data', 'dict.txt.big')
jieba.set_dictionary(dict_path) # use traditional Chinese dictionary
stopwords = [' ', '\n', '\u3000', '\xa0']

rev_path = os.path.join(app.static_folder, 'data', 'reverse_index.json')
reverse_idx = load_json(rev_path)

song_info_path = os.path.join(app.static_folder, 'data', 'song_info.json')
song_info_list = load_json(song_info_path)

avgdl = 0
for info in song_info_list:
    avgdl += info['length']
avgdl /= len(song_info_list)


@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        q = request.form.get('search')
        if q is not None:
            return redirect(url_for('result', search=q))
        
    return render_template('search.html')

@app.route("/result", methods=['GET'])
def result():
    if request.method == 'GET':
        search_string = request.args.get('search')
        
        if search_string is None:
            return redirect(url_for('search'))
        
        terms = jieba.lcut_for_search(search_string)
        terms = [t.lower() for t in terms if t not in stopwords]
       
        song_score = {}
        for t in terms:
            for song_id, score in bm25(t):
                pre_score = song_score.get(song_id, 0)
                song_score[song_id] = pre_score + score
       
        threshold = 0.05
        result_list = [(song_id, score) for song_id, score in song_score.items() if score >= threshold]
        result_list.sort(key = lambda x: x[1], reverse=True)
        
        result_list = [read_song(song_id) for song_id, _ in result_list]
        
        pattern = r'{}'.format('|'.join(terms))
        for i, song in enumerate(result_list):
            mark_list = mark_content_by_pattern(song['content'], pattern)
            result_list[i]['mark_list'] = mark_list
            result_list[i]['mark_length'] = len(mark_list)
            
        return render_template('result.html', result_list=result_list, search_string=search_string)
        
    return redirect(url_for('search'))

@app.route('/song/<song_id>', methods = ['GET', 'POST'])
def song(song_id):
    global app
    global song_info_list
    
    try:
        song_id = int(song_id)
    except:
         return redirect(url_for('search'))
     
    if request.method == 'GET' and int(song_id) < len(song_info_list):
        song = read_song(song_id)
        return render_template('song.html', song=song)
    
    return redirect(url_for('search'))

def bm25(term):
    global reverse_idx
    global avgdl
    global song_info_list
    
    k1 = 1.6
    b = 0.75
    
    term_list = reverse_idx.get(term, [])
    
    idf = (len(song_info_list) - len(term_list) + 0.5) / (len(term_list) + 0.5)
    idf += 1
    idf = math.log(idf)
    
    for song_id, tf in term_list:
        song_len = song_info_list[song_id]['length']
        
        score = idf * tf * (k1+1) / (tf + k1 * (1 - b + b * song_len / avgdl))
        yield song_id, score
        

# find terms that match the query and mark them
# by placing them in odd position of a list of strings
def mark_content_by_pattern(content, pattern):
    mark_list = []
    last = 0
    length = 0
    for match in re.finditer(pattern, content, re.IGNORECASE):
        st, end = match.span()
    
        if last + 40 < st:
            if last == 0:
                mark_list.append('...' + content[st-20:st])
            else:
                mark_list.append(content[last:last+20] + '...' + content[st-20:st])
        else:
            mark_list.append(content[last:st])
        length += len(mark_list[-1])
        
        mark_list.append(content[st:end])
        length += len(mark_list[-1])
        last = end

        if length >= 200:
            break
    
    mark_list.append(content[last:last+20])
    # print(mark_list)
    return mark_list
    
if __name__ == '__main__':
    app.debug = True
    app.run()