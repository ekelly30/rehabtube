__author__ = 'ekelly30'
import os
import datetime
import logging
import webapp2
import jinja2
from apiclient.discovery import build
from google.appengine.ext import ndb
from private_config import YOUTUBE_API_KEY

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
RESULTS_PER_PAGE = 30
RECENT_SEARCHES_TO_DISPLAY = 10

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
        recent_searches = get_recent_searches()
        template_data = {'recent_searches': recent_searches}
        self.response.write(template.render(template_data))


class SearchHandler(webapp2.RequestHandler):
    """Handler class for the search page"""

    def get(self):
        """Get the search results page"""
        self.store_query()
        response = self.search_by_keyword()
        page_data = self.generate_page_data(response)
        self.generate_page(page_data)

    def store_query(self):
        """Store the query in the database"""
        query=self.request.get('query')
        query_key = ndb.Key(Search, query)
        query_data = Search(key=query_key,
                            search_query=query,
                            date=datetime.datetime.now())
        query_data.put()

    def search_by_keyword(self):
        """
        Perform the API query
        :return: The youtube API search response
        """
        query = self.request.get('query')
        page = self.request.get('page')
        youtube = build(YOUTUBE_API_SERVICE_NAME,
                        YOUTUBE_API_VERSION,
                        developerKey=YOUTUBE_API_KEY)
        search_response = youtube.search().list(q=query,
                                                part='id,snippet',
                                                pageToken=page,
                                                maxResults=RESULTS_PER_PAGE,
                                                type='video').execute()
        return search_response

    def generate_page_data(self, search_response):
        """
        From the youtube API response, build the dictionary necessary to
        populate the jinja template
        :param search_response: The youtube API search response
        :return: A dictionary containing the videos, prev & next page tokens,
                 and the original query term
        """
        response = {}
        response['query'] = self.request.get('query')
        response['prev_page'] = search_response.get('prevPageToken')
        response['next_page'] = search_response.get('nextPageToken')

        videos = []
        for search_result in search_response.get('items', []):
            videos.append(search_result)
        response['videos'] = videos
        return response

    def generate_page(self, page_data):
        """
        Create the search results page from the API search response
        :param page_data: A dictionary containing a list of videos,
                        the previous and next page tokens, and the
                        initial search query
        :return:
        """
        self.response.headers['Content-type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(page_data))


class Search(ndb.Model):
    """Model to hold previous searches"""
    search_query = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(required=True)


def get_recent_searches():
    """Query the datastore to pull the RECENT_SEARCHES_TO_DISPLAY most recent
    searches
    """
    logging.info(Search.query)
    q = Search.query().order(-Search.date)
    recent_searches = [_ for _ in q][:RECENT_SEARCHES_TO_DISPLAY]
    return recent_searches


# Run the app with the appropriate page handlers
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/search', SearchHandler),],
                              debug=True)
