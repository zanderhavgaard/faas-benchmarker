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

dev_mode = eval(sys.argv[2]) if len(sys.argv) > 2 else False # TODO change dev_mode


db = database(True)
gg = GraphGenerater(name_of_report, dev_mode)

# meta coloring and order for produced graphs
hue_order = ['OpenFaaS','AWS Lambda','Azure Functions']

provider_color_dict = {'OpenFaaS': '#2316deff',
                    'AWS Lambda':'#ff8c00ff',
                    'Azure Functions': '#ffd700ff',
                    }
print('test',provider_color_dict['AWS Lambda'])
colors = {
    'light_gray': '#708090ff',
    'blue': '#191970ff'
}

# name sub-directories for the different categories by changing stringvalues in below list
# comment line out of graphs for that category is not wanted
category_of_graphs = [
    lambda : cold_start('cold_starts',dev_mode),
    lambda : function_lifetime('Function_lifetime', dev_mode),
    lambda : large_function('Large_function',dev_mode),
    lambda : throughput_graphs( 'Throughput', dev_mode),
    lambda : coldtimes_graphs('Coldtimes', dev_mode),
    # lambda : test( 'test', dev_mode),
]

# aux function for getting latest uuids from a experiment name
def get_uuids(experiment_name:str):
    return { x[0]: x[1] for x in db.get_latest_metadata_by_experiment(experiment_name) }



def cold_start(ldir:str, devmode):
    print('cold_start')
    # metadata
    directory = ldir
    experiment_uuids = get_uuids('simple-cold-function')

    def get_table_all(uuid):
        return f"""select cl_provider as provider, name, minutes, seconds, granularity, threads as requests, benchmark, cold, final 
                from Coldstart c left join Experiment e on e.uuid=c.exp_id where e.uuid = '{uuid}';"""
       
    def get_table_final(uuid):
        return f"""select cl_provider as provider, name, minutes, seconds, granularity, threads as requests, benchmark, cold from Coldstart c 
                left join Experiment e on e.uuid=c.exp_id where final = True and e.uuid = '{uuid}';"""
       
    
    # coldstart-identifier                 
    # coldstart-identifier-nested          
    # simple-cold-function                 
    # simple-cold-function-nested          
    # simple-cold-function-threaded-twelve

    aws_final_df = db.get_raw_query(get_table_final(experiment_uuids['aws_lambda']))
    aws_all_df = db.get_raw_query(get_table_all(experiment_uuids['aws_lambda']))
    open_final_df = db.get_raw_query(get_table_final(experiment_uuids['openfaas']))
    open_all_df = db.get_raw_query(get_table_all(experiment_uuids['openfaas']))
    azure_final_df = db.get_raw_query(get_table_final(experiment_uuids['azure_functions']))
    azure_all_df = db.get_raw_query(get_table_all(experiment_uuids['azure_functions']))
    experiment_uuids = get_uuids('simple-cold-function-nested')
    print('NESTED', experiment_uuids)
    aws_final_nested_df = db.get_raw_query(get_table_final(experiment_uuids['aws_lambda']))
    aws_all_nested_df = db.get_raw_query(get_table_all(experiment_uuids['aws_lambda']))
    open_final_nested_df = db.get_raw_query(get_table_final(experiment_uuids['openfaas']))
    open_all_nested_df = db.get_raw_query(get_table_all(experiment_uuids['openfaas']))
    azure_final_nested_df = db.get_raw_query(get_table_final(experiment_uuids['azure_functions']))
    azure_all_nested_df = db.get_raw_query(get_table_all(experiment_uuids['azure_functions']))
    experiment_uuids = get_uuids('simple-cold-function-threaded-twelve')
    print('CONCURRENT', experiment_uuids)
    aws_final_con_df = db.get_raw_query(get_table_final(experiment_uuids['aws_lambda']))
    aws_all_con_df = db.get_raw_query(get_table_all(experiment_uuids['aws_lambda']))
    open_final_con_df = db.get_raw_query(get_table_final(experiment_uuids['openfaas']))
    open_all_con_df = db.get_raw_query(get_table_all(experiment_uuids['openfaas']))
    azure_final_con_df = db.get_raw_query(get_table_final(experiment_uuids['azure_functions']))
    azure_all_con_df = db.get_raw_query(get_table_all(experiment_uuids['azure_functions']))
    experiment_uuids = get_uuids('coldstart-identifier')
    print('identifier', experiment_uuids)
    aws_final_iden_df = db.get_raw_query(get_table_final(experiment_uuids['aws_lambda']))
    aws_all_iden_df = db.get_raw_query(get_table_all(experiment_uuids['aws_lambda']))
    open_final_iden_df = db.get_raw_query(get_table_final(experiment_uuids['openfaas']))
    open_all_iden_df = db.get_raw_query(get_table_all(experiment_uuids['openfaas']))
    azure_final_iden_df = db.get_raw_query(get_table_final(experiment_uuids['azure_functions']))
    azure_all_iden_df = db.get_raw_query(get_table_all(experiment_uuids['azure_functions']))
    experiment_uuids = get_uuids('coldstart-identifier-nested')
    print('identifier', experiment_uuids)
    aws_final_iden_nest_df = db.get_raw_query(get_table_final(experiment_uuids['aws_lambda']))
    aws_all_iden_nest_df = db.get_raw_query(get_table_all(experiment_uuids['aws_lambda']))
    open_final_iden_nest_df = db.get_raw_query(get_table_final(experiment_uuids['openfaas']))
    open_all_iden_nest_df = db.get_raw_query(get_table_all(experiment_uuids['openfaas']))
    azure_final_iden_nest_df = db.get_raw_query(get_table_final(experiment_uuids['azure_functions']))
    azure_all_iden_nest_df = db.get_raw_query(get_table_all(experiment_uuids['azure_functions']))


    all_finals = [aws_final_df,
                        open_final_df,
                        azure_final_df,
                        aws_final_nested_df,
                        open_final_nested_df,
                        azure_final_nested_df,
                        aws_final_con_df,
                        open_final_con_df,
                        azure_final_con_df, 
                        aws_final_iden_df,
                        open_final_iden_df,
                        azure_final_iden_df,
                        aws_final_iden_nest_df,
                        open_final_iden_nest_df,
                        azure_final_iden_nest_df]
    


    table_df = pd.concat(all_finals)

   
    gg.save_table(table_df,'All final results',directory)
    gg.save_table(aws_all_df,'AWS all simple-cold-function',directory)
    gg.save_table(open_all_df,'OpenFaaS all simple-cold-function',directory)
    gg.save_table(azure_all_df,'Azure all simple-cold-function',directory)
    gg.save_table(aws_all_nested_df,'AWS all simple-cold-function-nested',directory)
    gg.save_table(open_all_nested_df,'OpenFaaS all simple-cold-function-nested',directory)
    gg.save_table(azure_all_nested_df,'Azure all simple-cold-function-nested',directory)
    gg.save_table(aws_all_con_df,'AWS all simple-cold-function-concurrent',directory)
    gg.save_table(open_all_con_df,'OpenFaaS all simple-cold-function-concurrent',directory)
    gg.save_table(azure_all_con_df,'Azure all simple-cold-function-concurrent',directory)
    gg.save_table(aws_all_iden_df,'AWS all coldstart-identifier',directory)
    gg.save_table(open_all_iden_df,'OpenFaaS all coldstart-identifier',directory)
    gg.save_table(azure_all_iden_df,'Azure all coldstart-identifier',directory)
    gg.save_table(aws_all_iden_nest_df,'AWS all coldstart-identifier-nested',directory)
    gg.save_table(open_all_iden_nest_df,'OpenFaaS all coldstart-identifier-nested',directory)
    gg.save_table(azure_all_iden_nest_df,'Azure all coldstart-identifier-nested',directory)
    


def function_lifetime(ldir:str, devmode:bool):
    print('function_lifetime')
    # metadata
    directory = ldir
    experiment_uuids = get_uuids('function-lifetime')
   

    def get_table(uuid):
        return f"""select cl_provider as provider,instance_identifier as first_invoked, orig_identifier as last_invoked, hours,minutes,seconds,sleep_time,reclaimed 
        from Function_lifetime f left join Experiment e on e.uuid=f.exp_id where e.uuid = '{uuid}';"""
       
    
    def get_invocations(uuid):
        return f"""select execution_start-invocation_start as latency, instance_identifier, cl_provider as provider from Invocation i 
            left join Experiment e on e.uuid=i.exp_id where e.uuid = '{uuid}';"""
       


    aws_table_df = db.get_raw_query(get_table(experiment_uuids['aws_lambda']))
    open_table_df = db.get_raw_query(get_table(experiment_uuids['openfaas']))
    azure_table_df = db.get_raw_query(get_table(experiment_uuids['azure_functions']))
    table_df = pd.concat([aws_table_df,open_table_df,azure_table_df])
   
    aws_df = db.get_raw_query(get_invocations(experiment_uuids['aws_lambda']))
    open_df = db.get_raw_query(get_invocations(experiment_uuids['openfaas']))
    open_df.loc[(open_df.latency > 5.0),'latency']= 5.0
    azure_df = db.get_raw_query(get_invocations(experiment_uuids['azure_functions']))
    joint_df = pd.concat([aws_df,open_df,azure_df])

    config = {
        'x': 'provider',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'markers': ['o','s','v'],
        'ylabel': ('Latency in seconds',12),
        'xlabel': ('Cloud provider',12),
        'markers': ['o','s','v'],
        'jitter': 0.25,
        'alpha': 0.5,
        # 'height': 4,
        # 'aspect': 0.8,
    }

    gg.strip_plot(joint_df, config, 'Latency by provider', directory)

    gg.save_table(table_df, 'Function lifetime values',directory)



def large_function(ldir:str, devmode:bool):

    # metadata
    directory = ldir
    experiment_uuids = get_uuids('coldtime-large-functions ')
   
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

    # copy_aws_linear_df = aws_linear_df.copy(deep=True)  
    # copy_aws_linear_df['instance_id'] = copy_aws_linear_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    # gg.strip_plot(copy_aws_linear_df,config,' AWS latency per function_instance',directory)


       
    config = {
        'x': 'function_name',
        'y': 'latency',
        'hue': 'provider',
        'ylabel': ('Latency in seconds',12),
        'xlabel': ('Function name',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        'x_strip': 'instance_id',
        'y_strip': 'latency',
        'strip': True,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

#  NOT INT USE ----------------------------------------------------------
    # aws_avg = aws_df.groupby('function_name')['latency'].sum()
    # avg_reg = aws_avg[0]/len(aws_df)
    # avg_mono = aws_avg[1]/len(aws_df)
    # warm_times = aws_df.map(lambda x: x.latency if x.latency < )

    # aws_mono = aws_df[aws_df['function_name'== 'monolith'] ]
    # aws_mono = aws_df.loc[aws_df['function_name'] == 'monolith'] 
    # aws_reg = aws_df.loc[aws_df['function_name'] != 'monolith'] 
    # aws_mono_cutoff = aws_mono *2 
    # aws_avg_mono = aws_mono.sum().latency / len(aws_mono)
    # print(aws_avg_mono)
    # aws_avg_reg = aws_reg.sum().latency / len(aws_reg)
    # aws_mono_warm = aws_mono.loc[aws_mono['latency'] < aws_mono_cutoff] 
    # pprint(aws_mono)


    # aws_reg = aws_df.query("function_name == monolith")
    # pprint(aws_reg)
    # aws_reg = aws_df.query(f"function_name == monolith")['*']


    # open_avg = open_df.groupby('function_name')['latency'].sum()
    # azure_avg = azure_df.groupby('function_name')['latency'].sum()
    # data = {'provider': ['AWS Lambda','OpenFaaS','Azure Functions'],
    #         'reg_func': [aws_avg[0]/len(aws_df),open_avg[0]/len(open_df),azure_avg[0]/len(azure_df)],
    #         'monolith':  [aws_avg[1]/len(aws_df),open_avg[1]/len(open_df),azure_avg[1]/len(azure_df)]}
    # df = pd.DataFrame(data)
    # pprint(df)
    
    # aws_sum = aws_df.sum()
    # avg_latency = aws_df.sum().latency / len(aws_df)
    # print(avg_latency)
    # pprint(aws_sum)
# ------------------------------------------------------------------------------------------
    config['palette'] = {'AWS Lambda':provider_color_dict['AWS Lambda']}
    config['hue_order'] = ['AWS Lambda']
    config['markers'] = ['s']
    gg.swarm_plot(aws_df, config, 'AWS latency small vs large function',directory)
    config['palette'] = {'OpenFaaS':provider_color_dict['OpenFaaS']}
    config['hue_order'] = ['OpenFaaS']
    config['markers'] = ['o']
    gg.swarm_plot(open_df, config, 'OpenFaaS latency small vs large function',directory)
    config['palette'] = {'Azure Functions':provider_color_dict['Azure Functions']}
    config['hue_order'] = ['Azure Functions']
    config['markers'] = ['v']
    gg.swarm_plot(azure_df, config, 'Azure latency small vs large function',directory)

    config = {
        'x': 'throughput',
        'y': 'latency',
        'hue': 'function_name',
        'palette': {'function1': 'red', 'monolith': 'black'},
        'ylabel': ('Latency in seconds',12),
        'xlabel': ('Number of operations',12),
        'markers': ['s'],
        'jitter': 0.1,
        'x_strip': 'instance_id',
        'y_strip': 'latency',
        'strip': True,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    aws_throughput = aws_df.loc[aws_df['throughput'] != 0.0] 
    gg.line_plot(aws_throughput,config,'AWS throughput by function type',directory)
    open_throughput = open_df.loc[open_df['throughput'] != 0.0] 
    gg.line_plot(open_throughput,config,'OpenFaaS throughput by function type',directory)
    azure_throughput = azure_df.loc[azure_df['throughput'] != 0.0] 
    gg.line_plot(azure_throughput,config,'Azure throughput by function type',directory)






def coldtimes_graphs(ldir:str, devmode:bool):
    print('coldtimes_graphs')

    # metadata
    directory = ldir
    experiment_uuids = get_uuids('linear-invocation')

    # queries
    def query_by_provider(uuid, level:int,pyramid:bool=False):
        return f"""select latency,instance_id, total, thread_id,  multi, provider, if(latency > if(coldtime > 1,{2.0 if pyramid else 1.0},coldtime), 'cold','warm') as cold, invocation_start  
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
    print('pyramid',experiment_uuids)
    aws_pyramid_df = db.get_raw_query(query_by_provider(experiment_uuids['aws_lambda'], 0, True)) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_pyramid_df = db.get_raw_query(query_by_provider(experiment_uuids['openfaas'], 0, True)) if 'openfaas' in experiment_uuids else np.DataFrame()
    azure_pyramid_df = db.get_raw_query(query_by_provider(experiment_uuids['azure_functions'], 0, True)) if 'azure_functions' in experiment_uuids else np.DataFrame()
    joint_pyramid_df = pd.concat([aws_pyramid_df,open_pyramid_df,azure_pyramid_df],ignore_index=True)
    aws_error_df = db.get_raw_query(error_by_provider(experiment_uuids['aws_lambda'])) if 'aws_lambda' in experiment_uuids else np.DataFrame()
    open_error_df = db.get_raw_query(error_by_provider(experiment_uuids['openfaas'])) if 'openfaas' in experiment_uuids else np.DataFrame()
    azure_error_df = db.get_raw_query(error_by_provider(experiment_uuids['azure_functions'])) if 'azure_functions' in experiment_uuids else np.DataFrame()
    joint_error_df = pd.concat([aws_error_df,open_error_df,azure_error_df],ignore_index=True)
    experiment_uuids = get_uuids('growing-load-spikes')

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
    #     'y': 'latency',
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

    # plist = np.array(aws_pyramid_df.loc[ : , 'invocation_start' ]).tolist()
    # gg.dist_plot(plist,config,'pyramid invocation starts',directory)

    

    config = {
        'x': 'cold',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': ['AWS Lambda'],
        'ylabel': ('latency in seconds',12),
        'xlabel': ('Cold time vs warm time',12),
        'markers': ['s'],
        'jitter': 0.1,
        'x_strip': 'cold',
        'y_strip': 'latency',
        'strip': True,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    gg.box_plot(aws_linear_df, config, 'AWS cold times distribution',directory)
    config['hue_order'] = ['OpenFaaS']
    config['markers'] = ['o']
    gg.box_plot(open_linear_df, config, 'OpenFaaS cold times distribution',directory)
    config['hue_order'] = ['Azure Functions']
    config['markers'] = ['v']
    gg.box_plot(azure_linear_df, config, 'Azure cold times distribution',directory)

    config = {
        'x': 'invocation_start',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('Latency in seconds',12),
        'xlabel': ('Invocation start (unix time)',12),
        'markers': ['o','s','v'],
        'alpha': 0.5,
        # 'jitter': 0.25,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    
    gg.scatter_plot(joint_linear_df,config,'Latency relative to invocation start:appendix',directory,18)
    joint_linear_df.loc[(joint_linear_df.latency > 10.0 ),'latency']=8.00
    gg.scatter_plot(joint_linear_df,config,'Latency relative to invocation start',directory,18)

    open_linear_df.loc[(open_linear_df.latency > 10.0 ),'latency']=3.00
    config['hue_order'] = ['AWS Lambda']
    config['palette'] = {'AWS Lambda':provider_color_dict['AWS Lambda']}
    config['markers'] = ['s']
    gg.scatter_plot(aws_linear_df,config,' AWS latency relative to invocation start',directory,18)
    config['hue_order'] = ['OpenFaaS']
    config['palette'] = {'OpenFaaS':provider_color_dict['OpenFaaS']}
    config['markers'] = ['o']
    gg.scatter_plot(open_linear_df,config,' OpenFaaS latency relative to invocation start',directory,18)
    config['hue_order'] = ['Azure Functions']
    config['palette'] = {'Azure Functions':provider_color_dict['Azure Functions']}
    config['markers'] = ['v']
    gg.scatter_plot(azure_linear_df,config,'Azure latency relative to invocation start',directory,18)


    config = {
        'x': 'provider',
        'y': 'cold',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('Number of cold times',12),
        'xlabel': ('Cloud provider',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        'alpha': 0.5,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    aws = np.array(aws_linear_df['cold'].value_counts()).tolist()+['AWS Lambda']
    openf = np.array(open_linear_df['cold'].value_counts()).tolist()+['OpenFaaS']
    azure = np.array(azure_linear_df['cold'].value_counts()).tolist()+['Azure Functions']
    zipped = list(zip(aws,openf,azure))
    data = {'provider': zipped[2], 'cold': zipped[1],'warm': zipped[0]}
    df = pd.DataFrame(data)
 

    gg.bar_plot(df, config,'Cold times by provider: linear-invocation',directory)
    config['y'] = 'warm'
    config['ylabel'] = ('Number of warm times',12)
    gg.bar_plot(df, config,'Warm times by provider: linear-invocation',directory)   

    config['x'] = 'instance_id'
    config['y'] = 'latency'
    config['xlabel'] = ('Function instance',12)
    config['ylabel'] = ('Latency in seconds',12)
    
    copy_aws_linear_df = aws_linear_df.copy(deep=True)  
    copy_aws_linear_df['instance_id'] = copy_aws_linear_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    gg.strip_plot(copy_aws_linear_df,config,' AWS latency per function instance',directory)

    copy_open_linear_df = open_linear_df.copy(deep=True)  
    copy_open_linear_df['instance_id'] = copy_open_linear_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    gg.strip_plot(copy_open_linear_df,config,'OpenFaaS latency per function instance',directory)


    copy_azure_linear_df = azure_linear_df.copy(deep=True)  
    copy_azure_linear_df['instance_id'] = copy_azure_linear_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    gg.strip_plot(copy_azure_linear_df,config,'Azure latency per function instance',directory)

    ###################################
    # --> linear-invocation-nested <--#
    ###################################

    directory = directory.split('/')[0]
    directory += '/nested'

    config = {
    'x': 'cold',
    'y': 'latency',
    'hue': 'provider',
    'palette': provider_color_dict,
    'ylabel': ('cold times',12),
    'markers': ['s'],
    'jitter': 0.1,
    'x_strip': 'cold',
    'y_strip': 'latency',
    'strip': True,
    # 'height': 4,
    # 'aspect': 0.8,
    'line_kws':{'color':colors['light_gray']},
    }

    config['hue_order'] = ['AWS Lambda']
    config['palette'] = {'AWS Lambda':provider_color_dict['AWS Lambda']}
    config['markers'] = ['s']
    gg.box_plot(aws_linear_nested_df, config, 'AWS cold times distribution: nested',directory)
    config['hue_order'] = ['OpenFaaS']
    config['palette'] = {'OpenFaaS':provider_color_dict['OpenFaaS']}
    config['markers'] = ['o']
    gg.box_plot(open_linear_nested_df, config, 'OpenFaaS cold times distribution: nested',directory)
    config['hue_order'] = ['Azure Functions']
    config['palette'] = {'Azure Functions':provider_color_dict['Azure Functions']}
    config['markers'] = ['v']
    gg.box_plot(azure_linear_nested_df, config, 'Azure cold times distribution: nested',directory)

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
    
    gg.scatter_plot(joint_linear_nested_df,config,'appendix:latency relative to invocation start: nested',directory,18)
    joint_linear_nested_df.loc[(joint_linear_nested_df.latency > 8.0 ),'latency']=8.00
    gg.scatter_plot(joint_linear_nested_df,config,'latency relative to invocation start: nested',directory,18)


    open_linear_nested_df.loc[(open_linear_nested_df.latency > 3.0 ),'latency']=3.00
    config['hue_order'] = ['AWS Lambda']
    config['palette'] = {'AWS Lambda':provider_color_dict['AWS Lambda']}
    config['markers'] = ['s']
    gg.scatter_plot(aws_linear_nested_df,config,' AWS latency relative to invocation start: nested',directory,18)
    config['hue_order'] = ['OpenFaaS']
    config['palette'] = {'OpenFaaS':provider_color_dict['OpenFaaS']}
    config['markers'] = ['o']
    gg.scatter_plot(open_linear_nested_df,config,' OpenFaaS latency relative to invocation start: nested',directory,18)
    config['hue_order'] = ['Azure Functions']
    config['palette'] = {'Azure Functions':provider_color_dict['Azure Functions']}
    config['markers'] = ['v']
    gg.scatter_plot(azure_linear_nested_df,config,'Azure latency relative to invocation start: nested',directory,18)


    config = {
        'x': 'provider',
        'y': 'cold',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('Number of cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        'alpha': 0.5,
      
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }


    aws = np.array(aws_linear_nested_df['cold'].value_counts()).tolist()+['AWS Lambda']
    openf = np.array(open_linear_nested_df['cold'].value_counts()).tolist()+['OpenFaaS']
    azure = np.array(azure_linear_nested_df['cold'].value_counts()).tolist()+['Azure Functions']
    zipped = list(zip(aws,openf,azure))
    data = {'provider': zipped[2], 'cold': zipped[1],'warm': zipped[0]}
    df = pd.DataFrame(data)
   
 

    gg.bar_plot(df, config,'Cold times: linear-invocation: nested',directory)
    config['y'] = 'warm'
    config['ylabel'] = ('Number of warm times',12)
    gg.bar_plot(df, config,'Warm times: linear-invocation: nested',directory)   

    config['x'] = 'instance_id'
    config['y'] = 'latency'
    config['xlabel'] = ('Function id',12)
    config['ylabel'] = ('Latency in seconds',12)
    
    copy_aws_linear_nested_df = aws_linear_nested_df.copy(deep=True)  
    copy_aws_linear_nested_df['instance_id'] = copy_aws_linear_nested_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    config['hue_order'] = ['AWS Lambda']
    config['palette'] = {'AWS Lambda':provider_color_dict['AWS Lambda']}
    config['markers'] = ['s']
    gg.strip_plot(copy_aws_linear_nested_df,config,' AWS latency per function_instance: nested',directory)

    copy_open_linear_nested_df = open_linear_nested_df.copy(deep=True)  
    open_linear_nested_df['instance_id'] = copy_open_linear_nested_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    config['hue_order'] = ['OpenFaaS']
    config['palette'] = {'OpenFaaS':provider_color_dict['OpenFaaS']}
    config['markers'] = ['o']
    gg.strip_plot(copy_open_linear_nested_df,config,'OpenFaaS latency per function_instance: nested',directory)


    copy_azure_linear_nested_df = azure_linear_nested_df.copy(deep=True)  
    copy_azure_linear_nested_df['instance_id'] = copy_azure_linear_nested_df.instance_id.map(lambda x: int(abs(int(hash(x)))/10000000000000000))
    config['hue_order'] = ['Azure Functions']
    config['palette'] = {'Azure Functions':provider_color_dict['Azure Functions']}
    config['markers'] = ['v']
    gg.strip_plot(copy_azure_linear_nested_df,config,'Azure latency per function_instance: nested',directory)

#########################
# --> load-scenario <-- #
#########################

    directory = directory.split('/')[0]
    directory += '/pyramid'

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

    aws = np.array(aws_pyramid_df['cold'].value_counts()).tolist()+['AWS Lambda']
    openf = np.array(open_pyramid_df['cold'].value_counts()).tolist()+['OpenFaaS']
    azure = np.array(azure_pyramid_df['cold'].value_counts()).tolist()+['Azure Functions']
    zipped = list(zip(aws,openf,azure))
    data = {'provider': zipped[2], 'cold': zipped[1],'warm': zipped[0]}
    df = pd.DataFrame(data)
   

    config = {
        'x': 'provider',
        'y': 'cold',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('number of cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    gg.bar_plot(df, config,'Cold times: load-scenario: pyramid',directory)
    config['y'] = 'warm'
    config['ylabel'] = ('number of warm times',12)
    gg.bar_plot(df, config,'Warm times: load-scenario: pyramid',directory) 

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
    gg.boxen_plot(joint_pyramid_df, config, 'Cold times concurrent vs sequential: pyramid',directory)

    config = {
        'x': 'invocation_start',
        'y': 'latency',
        'ylabel': ('Latency in seconds',12),
        'xlabel': ('Invocation start time',12),
        'fit_reg': False,
        # 'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    config['hue_order'] = ['AWS Lambda']
    config['palette'] = {'AWS Lambda':provider_color_dict['AWS Lambda']}
    config['markers'] = ['s']
    gg.lm_plot(aws_pyramid_df, config, 'AWS latency: pyramid', directory)
    config['hue_order'] = ['OpenFaaS']
    config['palette'] = {'OpenFaaS':provider_color_dict['OpenFaaS']}
    config['markers'] = ['o']
    gg.lm_plot(open_pyramid_df, config, 'OpenFaaS latency: pyramid', directory)
    config['hue_order'] = ['Azure Functions']
    config['palette'] = {'Azure Functions':provider_color_dict['Azure Functions']}
    config['markers'] = ['v']
    gg.lm_plot(azure_pyramid_df, config, 'Azure latency: pyramid', directory)
   

    config = {
        'x': 'invocation_start',
        'y': 'latency',
        'ylabel': ('Latency in seconds',12),
        'xlabel': ('Invocation start time',12),
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'markers': ['o','s','v'],
        # 'hist':True,
        # 'kde': False,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    gg.lm_plot(joint_pyramid_df, config, 'Latency by provider: pyramid', directory)



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

    data = {'provider': ['AWS Lambda','OpenFaaS','Azure Functions'],
            'cold_start': [aws_cold_starts,open_cold_starts,azure_cold_starts],
            'cold_times': [aws_cold_times,open_cold_times,azure_cold_times]}
    df = pd.DataFrame(data)

    config = {
        'x': 'provider',
        'y': 'cold_start',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('Number of cold starts',12),
        'xlabel': ('Provider',12),
        'markers': ['o','s','v'],
        # 'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    
    gg.bar_plot(df, config,'Cold starts: load-scenario-pyramid',directory)
    config['y'] = 'cold_times'
    config['ylabel'] = ('Number of cold times',12)
    gg.bar_plot(df, config,'Cold times: load scenario-pyramid',directory) 

    ###############################
    # growing-load-spike scenario #
    ###############################

    directory = directory.split('/')[0]
    directory += '/spikes'
   

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
    
    gg.bar_plot(joint_error_spike_df,config,'Error by provider for load-scenario: spikes',directory,18)

    aws = np.array(aws_spike_df['cold'].value_counts()).tolist()+['Aws Lambda']
    openf = np.array(open_spike_df['cold'].value_counts()).tolist()+['OpenFaaS']
    azure = np.array(azure_spike_df['cold'].value_counts()).tolist()+['Azure Functions']
    zipped = list(zip(aws,openf,azure))
    data = {'provider': zipped[2], 'cold': zipped[1],'warm': zipped[0]}
    df = pd.DataFrame(data)
   

    config = {
        'x': 'provider',
        'y': 'cold',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('number of cold times',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    gg.bar_plot(df, config,'Cold times: load-scenario: spikes',directory)
    config['y'] = 'warm'
    config['ylabel'] = ('number of warm times',12)
    gg.bar_plot(df, config,'Warm times: load-scenario: spikes',directory) 

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
    gg.boxen_plot(joint_spike_df, config, 'Cold times concurrent vs sequential: spikes',directory)

    config = {
        'x': 'invocation_start',
        'y': 'latency',
        'ylabel': ('Latency in seconds',12),
        'xlabel': ('Invocation start time',12),
        'fit_reg': False,
        # 'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }

    config['hue_order'] = ['AWS Lambda']
    config['palette'] = {'AWS Lambda':provider_color_dict['AWS Lambda']}
    config['markers'] = ['s']
    gg.lm_plot(aws_spike_df, config, 'AWS latency: spikes', directory)
    config['hue_order'] = ['OpenFaaS']
    config['palette'] = {'OpenFaaS':provider_color_dict['OpenFaaS']}
    config['markers'] = ['o']
    gg.lm_plot(open_spike_df, config, 'OpenFaaS latency: spikes', directory)
    config['hue_order'] = ['Azure Functions']
    config['palette'] = {'Azure Functions':provider_color_dict['Azure Functions']}
    config['markers'] = ['v']
    gg.lm_plot(azure_spike_df, config, 'Azure latency: spikes', directory)
    config['hue_order'] = hue_order
    config['palette'] = provider_color_dict
    

    config = {
        'x': 'invocation_start',
        'y': 'latency',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('Latency in seconds',12),
        'xlabel': ('Invocation start time',12),
        'markers': ['o','s','v'],
        'jitter': 0.1,
        'fit_reg': False,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    gg.lm_plot(joint_spike_df, config, 'Latency by provider: spikes', directory)



    def find_cold_times(df):

        cold_times = {}

        for row in df.itertuples(index=True, name='Pandas'):
            if row.cold == 'cold': 
                if row.instance_id not in cold_times:
                    cold_times[row.instance_id] = 0
                else:
                    cold_times[row.instance_id] += 1
        return cold_times
    
    aws_count = find_cold_times(aws_spike_df)
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

    data = {'provider': ['AWS Lambda','OpenFaaS','Azure Functions'],
            'cold_start': [aws_cold_starts,open_cold_starts,azure_cold_starts],
            'cold_times': [aws_cold_times,open_cold_times,azure_cold_times]}
    df = pd.DataFrame(data)

    config = {
        'x': 'provider',
        'y': 'cold_start',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('Number of cold starts',12),
        'xlabel': ('Provider',12),
        'markers': ['o','s','v'],
        # 'jitter': 0.1,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    
    gg.bar_plot(df, config,'Cold starts: load-scenario-spikes',directory)
    config['y'] = 'cold_times'
    config['ylabel'] = ('Number of cold times',12)
    gg.bar_plot(df, config,'Cold times: load scenario-spikes',directory) 

    






def throughput_graphs(directory:str, devmode:bool ):
    print('throughput_graphs')
    # metadata
    directory = 'Throughput'
    experiment_uuids = get_uuids('throughput-benchmarking') 
  
    # queries
    def query_by_provider(uuid, multi):
        return f"""SELECT throughput/1000 as operations_milli, throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, 
            execution_start-invocation_start as latency, thread_id, if(numb_threads > 1,1,0) as multi, cl_provider as provider from Experiment e left join Invocation i on i.exp_id=e.uuid 
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
        'ylabel': ('operations (1000)',12),
        'xlabel': ('time in seconds',12),
        'markers': ['o','s','v'],
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
   
    gg.lm_plot(joined_single_df,config,'Ops per second: sequential  ',directory)
    gg.line_plot(joined_single_df,config,'Ops per second: sequential',directory)
  
    gg.lm_plot(joined_multi_df,config,'Ops per second: concurrent',directory)
    gg.line_plot(joined_multi_df,config,'Ops per second: concurrent',directory)
    gg.lm_plot(all_invo_df,config,'Ops per second: all',directory)
    
    # for appendix
    config['hue_order'] = ['AWS Lambda']
    config['palette'] = {'AWS Lambda':provider_color_dict['AWS Lambda']}
    config['markers'] = ['s']
    gg.lm_plot(pd.concat([aws_invo_single_df,aws_invo_multi_df]),config,'AWS ops per second: all',directory )
    config['hue_order'] = ['OpenFaaS']
    config['palette'] = {'OpenFaaS':provider_color_dict['OpenFaaS']}
    config['markers'] = ['o']
    gg.lm_plot(pd.concat([open_invo_single_df,open_invo_multi_df]),config,'OpenFaaS ops per second: all',directory )
    config['hue_order'] = ['Azure Functions']
    config['palette'] = {'Azure Functions':provider_color_dict['Azure Functions']}
    config['markers'] = ['v']
    gg.lm_plot(pd.concat([azure_invo_single_df,azure_invo_multi_df]),config,'Azure ops per second: all',directory )

    config['x'] = 'latency'
    config['hue_order'] = hue_order
    config['palette'] = provider_color_dict
    config['markers'] = ['o','s','v']

    gg.lm_plot(joined_single_df,config,'Ops per second mapped to latency: sequential  ',directory)
    gg.lm_plot(joined_multi_df,config,'Ops per second mapped to latency: concurrent',directory)
    gg.lm_plot(all_invo_df,config,'Ops per second mapped to latency: all',directory)
    gg.lm_plot(pd.concat([aws_invo_single_df,aws_invo_multi_df]),config,'AWS ops per second mapped to latency: all',directory)
    gg.lm_plot(pd.concat([open_invo_single_df,open_invo_multi_df]),config,'OpenFaaS ops per second mapped to latency: all',directory)
    gg.lm_plot(pd.concat([azure_invo_single_df,azure_invo_multi_df]),config,'Azure ops per second mapped to latency: all',directory)

    # for appendix - no correlation found for latency
    copy_all_invo = all_invo_df.copy(deep=True)  
    indexNames = copy_all_invo[ copy_all_invo['latency'] > 10.0 ].index
    #  Delete these row indexes from dataFrame
    copy_all_invo.drop(indexNames , inplace=True)
    config['kind']='scatter'
    config['x_vars'] = ['operations_milli','throughput_process_time','process_fraction']
    config['y_vars'] = ['latency']
    gg.pair_plot(copy_all_invo, config,'Process fraction: sequential',directory)

    config = {
        'x': 'throughput_time',
        'y': 'process_fraction',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('Percentage of time in CPU ',12),
        'xlabel': ('Time in seconds',12),
        'markers': ['o','s','v'],
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    # single
    gg.bar_plot(joined_single_df,config,'Process fraction: sequential',directory)
    # multi
    gg.bar_plot(joined_multi_df, config,'Process fraction: concurrent',directory)
    # all
    gg.bar_plot(all_invo_df, config,'Process fraction: all',directory)

    config['x'] = 'provider'
    # plots per provider
    gg.violin_plot(joined_single_df,config,'Process fraction by provider: sequential',directory)
    # multi
    gg.violin_plot(joined_multi_df, config,'Process fraction: concurrent',directory)
    # all
    gg.violin_plot(all_invo_df, config,'Process fraction: all',directory)
    
    # --> Monolith plots <--

    directory += '/monolith'
    config = {
        'x': 'function_argument',
        'y': 'running_time_matrix',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'xlabel': ('Size of matrix',12),
        'ylabel': ('Running time in seconds',12),
        'markers': ['o','s','v'],
        'jitter':0.15,
        # 'height': 4,
        # 'aspect': 0.8,
    }

    gg.lm_plot(monolith_all_invo_df,config,'Time for matrix calculation: all',directory)
    gg.line_plot(monolith_all_invo_df,config,'Time for matrix calculation: all',directory)
    gg.swarm_plot(monolith_all_invo_df,config,'Time for matrix calculation: all',directory)
    
    config = {
        'x': 'multi',
        'y': 'running_time_matrix',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'ylabel': ('Time in seconds',12),
        'xlabel': ('Sequential vs concurrent',12),
        'markers': ['o','s','v'],
        'hist':True,
        'kde': False,
        # 'height': 4,
        # 'aspect': 0.8,
        'line_kws':{'color':colors['light_gray']},
    }
    # config['x']='multi'
    config['strip'] = True
    config['x_strip'] = 'multi'
    config['y_strip'] = 'running_time_matrix'
    config['bins'] = 30

    config['hue_order'] = ['AWS Lambda']
    config['palette'] = {'AWS Lambda':provider_color_dict['AWS Lambda']}
    config['markers'] = ['s']
    gg.box_plot(pd.concat([aws_monolith_df,aws_monolith_multi_df]),config,'AWS Time for matrix calc: all',directory)
    config['hue_order'] = ['OpenFaaS']
    config['palette'] = {'OpenFaaS':provider_color_dict['OpenFaaS']}
    config['markers'] = ['o']
    gg.box_plot(pd.concat([open_monolith_df,open_monolith_multi_df]),config,'OpenFaaS Time for matrix calc: all',directory)
    config['hue_order'] = ['Azure Functions']
    config['palette'] = {'Azure Functions':provider_color_dict['Azure Functions']}
    config['markers'] = ['s']
    gg.box_plot(pd.concat([azure_monolith_df,azure_monolith_multi_df]),config,'azure Time for matrix calc: all',directory)
    config['hue_order'] = hue_order
    config['palette'] = provider_color_dict
    config['markers'] = ['o','s','v']
    gg.box_plot(monolith_all_invo_df,config,'Time for matrix calc for all providers',directory)

    config = {
        'x': 'function_argument',
        'y': 'process_fraction',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'xlabel': ('Size of matrix',12),
        'ylabel': ('Process time in seconds',12),
        'markers': ['o','s','v'],
        'jitter':0.15,
        # 'height': 4,
        # 'aspect': 0.8,
    }

    gg.swarm_plot(monolith_all_invo_df,config,'Process fraction by function argument: all',directory)
    gg.bar_plot(monolith_all_invo_df,config,'Process fraction by function argument: all',directory)
    gg.scatter_plot(monolith_all_invo_df,config,'Process fraction by function argument: all',directory)

    config = {
        'x': 'running_time_matrix',
        'y': 'process_fraction',
        'hue': 'provider',
        'palette': provider_color_dict,
        'hue_order': hue_order,
        'xlabel': ('Running time seconds',14),
        'ylabel': ('Process time in seconds',14),
        'markers': ['o','s','v'],
        'jitter':0.15,
        # 'height': 4,
        # 'aspect': 0.8,
    }
    
    gg.scatter_plot(monolith_all_invo_df,config,'Matrix calculation: all',directory)





    

    




# delete when done

def test(directory:str, dev_mode:bool):
    
 
    db = database(True)
    gg = GraphGenerater('report',dev_mode)

    hue_order = ['OpenFaaS','AWS Lambda','Azure Functions']

    provider_color_dict = dict({'AWS Lambda':'#ff8c00ff',
                        'Azure Functions': '#ffd700ff',
                        'OpenFaaS': '#2316deff',
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

  