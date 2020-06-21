from webserver_db_interface import DB_interface
from pyfiglet import Figlet
from flask import (
    Flask,
    render_template
)

app = Flask(__name__)
db = DB_interface()


@app.route('/')
def hello_world():

    # create the ascii banner
    banner = Figlet(width=120).renderText('faas-benchmarker')

    experiments = db.get_experiments()

    experiment_table_header = "Experiments:"

    experiment_keys = list(experiments[0].keys())

    page = render_template('index.html',
                           banner=banner,
                           experiment_table_header=experiment_table_header,
                           experiment_keys=experiment_keys,
                           experiments=experiments
                           )

    return page
