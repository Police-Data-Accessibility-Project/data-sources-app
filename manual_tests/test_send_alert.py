from middleware.scheduled_tasks.check_database_health import send_alert


def test_send_alert():
    send_alert("Hello World")
