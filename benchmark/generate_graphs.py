import sys
import json
import time
from pprint import pprint
from mysql_interface import SQL_Interface as database
from graph_generater import GraphGenerater
import function_lib as lib
from datetime import datetime
from os.path import expanduser

from functools import reduce

import pandas as pd 
import numpy as np
import seaborn as sns

import warnings
warnings.filterwarnings("ignore")

# change 'report' to your default value
name_of_report = sys.argv[1] if len(sys.argv) > 1 else 'report'

dev_mode = eval(sys.argv[2]) if len(sys.argv) > 2 else True # TODO change dev:mode


db = database(True)
gg = GraphGenerater(name_of_report, dev_mode)

# meta coloring and order for produced graphs
hue_order = ['openfaas','aws_lambda','azure_functions']

provider_color_dict = dict({'aws_lambda':'#ff8c00ff',
                    'azure_functions': '#ffd700ff',
                    'openfaas': '#2316deff',
                    })

colors = {
    'light_gray': '#708090ff',
    'blue': '#191970ff'
}

# name sub-directories for the different categories by changing stringvalues in below list
# comment line out of graphs for that category is not wanted
category_of_graphs = [
    lambda : large_function('Large_function',dev_mode)
    # lambda : throughput_graphs( 'Throughput', dev_mode),
    # lambda : coldtimes_graphs('Coldtimes', dev_mode),
    # lambda : test( 'test', dev_mode),
]

# aux function for getting latest uuids from a experiment name
def get_uuids(experiment_name:str):
    return { x[0]: x[1] for x in db.get_latest_metadata_by_experiment(experiment_name) }




def large_function(ldir:str, devmode:bool):

    # metadata
    directory = ldir
    experiment_uuids = get_uuids('coldtime-large-functions ')
    print(experiment_uuids)
    # queries
    def query_by_provider(uuid):
        return f"""select execution_start-invocation_start as latency, execution_total, function_name, 
                instance_identifier as instance_id, throughput,cl_provider as provider from 
                Invocation i left join Experiment e on i.exp_id=e.uuid where e.uuid ='{uuid}';"""
    
    # dataframes
    aws_df = db.get_raw_query(query_by_provider(experiment_uuids['aws_lambda']))
    open_df = db.get_raw_query(query_by_provider(experiment_uuids['openfaas']))
    azure_df = db.get_raw_query(query_by_provider(experiment_uuids['azure_functions']))
    joint_df = pd.concat([aws_df,open_df,azure_df])
       
    config = {
        'x': 'function_name',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        'x_strip': 'instance_id',
        'y_strip': 'latency',
        'strip': True,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    
    gg.swarm_plot(aws_df, config, 'latency bu instance id',directory)
    gg.swarm_plot(open_df, config, 'latency bu instance id',directory)
    gg.swarm_plot(azure_df, config, 'latency bu instance id',directory)







def coldtimes_graphs(ldir:str, devmode:bool):

    # metadata
    directory = ldir
    experiment_uuids = get_uuids('linear-invocation')

    # queries
    def query_by_provider(uuid, level:int):
        return f"""select latency,instance_id, total, thread_id,  multi, provider, if(latency > if(coldtime > 1,1,coldtime), 'cold','warm') as cold, invocation_start  
            from (SELECT instance_identifier as instance_id, execution_total as total, thread_id,  if(numb_threads > 1,0,1) as multi, cl_provider as
            provider, coldtime, execution_start-invocation_start as latency, level, invocation_start from Experiment e 
            left join Invocation i on i.exp_id=e.uuid left join (select avg(execution_start-invocation_start)*3 as coldtime,exp_id as xexp_id from Invocation 
            where exp_id ='{uuid}') x on e.uuid=x.xexp_id where exp_id ='{uuid}') y where level = {level};"""
       
    
    def error_by_provider(uuid):
        return f"""select count(*) as number, cl_provider as provider from Error r left join Experiment e on e.uuid=r.exp_id where e.uuid = '{uuid}';"""


   
    # dataframes
    aws_linear_df = db.get_raw_query(query_by_provider(experiment_uuids['aws_lambda'], 0)) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_linear_df = db.get_raw_query(query_by_provider(experiment_uuids['openfaas'], 0)) if 'openfaas' in experiment_uuids else np.DataFrame()
    azure_linear_df = db.get_raw_query(query_by_provider(experiment_uuids['azure_functions'], 0)) if 'azure_functions' in experiment_uuids else np.DataFrame()
    joint_linear_df = pd.concat([aws_linear_df,open_linear_df,azure_linear_df],ignore_index=True)
    experiment_uuids = get_uuids('linear-invocation-nested')
   
    aws_linear_nested_df = db.get_raw_query(query_by_provider(experiment_uuids['aws_lambda'], 1)) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_linear_nested_df = db.get_raw_query(query_by_provider(experiment_uuids['openfaas'], 1)) if 'openfaas' in experiment_uuids else np.DataFrame()
    azure_linear_nested_df = db.get_raw_query(query_by_provider(experiment_uuids['azure_functions'], 1)) if 'azure_functions' in experiment_uuids else np.DataFrame()
    joint_linear_nested_df = pd.concat([aws_linear_nested_df,open_linear_nested_df,azure_linear_nested_df],ignore_index=True)
    experiment_uuids = get_uuids('scenario-pyramid')
    print(experiment_uuids)
    aws_pyramid_df = db.get_raw_query(query_by_provider(experiment_uuids['aws_lambda'], 0)) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_pyramid_df = db.get_raw_query(query_by_provider(experiment_uuids['openfaas'], 0)) if 'openfaas' in experiment_uuids else np.DataFrame()
    azure_pyramid_df = db.get_raw_query(query_by_provider(experiment_uuids['azure_functions'], 0)) if 'azure_functions' in experiment_uuids else np.DataFrame()
    joint_pyramid_df = pd.concat([aws_pyramid_df,open_pyramid_df,azure_pyramid_df],ignore_index=True)
    aws_error_df = db.get_raw_query(error_by_provider(experiment_uuids['aws_lambda'])) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_error_df = db.get_raw_query(error_by_provider(experiment_uuids['openfaas'])) if 'openfaas' in experiment_uuids else np.DataFrame()
    azure_error_df = db.get_raw_query(error_by_provider(experiment_uuids['azure_functions'])) if 'azure_functions' in experiment_uuids else np.DataFrame()
    joint_error_df = pd.concat([aws_error_df,open_error_df,azure_error_df],ignore_index=True)
    experiment_uuids = get_uuids('growing-load-spikes')
    print(experiment_uuids)
    aws_spike_df = db.get_raw_query(query_by_provider(experiment_uuids['aws_lambda'], 0)) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_spike_df = db.get_raw_query(query_by_provider(experiment_uuids['openfaas'], 0)) if 'openfaas' in experiment_uuids else np.DataFrame()
    azure_spike_df = db.get_raw_query(query_by_provider(experiment_uuids['azure_functions'], 0)) if 'azure_functions' in experiment_uuids else np.DataFrame()
    joint_spike_df = pd.concat([aws_spike_df,open_spike_df,azure_spike_df],ignore_index=True)
    aws_error_spike_df = db.get_raw_query(error_by_provider(experiment_uuids['aws_lambda'])) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_error_spike_df = db.get_raw_query(error_by_provider(experiment_uuids['openfaas'])) if 'openfaas' in experiment_uuids else np.DataFrame()
    azure_error_spike_df = db.get_raw_query(error_by_provider(experiment_uuids['azure_functions'])) if 'azure_functions' in experiment_uuids else np.DataFrame()
    joint_error_spike_df = pd.concat([aws_error_spike_df,open_error_spike_df,azure_error_spike_df],ignore_index=True)

    #########
    # PLOTS #
    #########

    # appendix stuff for showing graph of pyramid - get back to it
    # config = {
    #     'x': 'invocations_start',
    #     'y': 'cold',
    #     'hue': 'provider',
    #     'palette': provider_color_dict,
    #     'hue_order': hue_order,
    #     'ylabel': ('operations (1000)',14),
    #     'xlabel': ('time in seconds',14),
    #     'markers': ['o','s','v'],
    #     'hist':True,
    #     'kde': False,
    #     # 'height': 4,
    #     # 'aspect': 0.8,
    #     'line_kws':{'color':colors['light_gray']},
    # }

    # plist = np.array(aws_pyramid.loc[ : , 'invocation_start' ]).tolist()
    # gg.dist_plot(aws_pyramid,config,'pyramid inocation starts',directory)

    

    config = {
        'x': 'cold',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        'x_strip': 'cold',
        'y_strip': 'latency',
        'strip': True,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    # gg.box_plot(aws_linear_df, config, 'AWS cold times distribution',directory)
    # gg.box_plot(open_linear_df, config, 'AWS cold times distribution',directory)
    # gg.box_plot(azure_linear_df, config, 'AWS cold times distribution',directory)

    config = {
        'x': 'invocation_start',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('latency in seconds',12),
        'xlabel': ('invocation start (unix time)',12),
        'markers': ['o','s','v'],
        'alpha': 0.5,
        # 'jitter': 0.25,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    
    # gg.scatter_plot(joint_linear_df,config,'appendix: latency relative to invocation start',directory,18)
    # joint_linear_df.loc[(joint_linear_df.latency > 10.0 ),'latency']=8.00
    # gg.scatter_plot(joint_linear_df,config,'latency relative to invocation start',directory,18)

    # open_linear_df.loc[(open_linear_df.latency > 10.0 ),'latency']=3.00
    # gg.scatter_plot(aws_linear_df,config,' AWS latency relative to invocation start',directory,18)
    # gg.scatter_plot(open_linear_df,config,' OpenFaaS latency relative to invocation start',directory,18)
    # gg.scatter_plot(azure_linear_df,config,'Azure latency relative to invocation start',directory,18)


    config = {
        'x': 'provider',
        'y': 'cold',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        'alpha': 0.5,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }


    # aws = np.array(aws_linear_df['cold'].value_counts()).tolist()+['aws_lambda']
    # openf = np.array(open_linear_df['cold'].value_counts()).tolist()+['openfaas']
    # azure = np.array(azure_linear_df['cold'].value_counts()).tolist()+['azure_functions']
    # zipped = list(zip(aws,openf,azure))
    # data = {'provider': zipped[2], 'cold': zipped[1],'warm': zipped[0]}
    # df = pd.DataFrame(data)
 

    # gg.bar_plot(df, config,'Cold times: linear-invocation',directory)
    # config['y'] = 'warm'
    # gg.bar_plot(df, config,'Warm times: linear-invocation',directory)   

    # config['x'] = 'instance_id'
    # config['y'] = 'latency'
    
    # copy_aws_linear_df = aws_linear_df.copy(deep=True)  
    # copy_aws_linear_df['instance_id'] = copy_aws_linear_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    # gg.strip_plot(copy_aws_linear_df,config,' AWS latency per function_instance',directory)

    # copy_open_linear_df = open_linear_df.copy(deep=True)  
    # open_linear_df['instance_id'] = copy_open_linear_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    # gg.strip_plot(copy_open_linear_df,config,'OpenFaaS latency per function_instance',directory)


    # copy_azure_linear_df = azure_linear_df.copy(deep=True)  
    # copy_azure_linear_df['instance_id'] = copy_azure_linear_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    # gg.strip_plot(copy_azure_linear_df,config,'Azure latency per function_instance',directory)

    ###################################
    # --> linear-invocation-nested <--#
    ###################################


    config = {
    'x': 'cold',
    'y': 'latency',
    'hue': 'provider',
    'palette': provider_color_dict,
    'hue_order': hue_order,
    'ylabel': ('cold times',12),
    'markers': ['o','s','v'],
    'jitter': 0.1,
    'x_strip': 'cold',
    'y_strip': 'latency',
    'strip': True,
    # 'height': 4,
    # 'aspect': 0.8,
    'line_kws':{'color':colors['light_gray']},
    }

    # gg.box_plot(aws_linear_nested_df, config, 'AWS cold times distribution',directory)
    # gg.box_plot(open_linear_nested_df, config, 'AWS cold times distribution',directory)
    # gg.box_plot(azure_linear_nested_df, config, 'AWS cold times distribution',directory)

    config = {
        'x': 'invocation_start',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('latency in seconds',12),
        'xlabel': ('invocation start (unix time)',12),
        'markers': ['o','s','v'],
        'alpha': 0.9,
        # 'jitter': 0.25,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    
    # gg.scatter_plot(joint_linear_nested_df,config,'latency relative to invocation start',directory,18)
    # joint_linear_nested_df.loc[(joint_linear_nested_df.latency > 8.0 ),'latency']=8.00
    # gg.scatter_plot(joint_linear_nested_df,config,'latency relative to invocation start',directory,18)

    # open_linear_nested_df.loc[(open_linear_nested_df.latency > 3.0 ),'latency']=3.00
    # gg.scatter_plot(aws_linear_nested_df,config,' AWS latency relative to invocation start: nested',directory,18)
    # gg.scatter_plot(open_linear_nested_df,config,' OpenFaaS latency relative to invocation start: nested',directory,18)
    # gg.scatter_plot(azure_linear_nested_df,config,'Azure latency relative to invocation start: nested',directory,18)


    config = {
        'x': 'provider',
        'y': 'cold',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        'alpha': 0.5,
      
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }


    # aws = np.array(aws_linear_nested_df['cold'].value_counts()).tolist()+['aws_lambda']
    # openf = np.array(open_linear_nested_df['cold'].value_counts()).tolist()+['openfaas']
    # azure = np.array(azure_linear_nested_df['cold'].value_counts()).tolist()+['azure_functions']
    # zipped = list(zip(aws,openf,azure))
    # data = {'provider': zipped[2], 'cold': zipped[1],'warm': zipped[0]}
    # df = pd.DataFrame(data)
 

    # gg.bar_plot(df, config,'Cold times: linear-invocation',directory)
    # config['y'] = 'warm'
    # gg.bar_plot(df, config,'Warm times: linear-invocation',directory)   

    # config['x'] = 'instance_id'
    # config['y'] = 'latency'
    
    # copy_aws_linear_nested_df = aws_linear_nested_df.copy(deep=True)  
    # copy_aws_linear_nested_df['instance_id'] = copy_aws_linear_nested_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    # gg.strip_plot(copy_aws_linear_nested_df,config,' AWS latency per function_instance',directory)

    # copy_open_linear_nested_df = open_linear_nested_df.copy(deep=True)  
    # open_linear_nested_df['instance_id'] = copy_open_linear_nested_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    # gg.strip_plot(copy_open_linear_nested_df,config,'OpenFaaS latency per function_instance',directory)


    # copy_azure_linear_nested_df = azure_linear_nested_df.copy(deep=True)  
    # copy_azure_linear_nested_df['instance_id'] = copy_azure_linear_nested_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    # gg.strip_plot(copy_azure_linear_nested_df,config,'Azure latency per function_instance',directory)

#########################
# --> load-scenario <-- #
#########################

    config = {
        'x': 'provider',
        'y': 'number',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('number of errors',12),
        'xlabel': ('Cloud Provider',12),
        'markers': ['o','s','v'],
        'hist':True,
        'kde': False,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    
    gg.bar_plot(joint_error_df,config,'error by provider for load-scenario: pyramid',directory,18)

    aws = np.array(aws_pyramid_df['cold'].value_counts()).tolist()+['aws_lambda']
    print(aws)
    openf = np.array(open_pyramid_df['cold'].value_counts()).tolist()+['openfaas']
    print(openf)
    azure = np.array(azure_pyramid_df['cold'].value_counts()).tolist()+['azure_functions']
    print(azure)
    zipped = list(zip(aws,openf,azure))
    data = {'provider': zipped[2], 'cold': zipped[1],'warm': zipped[0]}
    df = pd.DataFrame(data)

    config = {
        'x': 'provider',
        'y': 'cold',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    gg.bar_plot(df, config,'Cold times: load-scenario: pyramid',directory)
    config['y'] = 'warm'
    gg.bar_plot(df, config,'Warm times: load-scenariocold: pyramid',directory) 

    config = {
        'x': 'provider',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }


    
    gg.boxen_plot(joint_pyramid_df, config, 'Cold times distribution: pyramid',directory)
    config['x'] = 'multi'
    gg.boxen_plot(joint_pyramid_df, config, 'Cold times distribution concurrent: pyramid',directory)

    config = {
        'x': 'invocation_start',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        # 'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    gg.lm_plot(aws_pyramid_df, config, 'AWS latency and invocation start: pyramid', directory)
    gg.lm_plot(open_pyramid_df, config, 'OpenFaaS latency and invocation start: pyramid', directory)
    gg.lm_plot(azure_pyramid_df, config, 'Azure latency and invocation start: pyramid', directory)

    config['fit_reg'] = False
    gg.lm_plot(joint_pyramid_df, config, 'latency and invocation start: pyramid', directory)



    def find_cold_times(df):

        cold_times = {}

        for row in df.itertuples(index=True, name='Pandas'):
            if row.cold == 'cold': 
                if row.instance_id not in cold_times:
                    cold_times[row.instance_id] = 0
                else:
                    cold_times[row.instance_id] += 1
        return cold_times
    
    aws_count = find_cold_times(aws_pyramid_df)
    # print(aws_count,'\n')
    aws_cold_starts = len(aws_count)
    aws_cold_times = reduce(lambda x,y: x+y[1],[0]+list(aws_count.items()))
   
    open_count = find_cold_times(open_pyramid_df)
    open_cold_starts = len(open_count)
    open_cold_times = reduce(lambda x,y: x+y[1],[0]+list(open_count.items()))
    # print(open_count,'\n')
    azure_count = find_cold_times(azure_pyramid_df)
    azure_cold_starts = len(azure_count)
    azure_cold_times = reduce(lambda x,y: x+y[1],[0]+list(azure_count.items()))
    # print(azure_count,'\n')

    data = {'provider': ['aws_lambda','openfaas','azure_functions'],
            'cold_start': [aws_cold_starts,open_cold_starts,azure_cold_starts],
            'cold_times': [aws_cold_times,open_cold_times,azure_cold_times]}
    df = pd.DataFrame(data)

    config = {
        'x': 'provider',
        'y': 'cold_start',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('number of cold starts',12),
        'xlabel': ('Provider',12),
        'markers': ['o','s','v'],
        # 'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    
    gg.bar_plot(df, config,'Cold starts: load-scenario: pyramid',directory)
    config['y'] = 'cold_times'
    config['ylabel'] = ('number of cold times',12)
    gg.bar_plot(df, config,'Cold times: load scenario: pyramid',directory) 

    ###############################
    # growing-load-spike scenario #
    ###############################

    config = {
        'x': 'provider',
        'y': 'number',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('number of errors',12),
        'xlabel': ('Cloud Provider',12),
        'markers': ['o','s','v'],
        'hist': True,
        'kde': False,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    
    gg.bar_plot(joint_error_spike_df,config,'error by provider load-scenario: spikes',directory,18)

    aws = np.array(aws_spike_df['cold'].value_counts()).tolist()+['aws_lambda']
 
    openf = np.array(open_spike_df['cold'].value_counts()).tolist()+['openfaas']
   
    azure = np.array(azure_spike_df['cold'].value_counts()).tolist()+['azure_functions']
   
    zipped = list(zip(aws,openf,azure))
    data = {'provider': zipped[2], 'cold': zipped[1],'warm': zipped[0]}
    df = pd.DataFrame(data)

    config = {
        'x': 'provider',
        'y': 'cold',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    gg.bar_plot(df, config,'Cold times: load-scenario: spikes',directory)
    config['y'] = 'warm'
    gg.bar_plot(df, config,'Warm times: load-scenario :spikes',directory) 

    config = {
        'x': 'provider',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }


    
    gg.boxen_plot(joint_spike_df, config, 'Cold times distribution: spikes',directory)
    config['x'] = 'multi'
    gg.boxen_plot(joint_spike_df, config, 'Cold times distribution concurrent: spikes',directory)

    config = {
        'x': 'invocation_start',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('cold times',12),
        'markers': ['o','s','v'],
        'fir_reg': False,
        # 'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws': {'color':colors['light_gray']},
    }

    gg.lm_plot(aws_spike_df, config, 'AWS latency and invocation start: spikes', directory)
    gg.lm_plot(open_spike_df, config, 'OpenFaaS latency and invocation start: spikes', directory)
    gg.lm_plot(azure_pyramid_df, config, 'Azure latency and invocation start: spikes', directory)

    gg.lm_plot(joint_pyramid_df, config, 'latency and invocation start: spikes', directory)


    
    aws_count = find_cold_times(aws_spike_df)
    # print(aws_count,'\n')
    aws_cold_starts = len(aws_count)
    aws_cold_times = reduce(lambda x,y: x+y[1],[0]+list(aws_count.items()))
   
    open_count = find_cold_times(open_spike_df)
    open_cold_starts = len(open_count)
    open_cold_times = reduce(lambda x,y: x+y[1],[0]+list(open_count.items()))
    # print(open_count,'\n')
    azure_count = find_cold_times(azure_spike_df)
    azure_cold_starts = len(azure_count)
    azure_cold_times = reduce(lambda x,y: x+y[1],[0]+list(azure_count.items()))
    # print(azure_count,'\n')

    data = {'provider': ['aws_lambda','openfaas','azure_functions'],
            'cold_start': [aws_cold_starts,open_cold_starts,azure_cold_starts],
            'cold_times': [aws_cold_times,open_cold_times,azure_cold_times]}
    df = pd.DataFrame(data)

    config = {
        'x': 'provider',
        'y': 'cold_start',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('number of cold starts',12),
        'xlabel': ('Provider',12),
        'markers': ['o','s','v'],
        ''
        # 'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    
    gg.bar_plot(df, config,'Cold starts: load-scenario spikes',directory)
    config['y'] = 'cold_times'
    config['ylabel'] = ('number of cold times',12)
    gg.bar_plot(df, config,'Cold times: load-scenario spikes',directory)  

    








def throughput_graphs(directory:str, devmode:bool ):

    # metadata
    directory = 'Throughput'
    experiment_uuids = get_uuids('throughput-benchmarking') 
  
    # queries
    def query_by_provider(uuid, multi):
        return f"""SELECT throughput/100 as operations_milli, throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, 
            execution_start-invocation_start as latency, thread_id, if(numb_threads > 1,0,1) as multi, cl_provider as provider from Experiment e left join Invocation i on i.exp_id=e.uuid 
            where throughput != 0 and numb_threads {'> 1' if multi else '= 1'} and exp_id ='{uuid}';"""

    def monolith_by_provider(uuid,multi):
        return f"""select function_argument,process_time_matrix,running_time_matrix,monolith_result,(process_time_matrix/running_time_matrix)*100 as process_fraction, 
                execution_start-invocation_start as latency, thread_id, numb_threads, if(numb_threads > 1,0,1) as multi, cl_provider as provider from 
                (Monolith m left join Experiment e on m.exp_id=e.uuid) join Invocation i on m.invo_id=i.identifier 
                where numb_threads {'> 1' if multi else '= 1'} and m.exp_id ='{uuid}';"""
    
   
   
    # dataframes
    aws_invo_single_df = db.get_raw_query(query_by_provider(experiment_uuids['aws_lambda'], False)) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    azure_invo_single_df = db.get_raw_query(query_by_provider(experiment_uuids['azure_functions'], False)) if 'azure_functions' in experiment_uuids else np.DataFrame()
    open_invo_single_df = db.get_raw_query(query_by_provider(experiment_uuids['openfaas'], False)) if 'openfaas' in experiment_uuids else np.DataFrame()
    aws_invo_multi_df = db.get_raw_query(query_by_provider(experiment_uuids['aws_lambda'], True)) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    azure_invo_multi_df = db.get_raw_query(query_by_provider(experiment_uuids['azure_functions'], True)) if 'azure_functions' in experiment_uuids else np.DataFrame()
    open_invo_multi_df = db.get_raw_query(query_by_provider(experiment_uuids['openfaas'], True)) if 'openfaas' in experiment_uuids else np.DataFrame()
    joined_single_df = pd.concat([aws_invo_single_df,azure_invo_single_df,open_invo_single_df],ignore_index=True)
    joined_multi_df = pd.concat([aws_invo_multi_df,azure_invo_multi_df,open_invo_multi_df],ignore_index=True)
    all_invo_df = pd.concat([joined_single_df,joined_multi_df],ignore_index=True)
    
    # from monolith table
    aws_monolith_df = db.get_raw_query(monolith_by_provider(experiment_uuids['aws_lambda'], False)) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_monolith_df = db.get_raw_query(monolith_by_provider(experiment_uuids['azure_functions'], False)) if 'azure_functions' in experiment_uuids else np.DataFrame()
    azure_monolith_df = db.get_raw_query(monolith_by_provider(experiment_uuids['openfaas'], False)) if 'openfaas' in experiment_uuids else np.DataFrame()
    aws_monolith_multi_df = db.get_raw_query(monolith_by_provider(experiment_uuids['aws_lambda'], True)) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_monolith_multi_df = db.get_raw_query(monolith_by_provider(experiment_uuids['azure_functions'], True)) if 'azure_functions' in experiment_uuids else np.DataFrame()
    azure_monolith_multi_df = db.get_raw_query(monolith_by_provider(experiment_uuids['openfaas'], True)) if 'openfaas' in experiment_uuids else np.DataFrame()
    monolith_single_df = pd.concat([aws_monolith_df, azure_monolith_df,open_monolith_df],ignore_index=True)
    monolith_multi_df = pd.concat([aws_monolith_multi_df,azure_monolith_multi_df,open_monolith_multi_df],ignore_index=True)
    monolith_all_invo_df = pd.concat([monolith_single_df,monolith_multi_df],ignore_index=True)



    # Throughput time and operations perfomed in that time
    config = {
        'x': 'throughput_time',
        'y': 'operations_milli',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('operations (1000)',14),
        'xlabel': ('time in seconds',14),
        'markers': ['o','s','v'],
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
   
    # gg.lm_plot(joined_single_df,config,'Ops per sec :S  ',directory)
    # gg.line_plot(joined_single_df,config,'Ops per sec :S',directory)
  
    # gg.lm_plot(joined_multi_df,config,'Ops per sec :C',directory)
    # gg.line_plot(joined_multi_df,config,'Ops per sec :C',directory)
    # gg.lm_plot(all_invo_df,config,'Ops per sec :A',directory)
    # # for appendix
    # gg.lm_plot(pd.concat([aws_invo_single_df,aws_invo_multi_df]),config,'aws ops per sec :A',directory )
    # gg.lm_plot(pd.concat([open_invo_single_df,open_invo_multi_df]),config,'openfaas ops per sec :A',directory )
    # gg.lm_plot(pd.concat([azure_invo_single_df,azure_invo_multi_df]),config,'azure ops per sec :A',directory )

    # for appendix - no correlation found for latency
    copy_all_invo = all_invo_df.copy(deep=True)  
    indexNames = copy_all_invo[ copy_all_invo['latency'] > 10.0 ].index
    #  Delete these row indexes from dataFrame
    copy_all_invo.drop(indexNames , inplace=True)
    config['kind']='scatter'
    config['x_vars'] = ['operations_milli','throughput_process_time','process_fraction']
    config['y_vars'] = ['latency']
    # gg.pair_plot(copy_all_invo, config,'process_fraction__single',directory)

    config = {
        'x': 'throughput_time',
        'y': 'process_fraction',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('operations (1000)',14),
        'xlabel': ('time in seconds',14),
        'markers': ['o','s','v'],
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    # single
    # gg.bar_plot(joined_single_df,config,'process_fraction__single',directory)
    # # multi
    # gg.bar_plot(joined_multi_df, config,'process_fraction_multi',directory)
    # # all
    # gg.bar_plot(all_invo_df, config,'process_fraction_joined',directory)

    # config['x'] = 'provider'
    # # plots per provider
    # gg.violin_plot(joined_single_df,config,'process_fraction_single',directory)
    # # multi
    # gg.violin_plot(joined_multi_df, config,'process_fraction_multi',directory)
    # # all
    gg.violin_plot(all_invo_df, config,'process fraction all',directory)
    
    # --> Monolith plots <--

    directory += '/monolith'
    config = {
        'x': 'function_argument',
        'y': 'running_time_matrix',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'xlabel': ('size of matrix',14),
        'ylabel': ('running time in seconds',14),
        'markers': ['o','s','v'],
        'jitter':0.15,
        # 'height': 4,
        # 'aspect': 0.8,
    }

    # gg.lm_plot(monolith_all_invo_df,config,'lm Time for matrix calc :A',directory)
    # gg.line_plot(monolith_all_invo_df,config,'line Time for matrix calc :A',directory)
    # gg.swarm_plot(monolith_all_invo_df,config,'swarm Time for matrix calc :A',directory)
    
    config = {
        'x': 'provider',
        'y': 'number',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('number of errors',12),
        'xlabel': ('Cloud Provider',12),
        'markers': ['o','s','v'],
        'hist':True,
        'kde': False,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    # config['x']='multi'
    # config['strip'] = True
    # config['x_strip'] = 'multi'
    # config['y_strip'] = 'running_time_matrix'
    # config['bins'] = 30
    # gg.box_plot(pd.concat([aws_monolith_df,aws_monolith_multi_df]),config,'aws Time for matrix calc :A',directory)
    # gg.box_plot(pd.concat([open_monolith_df,open_monolith_multi_df]),config,'openfaas Time for matrix calc :A',directory)
    # gg.box_plot(pd.concat([azure_monolith_df,azure_monolith_multi_df]),config,'azure Time for matrix calc :A',directory)
    # gg.box_plot(monolith_all_invo_df,config,'Time for matrix calc :A',directory)

    config = {
        'x': 'function_argument',
        'y': 'process_fraction',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'xlabel': ('size of matrix',14),
        'ylabel': ('process time in seconds',14),
        'markers': ['o','s','v'],
        'jitter':0.15,
        # 'height': 4,
        # 'aspect': 0.8,
    }

    # gg.swarm_plot(monolith_all_invo_df,config,'swarm Time for matrix calc :A',directory)
    # gg.bar_plot(monolith_all_invo_df,config,'barTime for matrix calc :A',directory)
    # gg.scatter_plot(monolith_all_invo_df,config,'scatterfor matrix calc :A',directory)

    config = {
        'x': 'running_time_matrix',
        'y': 'process_fraction',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'xlabel': ('running time seconds',14),
        'ylabel': ('process time in seconds',14),
        'markers': ['o','s','v'],
        'jitter':0.15,
        # 'height': 4,
        # 'aspect': 0.8,
    }
    
    gg.scatter_plot(monolith_all_invo_df,config,'scatterfor matrix calc :A',directory)





    

    




# delete when done

def test(directory:str, dev_mode:bool):
    
 
    db = database(True)
    gg = GraphGenerater('report',dev_mode)

    hue_order = ['openfaas','aws_lambda','azure_functions']

    provider_color_dict = dict({'aws_lambda':'#ff8c00ff',
                        'azure_functions': '#ffd700ff',
                        'openfaas': '#2316deff',
                        })


    query_throughput = """SELECT floor(throughput/1000) as operations_milli,throughput_time,(throughput_process_time/throughput_time)*100 as process_fraction, 
                        cl_provider from (select name, cl_provider, total_time, uuid as experiment_uuid from Experiment where name = 'throughput-benchmarking') x 
                        left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 and throughput_time < 2.0 and floor(throughput/1000) < 1000 order by throughput_time;"""
  
    throughput_dataframe = db.get_raw_query(query_throughput)
    # print(throughput_dataframe.head(10).to_latex(index=False)) 
    # print(throughput_dataframe.head(10).to_html(index=False)) 

    # basic_throughput = throughput_dataframe.copy(deep=True)    

    # lineplot - throughput per second all providers
    config = {
        'x': 'throughput_time',
        'y': 'operations_milli',
        'hue': 'cl_provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('operations (100)',14),
        'xlabel': ('time in seconds',18),
        # 'markers': ['o','s','v'],
        # 'height': 3,
        # 'aspect':0.8,
        # 'kind': 'scatter',
        # 'x_jitter':0.25,
        # 'y_jitter': 0.25,
        # 'row':'cl_provider',
        # 'line_kws':{'color':'#191970ff'},
        # 'color':'purple'
    }
    # gg.joint_plot(throughput_dataframe,config,'jointplot',directory)
    list_query = """select execution_start-invocation_start as latency from Invocation where exp_id in (select uuid from Experiment where name='linear-invocation-nested' and cl_provider='aws_lambda')
    and execution_start-invocation_start > 0.5;"""
    res_list = db.get_raw_query(list_query,False)
    flatten = reduce(lambda x,y: x+y,res_list)
  
    # config['hist']=True 
    # config['kde']= False
    # config['bins'] = 30
    # config['height'] = 0.5
    # config.pop('x')
    # config['color']='#ff8c00ff'
    # gg.rug_plot(flatten,config,'rug plot',directory)
    # gg.dist_plot(flatten,config,'dist plot',directory)
    # gg.bar_plot(throughput_dataframe,config,'operations (1000) per second',directory)
    # config.pop('y')
    # gg.count_plot(throughput_dataframe,config,'operations (1000) per second',directory)
    
    # gg.line_plot(throughput_dataframe,config,'operations (1000) per second',directory,12)
    # config['col'] = 'cl_provider'
    # config['jitter'] = 0.25
    # config['aspect'] = 1.2
    # config['height'] = 3
    # config.pop('hue')
    # config['palette'] = 'bright' 
    # gg.cat_plot(throughput_dataframe,config,'cat plot',directory)
    
    # gg.violin_plot(throughput_dataframe,config,'Violin plot',directory)
    # config['y'] = 'process_fraction'
    # gg.strip_plot(throughput_dataframe,config,'strip plot',directory)
    gg.dynamic_multi_plot(throughput_dataframe,config,'line + scatter',directory,[lambda l: sns.lineplot(
                                                                                                        x=l[0],
                                                                                                        y=l[1],
                                                                                                        hue=l[2],
                                                                                                        style=None,
                                                                                                        palette=l[3],
                                                                                                        hue_order=l[4],
                                                                                                        data=l[5]),
                                                                                                lambda l: sns.scatterplot(
                                                                                                        x=l[0],
                                                                                                        y=l[1],
                                                                                                        hue=l[2],
                                                                                                        style=None,
                                                                                                        palette=l[3],
                                                                                                        hue_order=l[4],
                                                                                                        data=l[5],
                                                                                                )],12,)
                                                                                                
    
    gg.scatter_plot(throughput_dataframe,config,'scatterplot',directory,12)


 
    # swarmplot - process_fraction per throughput_time
    config = {
        'x': 'throughput_time',
        'y': 'process_fraction',
        'hue': 'cl_provider',
        'palette': provider_color_dict
    }
 
    # gg.swarm_plot(throughput_dataframe,config,'process fraction',directory)
    config['x'] = 'cl_provider'
    gg.box_plot(throughput_dataframe,config,'process fraction',directory)

    # 
    query_avg_process_fraction = """SELECT floor(throughput/1000) as operations_milli,throughput_time,throughput_process_time,
                                    avg((throughput_process_time/throughput_time)*100) as process_fraction, cl_provider from 
                                    (select name, cl_provider, total_time, uuid as experiment_uuid from Experiment where name = 'throughput-benchmarking') x 
                                    left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 group by throughput_time,cl_provider order by cl_provider;"""
    avg_process_fraction_df = db.get_raw_query(query_avg_process_fraction)


    config = {
        'x': 'throughput_time',
        'y': 'process_fraction',
        'hue': 'cl_provider',
        'palette': provider_color_dict
    }
  
    gg.lineplot_graph(avg_process_fraction_df, config, 'lineplot process fraction', directory)

    gg.relplot(avg_process_fraction_df, config, 'relplot process fraction', directory)
    





# Produce the graphs by calling chosen graph methos

for category in category_of_graphs:
    category()

  