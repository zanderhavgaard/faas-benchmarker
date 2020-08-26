import sys
import json
import time
from pprint import pprint
from mysql_interface import SQL_Interface as database
from graph_generater import GraphGenerater
import function_lib as lib
from datetime import datetime
from os.path import expanduser
import seaborn as sns

import pandas as pd 
import numpy as np

def througput_graphs(directory:str, dev_mode:bool):
    
 
    db = database(True)
    gg = GraphGenerater('report',dev_mode)

    hue_order = ['aws_lambda','openfaas','azure_functions']

    provider_color_dict = dict({'aws_lambda':'#ff8c00ff',
                        'azure_functions': '#ffd700ff',
                        'openfaas': '#2316deff',
                        })


    query_throughput = """SELECT floor(throughput/1000) as operations_milli,throughput_time,(throughput_process_time/throughput_time)*100 as process_fraction, 
                        cl_provider from (select name, cl_provider, total_time, uuid as experiment_uuid from Experiment where name = 'throughput-benchmarking') x 
                        left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 order by throughput_time;"""
  
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
        'xlabel': ('time in seconds',18)
    }
    list_query = """select execution_start-invocation_start as latency from Invocation where exp_id in (select uuid from Experiment where name='linear-invocation-nested' and cl_provider='aws_lambda')
    and execution_start-invocation_start > 0.5;"""
    res_list = db.get_raw_query(list_query,False)
    print('length',len(res_list))
    from functools import reduce
    flatten = reduce(lambda x,y: x+y,res_list)
    print('length',len(flatten))
    config['hist']=True 
    config['kde']= False
    config['bins'] = 30
    config['color']='#ff8c00ff'

    gg.dist_plot(flatten,config,'dist plot',directory)
    gg.bar_plot(throughput_dataframe,config,'operations (1000) per second',directory)
    # config.pop('y')
    # gg.count_plot(throughput_dataframe,config,'operations (1000) per second',directory)
    
    gg.lineplot_graph(throughput_dataframe,config,'operations (1000) per second',directory,12)
    # config['col'] = 'cl_provider'
    # config['jitter'] = 0.25
    # config['aspect'] = 1.2
    # config['height'] = 3
    # config.pop('hue')
    # config['palette'] = 'bright' 
    # gg.cat_plot(throughput_dataframe,config,'cat plot',directory)
    
    gg.violin_plot(throughput_dataframe,config,'Violin plot',directory)
    config['y'] = 'process_fraction'
    # gg.strip_plot(throughput_dataframe,config,'strip plot',directory)
    # gg.dynamic_multi_plot(throughput_dataframe,config,'line + scatter',directory,[lambda l: sns.lineplot(
                                                                                                #         x=l[0],
                                                                                                #         y=l[1],
                                                                                                #         hue=l[2],
                                                                                                #         style=None,
                                                                                                #         palette=l[3],
                                                                                                #         hue_order=l[4],
                                                                                                #         data=l[5]),
                                                                                                # lambda l: sns.scatterplot(
                                                                                                #         x=l[0],
                                                                                                #         y=l[1],
                                                                                                #         hue=l[2],
                                                                                                #         style=None,
                                                                                                #         palette=l[3],
                                                                                                #         hue_order=l[4],
                                                                                                #         data=l[5],
                                                                                                # )],12,)
                                                                                                
    
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
    


througput_graphs(directory='throughput',dev_mode=True)

  