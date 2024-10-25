from middleware.third_party_interaction_logic.mailgun_logic import send_via_mailgun
from middleware.util import get_env_variable

html_text = """
<p>There have been updates to locations you've followed.
</br>
<h1>New Data Sources Approved</h1>
<p>The following data sources associated with your followed locations have been approved:</p>
<ul>
	<li><a href="www.google.com">Test Data Source 1</a></li>
</ul>
</br>
<h1>Data Requests Ready to Start</h1>
<p>The following data requests associated with your followed locations have been marked as 'Ready to Start':</p>
<ul>
	<li><a href="www.google.com">Test Data Request 1</a></li>
</ul>
</br>
<h1>Data Requests Completed</h1>
<p>The following data requests associated with your followed locations have been completed:</p>
<ul>
	<li><a href="www.google.com">Test Data Request 2</a></li>
</ul>
</br>
<p>Click <a href="www.google.com">here</a> to view and update your user profile.
"""

def test_send_via_mailgun():
    send_via_mailgun(
        to_email=get_env_variable("TEST_EMAIL_ADDRESS"),
        subject="This is a subject test",
        text=html_text,
        html=html_text
    )