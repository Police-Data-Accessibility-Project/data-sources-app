from middleware.third_party_interaction_logic.mailgun_logic import send_via_mailgun
from middleware.util import get_env_variable

html_text = """
<!DOCTYPE html>
<html>
  <head>
    <title>Notifications</title>
  </head>
  <body>
    <p>There have been updates to locations you've followed.</p><br>
    <h1>Data Sources Approved</h1>
    <p>The following data sources were approved:</p>
    <div>
      <ul>
        <li>
          <a href="https://test.com/data-source/52">Test Data Source 1</a>
        </li>
        <li>
          <a href="https://test.com/data-source/79">Test Data Source 2</a>
        </li>
      </ul>
    </div><br>
    <h1>Data Request Completed</h1>
    <p>The following data request was completed:</p>
    <div>
      <ul>
        <li>
          <a href="https://test.com/data-request/45">Test Data Request 2</a>
        </li>
      </ul>
    </div><br>
    <h1>Data Request Started</h1>
    <p>The following data request was started:</p>
    <div>
      <ul>
        <li>
          <a href="https://test.com/data-request/39">Test Data Request 1</a>
        </li>
      </ul>
    </div><br>
    <p>Click 
      <a href="https://test.com/data-request">here</a> to view and update your user profile.
    </p>
  </body>
</html>
"""

def test_send_via_mailgun():
    send_via_mailgun(
        to_email=get_env_variable("TEST_EMAIL_ADDRESS"),
        subject="This is a subject test",
        text=html_text,
        html=html_text
    )