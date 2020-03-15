#!/usr/bin/env python3

import re
import time
from .parse_query import ParseQuery

def QuerySphinx(sphinx_client, mydb, mycursor, query, fst_lang, scd_lang, offset, res_per_page, pos_tags, imdb_id):

# fst_lang = "en"
# scd_lang = "ru"

    if set((fst_lang, scd_lang)) == {'en', 'ru'}:
        sentence_table = 'sentences_en_ru'
    elif set((fst_lang, scd_lang)) == {'en', 'fr'}:
        sentence_table = 'sentences_en_fr'
    elif set((fst_lang, scd_lang)) == {'fr', 'ru'}:
        sentence_table = 'sentences_fr_ru'

    max_sentences_length = 1000
    #
    # offset = 0
    # res_per_page = 100

    #options for sphinx BuildExcerpts function
    excerpts_opt = {
    "before_match": '<span class="marked">',
    "after_match": '</span>',
    "chunk_separator": '',
    "limit": 1000,
    "around": 1000,
    }

    if sphinx_client._reqs:
        return {'error_code': -10, 'error_msg': "The server is busy. Try to repeat your search later."}


    #if language is Russian, no POS tags are possible, don't parse the query and use the Sphinx lemmatizer
    #if language is English and  POS tags are not requested, don't parse the query and use the Sphinx lemmatizer
    #otherwise, parse the query (add wordforms for each word) and send it to Sphinx for search
    if fst_lang in ("en", "ru") and not (query.count('_') or pos_tags):

        index = (sentence_table+'_{}_clean').format(fst_lang)
        sentence1_column = 'sentence_{}_clean'.format(fst_lang)

    else:

        status, query, error_msg = ParseQuery(query, mycursor, fst_lang)
        if status<0:
            return {'error_code': status, 'error_msg': error_msg}
        index = (sentence_table+'_{}').format(fst_lang)
        sentence1_column = 'sentence_{}'.format(fst_lang)

    if  not pos_tags or scd_lang == "ru":
        sentence2_column = 'sentence_{}_clean'.format(scd_lang)
    else:
        sentence2_column = 'sentence_{}'.format(scd_lang)

    sphinx_client.SetLimits (offset, res_per_page) #request only results for the current page

    try:
        # start = time.time()
        res = sphinx_client.Query (query, index )
        # end = time.time()
    except Exception as e:
        sphinx_client._reqs=[] #clear previous query
        return {'error_code': -100, 'error_msg': "Timeout error. Try to limit your search."}

    if not res or not res['total_found']:
        return {'error_code': -1, 'error_msg': "No matches found. Try again!"}

    # print("query time: {}s".format(end-start))

    matches = res['matches']

    # print("Total matches:{} (max:{})".format(res['total_found'], limit))

    def clean_sentences(sentences, lang):
        # sentences = cl.BuildExcerpts([sentences,], index, query, excerpts_opt)[0]
        if len(sentences) == max_sentences_length:
            sentences += "..."
        if not pos_tags:
            sentences = re.sub('_[\$A-Z]+','', sentences)
        sentences = sentences.replace(" '", "'")
        if lang=="en":
            sentences = sentences.replace(" n't", "n't")
            sentences = sentences.replace("</span>n't", "n't</span>")
        # sentences = sentences.replace("\n", "<br>")
        return sentences

    sentences_1 = list()
    sentences_2 = list()
    titles = list()
    imdb_ids = list()

    #for each found sentences group
    for match in matches:

        id = match['id'] #sentences group sphinx id

        imdb_id = id//10000

        imdb_id_text = str(imdb_id)
        #add zeros at the beginning of short ids to generate the right link to the imdb movie page
        imdb_id_text = '0'* (7-len(imdb_id_text)) + imdb_id_text
        imdb_ids.append(imdb_id_text)

        #retrieve sentences from the database
        sql = ('SELECT {}, {} FROM {} WHERE '
                ' sentence_id = {}'.format(
                sentence1_column, sentence2_column, sentence_table, id))
        mycursor.execute(sql)
        r = mycursor.fetchone()

        sentences_1.append(r[0])
        sentences_2.append(r[1])

        #retrieve year and title from the titles_new db to display after each search result
        sql = ('SELECT year, lang, title FROM titles_new WHERE imdb_id = {} AND lang IN ("{}", "{}") ORDER BY lang'.format(imdb_id, fst_lang, scd_lang))
        mycursor.execute(sql)
        r = mycursor.fetchall()

        year = r[0][0]
        title = {r[0][1]:r[0][2], r[1][1]:r[1][2]} #language:title_in_this_language

        title = 'Title: {} ({}) - {}'.format(title[fst_lang], title[scd_lang], year, imdb_id)

        titles.append(title)

    #use the SphinxAPI BuildExcerpts function to highlight query words in the search result
    sentences_1 = sphinx_client.BuildExcerpts(sentences_1, index, query, excerpts_opt)

    sentences_1 = [clean_sentences(s, fst_lang) for s in sentences_1]
    sentences_2 = [clean_sentences(s, scd_lang) for s in sentences_2]


    return {'total_found':res['total_found'], 'matches':list(zip(sentences_1, sentences_2, titles, imdb_ids)), 'error_code':0}
