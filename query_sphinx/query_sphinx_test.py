def QuerySphinx(query):

    #2 lines of table for test
    results =  {'1': {
    'sentences_L1':"<p>First sentence_L1.</br> Second_sentence_L1.</br> Third_sentence_L1.</p>",
    'sentences_L2': "<p>First sentence_L2.</br> Second_sentence_L2.</br> Third_sentence_L2.</p>",
    'title_L1': "Title_L1", 'title_L2': "Title_L2"},
    '2': {'sentences_L1':"<p>First sentence_L1. </br> Second_sentence_L1. </br> Third_sentence_L1.</p>",
    'sentences_L2':"<p>First sentence_L2.</br> Second_sentence_L2.</br> Third_sentence_L2.</p>",
    'title_L1': "Title_L1", 'title_L2': "Title_L2"}}

    for i in range (3,1000):
        results[str(i)] = results['2']

    table_data = list()
    for r in results:
        table_data.append([results[r]['sentences_L1'], results[r]['sentences_L2'],
        results[r]['title_L1'], results[r]['title_L2']])
        #table_data.append([results[r]['title_L1'], results[r]['title_L2']])

    results = {'matches': table_data, 'total_found': len(table_data)}

    return results
