__author__ = 'ekelly30'
import os
import webapp2
import jinja2
from apiclient.discovery import build
from private_config import YOUTUBE_API_KEY

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                                'templates')),
    extensions=['jinja2.ext.autoescape'])


class MainHandler(webapp2.RequestHandler):
    """Handler class for the main page"""

    def get(self):
        """Get the main page, and previous searches"""
        self.response.headers['Content-type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())


class SearchHandler(webapp2.RequestHandler):
    """Handler class for the search page"""

    def get(self):
        """Get the search results page"""
        videos = self.search_by_keyword(self.request.get('Query'))
        self.generate_page(videos)

    def search_by_keyword(self, query_term):
        """
        Perform the API query
        :param query_term: The term to search for
        :return: A list of videos returned by the query
        """
        youtube = build(YOUTUBE_API_SERVICE_NAME,
                        YOUTUBE_API_VERSION,
                        developerKey=YOUTUBE_API_KEY)
        search_response = youtube.search().list(q=query_term,
                                                part="id,snippet",
                                                maxResults=5).execute()

        videos = []
        for search_result in search_response.get("items", []):
            videos.append(search_result)
        return videos

    def generate_page(self, videos):
        """
        Create the search results page from the list of videos
        :param videos: A list of videos returned by the youtube API
        :return:
        """
        template_values = {'videos': videos}
        self.response.headers['Content-type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))

# Run the app with the appropriate page handlers
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/search', SearchHandler),],
                              debug=True)
