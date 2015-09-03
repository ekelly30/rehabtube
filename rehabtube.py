__author__ = 'ekelly30'
import os
import webapp2
import jinja2
from apiclient.discovery import build
from private_config import YOUTUBE_API_KEY

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
    extensions=['jinja2.ext.autoescape'])


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())


class SearchHandler(webapp2.RequestHandler):
    def post(self):
        self.search_by_keyword(self.request.get('Query'))

    def search_by_keyword(self, query_term):
        youtube = build(YOUTUBE_API_SERVICE_NAME,
                        YOUTUBE_API_VERSION,
                        developerKey=YOUTUBE_API_KEY)
        search_response = youtube.search().list(q=query_term,
                                                part="id,snippet",
                                                maxResults=5).execute()

        videos = []
        for search_result in search_response.get("items", []):
            videos.append(search_result)

        template_values = {
        'videos': videos
        }
        self.response.headers['Content-type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
  ('/', MainHandler),
  ('/search', SearchHandler),
], debug=True)
