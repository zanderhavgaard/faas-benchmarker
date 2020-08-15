
import time
import ntplib
from functools import reduce
from pprint import pprint
# from time import ctime
# import os
# import time
# ntp_overhead = 0.0


def res(s,idx,avg_divider,l,iterations):
    list_size = len(l)

    print(s,'list size',list_size)
    local_list = list(map(lambda x: x[idx],l))
    local_list.sort()
 
    print('index 0',local_list[0])
    print('index 999',local_list[list_size-1])
    avg_network_overhead = reduce(lambda x,y: x+y,local_list)/list_size
    print('avg',avg_network_overhead)
    print('mean',local_list[int(len(l)/2)])
    new_avg_network_overhead = reduce(lambda x,y: x+y,local_list[int(iterations*0.1):int(iterations*0.9)])/list_size
    print(f'avg adjusted {int(iterations*0.8)}',new_avg_network_overhead)
    from_avg_divider = list(map(lambda x: x-avg_divider,local_list))
    print('index 0 from_avg_divider',from_avg_divider[0])
    print('index 999 from avg_divider',from_avg_divider[len(from_avg_divider)-1])
    avg_from_from_avg_divider = reduce(lambda x,y: x+y,from_avg_divider)/len(from_avg_divider)
    print('avg_from_from_avg_divider',avg_from_from_avg_divider)
    print()

def test(divider):
    print('testing with',divider)
    l = []
    iterations = 1000
    ntpc = ntplib.NTPClient()
    overhead = 0.0
    
    for i in range(iterations):
        try:
            t1 = time.time()
            ntp_response = ntpc.request('ntp0.cam.ac.uk')
            t2 = time.time()

            l.append(
                (t2-t1,
                ntp_response.tx_time-t1,
                t2-ntp_response.tx_time,
                (t2-t1)/divider,
                ntp_response.offset,
                )
            )
            overhead += time.time()-t1
        except Exception as e:
            print(str(e))
    avg_overhead = overhead/iterations
    print('avg_overhead',avg_overhead)
    avg_divider = reduce(lambda x,y: x+y,list(map(lambda x: x[3],l)))/len(l)
    print()

    res('total overhead',0,avg_divider,l,iterations)
    res('start to time',1,avg_divider,l,iterations)
    res('time to end',2,avg_divider,l,iterations)
    res('offset',3,avg_divider,l,iterations)
  

test(2)
test(3)
test(4)







