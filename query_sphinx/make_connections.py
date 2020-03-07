import mysql.connector
from .sphinxapi import *

def MakeConnections():
    print("Connecting to the Sphinx server...")

    host = 'localhost'
    port = 9312
    limit = 1000

    sphinx_client = SphinxClient()
    sphinx_client.SetServer ( host, port )
    sphinx_client.SetConnectTimeout (5.) #timeout for long queries
    sphinx_client.SetRankingMode(4) #SPH_RANK_PROXIMITY

    print('Done')

    print("Opening  local database...")

    mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "Q:)T69pw",
    database = "movies"
    )

    mycursor = mydb.cursor(buffered=True)
    print('Done')

    #we keep mydb in order not to loose mycursor (weak reference)
    return(sphinx_client, mydb, mycursor)
