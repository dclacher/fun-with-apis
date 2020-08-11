import pyowm
from flask import render_template, request, Blueprint
import log_module as logger
import wikipedia as wiki
import pycountry
import re
from wikipedia import DisambiguationError

the_logger = logger.get_logger(__name__)
"The logger object for this module"

weather_page = Blueprint('weather_page', __name__, template_folder='templates')
"The blueprint (sub-component) to be referenced by the main module (app.py)"

owm = pyowm.OWM('8048605ff47ae7c7249dbcf09736aa7f')
"The object to interact with OWM API"

owm_error_message = ''
"The error message in case an exception occurs on OWM side"

wiki_error_message = ''
"The error message in case an exception occurs on Wikipedia side"

observation = None
"The Observation object retrieved by OWM API, from which Location and Weather objects are retrieved"


@weather_page.route('/weather', methods=['GET', 'POST'])
def weather_info():
    """
    Function to manage the GET and POST requests from the /weather page of the application.
    It interacts with both OWM and Wikipedia APIs.
    :return: a call to Flask's render_template function, to render the page in different ways
    """
    # Declaring local variables and referencing global values
    global owm_error_message
    global wiki_error_message
    global observation
    owm_error_message = ''
    wiki_error_message = ''
    observation = None
    city_query = ''

    # Action to perform in case of a POST request
    if request.method == 'POST':
        city_query = request.form['city_name']

    # Validate input
    if city_query and not validate_input(city_query):
        return render_template('weather.html', observation=None, invalid_input='Invalid input')

    # APIs calls
    if city_query:
        try:
            # Calling the OWM API to retrieve the Observation object
            observation = owm.weather_at_place(city_query)
            # LOGGING the payload for the Weather object received from OWM API
            the_logger.debug('OWM API Weather object: ' + observation.get_weather().to_JSON())
            # LOGGING the payload for the Location object received from OWM API
            the_logger.debug('OWM API Location object: ' + observation.get_location().to_JSON())
            # Wikipedia API flow
            summary = ''
            url = ''
            country_name = pycountry.countries.get(alpha_2=observation.get_location().get_country()).name
            search_string = observation.get_location().get_name() + ', ' + country_name
            search_results = wiki.search(search_string, results=10)
            # LOGGING the search results from Wikipedia
            the_logger.debug('Wikipedia search results: ' + str(search_results))
            match_list = ['city', 'municipality', 'prefecture', 'capital', 'cities', 'prefectures', 'urban area']
            for result in search_results:
                try:
                    temp_summary = wiki.summary(result, sentences=5)
                    temp_summary_list = temp_summary.split()
                    # using list comprehension to check if string contains list element
                    res = [ele for ele in match_list if (ele in temp_summary_list)]
                    if bool(res):
                        summary = wiki.summary(result, sentences=5)
                        # LOGGING the summary retrieved from Wikipedia API for the city
                        the_logger.debug('Wikipedia summary result: ' + summary)
                        url = wiki.page(result).url
                        # LOGGING the URL retrieved from Wikipedia API for the city
                        the_logger.debug('Wikipedia URL result: ' + url)
                        break
                except DisambiguationError as d:
                    # Handling specific Wikipedia error, including LOGGING
                    the_logger.error(d)
                    wiki_error_message = str(d)
                    continue
            return render_template('weather.html', observation=observation, wiki_summary=summary, wiki_url=url,
                                   wiki_error_message=wiki_error_message)
        except Exception as e:
            # Handling OWM exceptions/errors, including LOGGING
            the_logger.error(e)
            owm_error_message = str(e)
            return render_template('weather.html', observation=None, owm_error_message=owm_error_message,
                                   wiki_error_message=wiki_error_message)
    # What to return in case of a GET request
    else:
        return render_template('weather.html', observation=None, owm_error_message=owm_error_message,
                               wiki_error_message=wiki_error_message)


def validate_input(city):
    pattern = re.compile("^[a-zA-ZÀ-ÿ .'-]+[,]?[a-zA-ZÀ-ÿ .'-]+[^,]*$")
    if pattern.match(city):
        return True
    return False
