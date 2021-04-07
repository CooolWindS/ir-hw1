import json
import jieba
import os


def add_doc_terms_to_reverse_index(reverse_idx, doc_id, doc_terms):
    unique_doc_terms = set(doc_terms)
    
    for term in unique_doc_terms:
        if term not in reverse_idx:
            reverse_idx[term] = []
        
        term_freq = doc_terms.count(term)
        
        reverse_idx[term].append((doc_id, term_freq))

        
def save_reverse_index(reverse_idx, save_path):
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(reverse_idx, f, ensure_ascii=False, indent=4)


def save_song_info(info_list, save_path):
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(info_list, f, ensure_ascii=False, indent=4)



if __name__ == '__main__':
    
    save_dir = '../web/static/data'
    doc_dir = '../web/static/data/lyrics'
    
    jieba.set_dictionary('../web/static/data/dict.txt.big') # use traditional Chinese dictionary
    stopwords = [' ', '\n', '\u3000', '\xa0']
    
    reverse_idx = {}
    song_info_list = []
    
    doc_id = 0
    for f in os.listdir(doc_dir):
        path = os.path.join(doc_dir, f)
        
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            terms = jieba.lcut_for_search(content)
            terms = [t.lower() for t in terms if t not in stopwords]
            add_doc_terms_to_reverse_index(reverse_idx, doc_id, terms)
            
            info = {'title': f[:-4], 'length': len(terms), 
                    'path': os.path.join('static', 'data', 'lyrics', f)}
            song_info_list.append(info)
            
            doc_id += 1
    
    rev_path = os.path.join(save_dir, 'reverse_index.json')
    info_path = os.path.join(save_dir, 'song_info.json')
    save_reverse_index(reverse_idx, rev_path)
    save_song_info(song_info_list, info_path)