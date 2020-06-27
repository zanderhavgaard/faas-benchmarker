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

    # prepare experiment status data
    experiment_status = db.get_experiment_status()
    if experiment_status is not None:
        experiment_satus = make_experiment_status_human_readable(experiment_status)
        experiment_status_keys = list(experiment_status[0].keys())
    else:
        experiment_status = {}
        experiment_status_keys = {}
    experiment_status_table_header = "Experiment Status:"

    # prepare experiment data
    experiments = db.get_experiments()
    if experiments is not None:
        experiments = make_experiment_data_more_readable(experiments)
        experiment_keys = list(experiments[0].keys())
    else:
        experiments = {}
        experiment_keys = {}
    experiment_table_header = "Experiments:"

    data = {
        'experiment_status': experiment_status,
        'experiment_status_keys': experiment_status_keys,
        'experiment_status_table_header': experiment_status_table_header,
        'experiment_table_header': experiment_table_header,
        'experiment_keys': experiment_keys,
        'experiments': experiments,
    }

    page = render_template('index.html',
                           banner=banner,
                           data=data
                           )

    return page


def make_experiment_status_human_readable(experiment_status: dict) -> dict:
    for exp_stat in experiment_status:
        # make start time readable
        start_time = exp_stat['start_time']
        exp_stat['start_time'] = human_readable_time(start_time, show_date=True)
        # add running time if experiment is running
        status = exp_stat['status']
        if status == 'running':
            running_time = human_readable_time(time.time() - start_time)
            exp_stat['running_time'] = running_time
        elif status == 'completed':
            exp_stat['running_time'] = 'completed'
        elif status == 'failed':
            exp_stat['running_time'] = 'failed'

    return experiment_status


def make_experiment_data_more_readable(experiments: dict):
    if experiments is None:
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
