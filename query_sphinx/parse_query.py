#!/usr/bin/env python3

import re

#function to get all combinations of words for the long query format
def permut(all, i, s, res):
    if i < len(all):
        for j in range(len(all[i])):
            res = permut(all, i+1, s + [all[i][j]], res)
    else:
        res.append(s)
    return res

#
# def expand_tags(tag):
#     tag = tag.upper()
#     if tag == "VB*":
#         return "'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'"
#     elif tag == "NN*":
#         return "'NN', 'NNS', 'NNP', 'NNPS'"
#     elif tag == "JJ*":
#         return "'JJ', 'JJR', 'JJS'"
#     elif tag == "RB*":
#         return "'RB', 'RBR', 'RBS'"
#
#     return "'" + tag + "'"

# def collapse_tags(tag):
#     tag = tag.upper()
#     if tag[0:2] == "JJ":
#         return "JJ*"
#     elif tag in {"NN", "NNS", "NNP", "NNPS"}:
#         return "NN*"
#     elif tag[:2] == "RB":
#         return "RB*"
#     elif tag[:2] == "VB":
#         return "VB*"
#     return tag

def ParseQuery(q, mycursor, fst_lang):

    max_query_length = 13400 #maximum query length accepted by sphinx daemon
    min_infix_len = 3 #see sphinx.conf

    for s in ",?!":
        q = q.replace(s, ' ')

    q = q.replace("'", " '") #any word starting with ' is a separate word
    q = q.lower() #to avoid confusion while comparing
    q = " " + q + " " #to always have fragments at the beggining and at the end

    #forbid *_JJ, *_RB etc.
    if re.search('[\W\d]+\*_\w+',q):
        return([-2, '',  "Your request expands in a too long query. Try to limit your search."])

    if q.count('"'):
        #for the phrase search don't insert multiple wordforms inside the phrase
        #create a distinct phrase for each wordform and then concatenate these phrases with the OR operator
        long_query_format = 1
    else:
        #replace words in the initial query by their wordforms separated by the OR operator
        long_query_format = 0


    fragments = list() #anything which doesn't contain letters or underscore
    words = list()

    exact_phrase = 0 # for the EXACT Sphinx operator = (exact wordform/phrase search)
    start = 0

    #split the query into words(containing letters and _) and fragments
    while start < len(q):
        r = re.search("\=?[a-z_\*\']+",q[start:])
        if r:
            word = r.group()
            fragment = q[start: start + r.start()]
            if fragment.count('="'):
                exact_phrase = 1
            elif fragment.count('"'):
                exact_phrase = 0
            start = start + r.end()
            fragments.append(fragment)
            words.append(word)
        else:
            fragments.append(q[start:])
            break

    all_w_tagged = list()
    words_tagged = None
    query_words = list() #will contain wordforms for the words in the query

    #look for a tag(s) for each word in the query, to be able to use full-text search
    #add each tag to its word
    for w in words:

        if w.count('*'):

            if re.search('\*[a-z]+$', w) and len(w)>=min_infix_len:
                #if the user didn't put the tag with a wildcard(*) search
                words_tagged = [w, w + '_*']
            else:
                words_tagged = [w]

        else:

            w_spl = w.split('_')

            if (w.count('=')  or exact_phrase):
                #keep the requested wordform(WHERE word = ...)

                if len(w_spl)>1:
                    #if a particular tag is indicated in the query, use it to filter the results
                    sql = 'SELECT word, tag FROM dict_{} WHERE word = "{}" AND tag = "{}"'.format(fst_lang, w_spl[0], w_spl[1])

                else:
                    sql = 'SELECT word, tag FROM dict_{} WHERE word = "{}"'.format(fst_lang, w)

            else:
                #collect all wordforms for the requested lemma(WHERE lemma = ...)

                if len(w_spl)>1:
                    #if a particular tag is indicated in the query, use it to filter the results
                    sql = 'SELECT word, tag FROM dict_{} WHERE lemma = "{}" AND tag = "{}"'.format(fst_lang, w_spl[0], w_spl[1])

                else:
                    sql = ('SELECT word, tag FROM dict_{} WHERE lemma IN'
                    '(SELECT lemma FROM os_ulmtd_{} WHERE word = "{}")'.format(fst_lang, fst_lang, w))

            mycursor.execute(sql)
            r = mycursor.fetchall()

            if r:
                #if there is a tag X in the dictionary, add the word without tags
                #since the word is unlabelled in the sentences database
                words_tagged = [x[0] if x[1] == 'X' else x[0] + '_' + x[1] for x in r]
            else:
                #if there are no results for the word, accept
                #any tag (the word was labelled but was removed from the dictionary as rare)
                #no tag (the word in the sentence may not be labelled)
                words_tagged = [w, w + '_*']

        #if not words_tagged:
        #    return ([-3, '', 'Unknown words in the query. Use another dictionary!'])

        if words_tagged:

            if not long_query_format:
                #put the OR operator btw all wordforms
                words_tagged = "(" + "|".join(words_tagged) + ")"

            query_words.append(words_tagged)

    #restore the query: put fragments and withdrawn wordforms in the righ order
    if long_query_format:

        query_words = permut(query_words, 0, list(), list() )

        new_query = list()
        for t in query_words:
            r = [a + b for a, b in zip(fragments, t)]
            r.append(fragments[-1])
            r = '(' + ''.join(r) + ')'
            new_query.append(r)

        new_query = '|'.join(new_query)

    else:

        new_query = [a + b for a, b in zip(fragments, query_words)]
        new_query.append(fragments[-1])
        new_query = ''.join(new_query)

    if len(new_query) > max_query_length:
        return([-2, '',  "Your request expands in a too long query. Try to limit your search."])


    return([1, new_query, ''])
