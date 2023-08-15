import os
import json
import logging
import ssl

from flask import Flask, request, make_response, Response

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

from slashCommand import Slash

# python uses a SSL cert store which doesn't support the cert used by slack, this works as a temporary workaround
ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

@app.route("/slack/test", methods=["POST"])
def command():
  if not verifier.is_valid_request(request.get_data(), request.headers):
    return make_response("invalid request", 403)
  info = request.form

  if "payload" in info:
    payload = json.loads(request.form["payload"])
    if payload["type"] == "view_submission":
      print(payload["view"]["state"]["values"])
      return make_response("", 200)

  try:
    response = slack_client.views_open(
      trigger_id=info["trigger_id"],
      view={
        "type": "modal",
        "title": {
          "type": "plain_text",
          "text": "Add Collection"
        },
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "Mark a collection for IP infringement"
            },
            "block_id": "section1",
          },
          {
            "type": "input",
            "label": {
              "type": "plain_text",
              "text": "Address"
            },
            "element": {
              "type": "plain_text_input",
              "action_id": "address",
              "placeholder": {
                "type": "plain_text",
                "text": "Type in here"
              },
            },
          },
           {
            "type": "input",
            "label": {
              "type": "plain_text",
              "text": "Chain (e.g. MAINNET)"
            },
            "element": {
              "type": "plain_text_input",
              "action_id": "chain",
              "placeholder": {
                "type": "plain_text",
                "text": "Type in here"
              },
            },
          }
        ],
        "close": {
          "type": "plain_text",
          "text": "Cancel"
        },
        "submit": {
          "type": "plain_text",
          "text": "Save"
        },
        "private_metadata": "Shhhhhhhh",
        "callback_id": "view_identifier_12"
      }
    )
  except SlackApiError as e:
    logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
    logging.error(e.response)
    return make_response("", e.response.status_code)

  return make_response("", response.status_code)

@app.route("/slack/submit", methods=["POST"])
def submit():
  print("we get here")
  if not verifier.is_valid_request(request.get_data(), request.headers):
    return make_response("invalid request", 403)
  info = request.form
  print("REQUEST FORM", "payload" in info)

  # # send user a response via DM
  # im_id = slack_client.im_open(user=info["user_id"])["channel"]["id"]
  # ownerMsg = slack_client.chat_postMessage(
  #   channel=im_id,
  #   text="Thanks for submitting a collection!"
  # )

  # send channel a response
  response = slack_client.chat_postMessage(
    channel='#{}'.format(info["channel_name"]), 
    text="Thanks for submitting a collection!"
  )

  return make_response("", response.status_code)

# Start the Flask server
if __name__ == "__main__":
  SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
  SLACK_SIGNATURE = os.environ['SLACK_SIGNATURE']
  slack_client = WebClient(SLACK_BOT_TOKEN)
  verifier = SignatureVerifier(SLACK_SIGNATURE)

  commander = Slash("Hey there! It works.")

  app.run(port=8080)