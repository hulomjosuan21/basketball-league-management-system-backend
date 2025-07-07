
def job_wrapper(app):
    with app.app_context():
        print("Hello World")