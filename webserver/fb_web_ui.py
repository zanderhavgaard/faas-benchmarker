from webserver_db_interface import DB_interface
from pyfiglet import Figlet
from flask import (
    Flask,
    render_template
)
import time
from flask_socketio import SocketIO, emit

# create app instances
app = Flask(__name__)
# TODO is the secret_key needed?
#  app.config['SECRET_KEY'] = 'very_secret'
db = DB_interface()
socketio = SocketIO(app)


@app.route('/')
def index():

    # create the ascii banner
    banner = Figlet(width=120).renderText('faas-benchmarker')

    # get data from db 
    data = create_index_data_dict()

    page = render_template('index.html',
                           banner=banner,
                           data=data
                           )
    return page


@socketio.on('update_data')
def update_date():
    data = {
        'experiment_status_table_html': create_experiment_status_table_html(),
        'experiment_table_html': create_experiment_table_html(),
    }
    emit('update_data', data)


def ready_experiment_data():
    # prepare experiment data
    experiments = db.get_experiments()
    if experiments is not None:
        experiments = make_experiment_data_more_readable(experiments)
        experiment_keys = list(experiments[0].keys())
    else:
        experiments = {}
        experiment_keys = {}
    return(experiment_keys,experiments)


def create_experiment_table_html():
    experiment_keys, experiments = ready_experiment_data()
    experiment_table_html = render_template('experiment_table.html',
                                            data={'experiment_keys': experiment_keys,
                                                  'experiments': experiments,
                                            })
    return experiment_table_html


def ready_experiment_status_data():
    # prepare experiment status data
    experiment_status = db.get_experiment_status()
    if experiment_status is not None:
        experiment_satus = make_experiment_status_human_readable(experiment_status)
        experiment_status_keys = list(experiment_status[0].keys())
    else:
        experiment_status = {}
        experiment_status_keys = {}
    return (experiment_status_keys,experiment_status)



def create_experiment_status_table_html():
    experiment_status_keys, experiment_status = ready_experiment_status_data()
    experiment_status_table_html = render_template('experiment_status_table.html',
                                                   data={'experiment_status_keys': experiment_status_keys,
                                                         'experiment_status': experiment_status,
                                                   })
    return experiment_status_table_html


def create_index_data_dict():
    experiment_status_keys, experiment_status = ready_experiment_status_data()
    experiment_keys, experiments = ready_experiment_data()
    data = {
        'experiment_status': experiment_status,
        'experiment_status_keys': experiment_status_keys,
        'experiment_status_table_header': 'Experiment Status:',
        'experiment_table_header': 'Experiment data:',
        'experiment_keys': experiment_keys,
        'experiments': experiments,
    }

    return data


def make_experiment_status_human_readable(experiment_status: dict) -> dict:
    for exp_stat in experiment_status:
        # make start time readable
        start_time = exp_stat['start_time']
        end_time = exp_stat['end_time']
        if end_time == 0:
            exp_stat['end_time'] = 'n/a'
        else:
            exp_stat['end_time'] = human_readable_time(exp_stat['end_time'], show_date=True)
        exp_stat['start_time'] = human_readable_time(start_time, show_date=True)
        # add running time if experiment is running
        if exp_stat['status'] != 'failed' and exp_stat['status'] != 'completed':
            running_time = human_readable_time(time.time() - start_time)
            exp_stat['running_time'] = running_time
        else:
            exp_stat['running_time'] = human_readable_time(end_time - start_time)

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
        if seconds > 86400:
            return f'{int(seconds // 86400)} days ' + time.strftime("%H:%M:%S", time.gmtime(seconds))
        else:
            return time.strftime("%H:%M:%S", time.gmtime(seconds))

if __name__ == '__main__':
    socketio.run(app, port=7890, host='0.0.0.0')
