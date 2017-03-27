from __future__ import print_function
import urllib2
import json

def lambda_handler(event, context):
    # print my app id
    print("event.session.application.applicationId=" + event['session']['application']['applicationId'])

    # check if incoming app id matches, return error if not
    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.0cdb553d-78ec-433c-a3e7-7fadb6615650"):
        raise ValueError("Invalid Application ID")

    # check if its a new session and print out details
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    # starts up skill
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
     # performs skill intent
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    # stops skill
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

# called when the session starts
def on_session_started(session_started_request, session):
    print("Starting new session.")

# Called when the user launches the skill without specifying what they want
def on_launch(launch_request, session):
    return get_welcome_response()

# Called when the user specifies an intent for this skill
def on_intent(intent_request, session):

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "WhoAreTottenhamHotspurPlayingNext":
        print("checking for match data")
        return get_match_data(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print("Ending session.")
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Match Finder - Thanks"
    speech_output = "Thank you for using the Match Finder skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the football match lookup service. " \
                    "Please tell me a football team, " \
                    "and I'll give you details on the next match"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me which football team you want to find a match for." \
                    "For example, say When is the next Chelsea match"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# passes team id to football api and returns next fixture info
def get_match_data(intent):
    session_attributes = {}
    card_title = "Match Info"
    speech_output = "I'm not sure which team you wanted match info for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which team you wanted match info for. " \
                    "Try asking about Spurs or Liverpool for example."
    should_end_session = False

    if "prem_league_teamsslot" in intent["slots"]:
        team_name = intent["slots"]["prem_league_teamsslot"]["value"]
        team_id = get_team_id(team_name)
        if (team_id != "unkn"):
            card_title = "Match info for " + team_name

            response = urllib2.urlopen('https://api.football-data.org/v1/teams/' + str(team_id) + '/fixtures?timeFrame=n14').read()
            result = json.loads(response)
            fixtures = result['fixtures']
            home_team_name = fixtures[0]['homeTeamName']
            away_team_name = fixtures[0]['awayTeamName']
            match_date = fixtures[0]['date']
            match_date = match_date[:10]

            speech_output = home_team_name + ' plays against ' + away_team_name + ' on ' + match_date
            reprompt_text = ""

        return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# checks team name string and returns id
def get_team_id(team_in):
    return {
      "Manchester United FC" : 66,
      "Manchester United " : 66,
      "Man United" : 66,
      "Man U" : 66,
      "Tottenham Hotspur FC" : 73,
      "Tottenham Hotspur" : 73,
      "Tottenham" : 73,
      "Spurs" : 73,
      "AFC Bournemouth" : 1044,
      "Bournemouth" : 1044,
      "Aston Villa FC" : 58,
      "Aston Villa" : 58,
      "Villa" : 58,
      "Everton FC" : 62,
      "Everton" : 62,
      "Watford FC" : 346,
      "Watford" : 346,
      "Leicester City FC" : 338,
      "Leicester City" : 338,
      "Leicester" : 338,
      "Foxes" : 338,
      "Sunderland AFC" : 71,
      "Sunderland" : 71,
      "Norwich City FC" : 68,
      "Norwich City" : 68,
      "Norwich" : 68,
      "Crystal Palace FC" : 354,
      "Crystal Palace" : 354,
      "Palace" : 354,
      "Chelsea FC" : 61,
      "Chelsea" : 61,
      "Swansea City FC" : 72,
      "Swansea City" : 72,
      "Swansea" : 72,
      "Swans" : 72,
      "Newcastle United FC" : 67,
      "Newcastle United" : 67,
      "Newcastle" : 67,
      "Magpies" : 67,
      "Southampton FC" : 340,
      "Southampton" : 340,
      "Arsenal FC" : 57,
      "Arsenal" : 57,
      "Gunners" : 57,
      "West Ham United FC" : 563,
      "West Ham United" : 563,
      "West Ham" : 563,
      "Hammers" : 563,
      "Stoke City FC" : 70,
      "Stoke City" : 70,
      "Stoke" : 70,
      "Liverpool FC" : 64,
      "Liverpool" : 64,
      "Reds" : 64,
      "West Bromwich Albion FC" : 74,
      "West Bromwich Albion" : 74,
      "West Brom" : 74,
      "Albion" : 74,
      "Manchester City FC" : 65,
      "Manchester City" : 65,
      "Man City" : 65
    }.get(team_in, "unkn")

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
