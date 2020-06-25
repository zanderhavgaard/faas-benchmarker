from webserver_db_interface import DB_interface
from pyfiglet import Figlet
from flask import (
    Flask,
    render_template
)
import time

app = Flask(__name__)
db = DB_interface()


@app.route('/')
def index():

    # create the ascii banner
    banner = Figlet(width=120).renderText('faas-benchmarker')

    experiments = db.get_experiments()

    experiment_table_header = "Experiments:"

    experiment_keys = list(experiments[0].keys())

    experiments_human_readable = make_experiment_data_more_readable(experiments)

    page = render_template('index.html',
                           banner=banner,
                           experiment_table_header=experiment_table_header,
                           experiment_keys=experiment_keys,
                           experiments=experiments_human_readable
                           )

    return page


def make_experiment_data_more_readable(experiments: dict):
    if experiments == None:
        return None

    for exp in experiments:
        exp['dev_mode'] = 'true' if exp['dev_mode'] == 1 else 'false'
        exp['start_time'] = human_readable_time(exp['start_time'], show_date=True)
        exp['end_time'] = human_readable_time(exp['end_time'], show_date=True)
        exp['total_time'] = human_readable_time(exp['total_time'])
        exp['memory'] = f"{round(exp['memory'] / (1024 ** 3), 2)} gb"

    return experiments


def human_readable_time(seconds: float, show_date: bool = False):
    if show_date:
        return time.strftime("%d/%m-%y %H:%M:%S", time.gmtime(seconds))
    else:
        return time.strftime("%H:%M:%S", time.gmtime(seconds))
