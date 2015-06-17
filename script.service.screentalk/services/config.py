from resources.settings import get_setting

SCRIPTNAME = "ScreenTalk"
SCREENTALK_HOST = get_setting('screentalk_url').strip('/')
SCREENTALK_API = SCREENTALK_HOST + '/api'

KODI_URL = "http://127.0.0.1:80/jsonrpc"
KODI_JSONRPC_BASE_PAYLOAD = {"jsonrpc": "2.0", "id": "1"}

# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after
TWITTER_CONSUMER_KEY = "TzKmC1takxzHeoxqm6ylUfiKQ"
TWITTER_CONSUMER_SECRET = "99DejrKVkINTxTDthcPNDbjh17mSfUtNw8Nkh3adtnYdle3sAz"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
TWITTER_ACCESS_TOKEN = "14186728-gA85ngyLxfIxu3FqA873XYhs29Mhckft39nm5TPSa"
TWITTER_ACCESS_TOKEN_SECRET = "Ydba4gAUOBHw2EB50vM3A9tiM9UtvvySPHZJD4MtPh8VP"

DIALOG_LIFESPAN_MS = 3000  # milliseconds
DIALOG_LIFESPAN_SECONDS = DIALOG_LIFESPAN_MS / 1000.0

KODI_AUTH = ("xbmc", "xbmc")


