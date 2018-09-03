from app import create_app
# from app.models import User, Message, GloveEmbedding, Line, Day, Line_Schedule, Falcuty, Class
# from app.controllers.emojifier.helpers import emojifier_setup
# from app.controllers.schedule.helpers import schedule_setup, setup_line_time
from app.controllers.classroom.helpers import setup_line_time
from app.models import User

# get the app instance
app = create_app()

@app.shell_context_processor
def make_shell_context():
    # return {
    #     'db': db, 
    #     'User': User, 
    #     "Message": Message, 
    #     "Line": Line,
    #     "Day": Day,
    #     "Class": Class,
    #     "Falcuty": Falcuty,
    #     "Line_Schedule": Line_Schedule,
    #     "GloveEmbedding": GloveEmbedding, 
    #     "emojifier_setup": emojifier_setup,
    #     "schedule_setup": schedule_setup,
    #     "setup_line_time": setup_line_time,
    #     "falcuty_setup": falcuty_setup
    # }
    return {
        "User": User,
        "setup_line_time": setup_line_time
    }


# with app.app_context():
#     try: 
#         schedule_setup(db, Day, Line, Line_Schedule)
#         setup_line_time(db, Line_Schedule)
#         falcuty_setup(db, Falcuty)
#     except: 
#         print("Already created")

app.run(host='0.0.0.0')