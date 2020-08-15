
import time
import ntplib
from functools import reduce
from pprint import pprint
# from time import ctime
# import os
# import time
# ntp_overhead = 0.0


def res(s,idx,by3,l,iterations):
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
    from_by3 = list(map(lambda x: x-by3,local_list))
    print('index 0 from_by3',local_list[0])
    print('index 999 from by3',local_list[list_size-1])
    avg_from_by3 = reduce(lambda x,y: x+y,from_by3)/len(from_by3)
    print('avg_from_by3',avg_from_by3)
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
                )
            )
            overhead += time.time()-t1
        except Exception as e:
            print(str(e))
    avg_overhead = overhead/iterations
    print('avg_overhead',avg_overhead)
    by3 = reduce(lambda x,y: x+y,list(map(lambda x: x[3],l)))/len(l)
    print()

    res('total overhead',0,by3,l,iterations)
    res('start to time',1,by3,l,iterations)
    res('time to end',2,by3,l,iterations)

test(2)
test(3)
test(4)





# res('divided by 3',3)


    
#     start = time.time()
#     import ntplib
#     ntpc = ntplib.NTPClient()
#     retries = 0
#     overhead = time.time() - start
#     pools = ['cambrige1','cambridge2',...]
#     for adr in pools: 
#         while retries < 10:
#             retries += 1
#             try:
#                 t1 = time.time()
#                 ntp_response = ntpc.request(adr)
#                 t2 = time.time()
#                 res = ntp_response.tx_time - overhead - (t2-t1)/2
#                 # print('latency',(t2-t1)/2,( (t2+ntp_response.offset)-ntp_response.tx_time),'overhead',overhead)
#                 # print('offset test',ntp_response.offset,ntp_response.tx_time,t2,(t2-ntp_response.tx_time)) #-((t2-t1)/2))
#                 if retries < 3:
#                     raise ntplib.NTPException
#                 return (res,overhead+(t2-t1),ntp_response.offset,ntp_response.tx_time,start,(t2-t1)/2)
#                 # return (result,'tx_time',ntp_response.tx_time,'diff',ntp_response.tx_time-result,'offset',t1+ntp_response.offset,ntp_response.offset)
#             except ntplib.NTPException:
#                 print(f'no response from ntp request, trying again ...{retries}')
#                 overhead += time.time()-t1
#         retries = 0

#     return (start,overhead)

# for i in range(3):
#     res = test()
#     tt2 = time.time()
#     print('local times',tt2,res[4],'diff',(tt2-res[1])-res[4])
#     print('res times',res[0],tt2,'diff',res[0]-(tt2),'diff with offset',res[0]-((tt2)+res[2]),res[0]-((tt2)+(res[2]-res[5])))
#     print('offsets',res[1],'own offset',res[3]-res[0])
#     print(res)
#     print()
 
#     ntp_overhead += res[1]
#     print()
# print('ntp_overhead',ntp_overhead)
    # try:
    #     start = time.time()
    #     import ntplib
    #     f = time.time()
    #     client = ntplib.NTPClient()
    #     response = client.request('uk.pool.ntp.org')
    #     l = time.time()
    # except Exception as e:
    #     print('Could not sync with time server.')
    #     print(str(e))
    
    # print('testtime1',time.time())
    # try:
    #     os.system('date'+time.strftime('%m%d%H%M%Y.%S',time.localtime(response.tx_time)))
    # except Exception as e:
    #     print('error',str(e))
    # print('testtime2',time.time())
    # offset_calc = time.time()-start-(l-f)
    # new_start = start-offset_calc
    # print('start',start)
    # print('ntp_overhead',l-f)
    # print('offset_calc',offset_calc)
    # print('new_start',new_start)
    # print('offset',response.offset)
   
    # t1 = time()
    # local = time()
    # ntptime = client.request('uk.pool.ntp.org',version=3)
    # t2 = time()
   
    # pprint(ntptime.__dict__)
    # print()
    # print('ntp',ctime(ntptime.tx_time))
    # print('local',ctime(local))
    # print('diff',local-ntptime.tx_time)
    # print('offset',ntptime.offset)


    # print('t1 vs local',local-t1)
    # networking = (t2-t1) / 2
    # print('networking',networking)
    # print('diff tx ca',(ntptime.tx_time-networking)-t1)
    # print('diff orig ca',(ntptime.orig_time-networking)-t1)
    # print('diff recv ca',(ntptime.recv_time-networking)-t1)

    # print()
    # print('offset',ntptime.offset)
    # print('root_delay',ntptime.root_delay)

    # print('t1',t1)
    # print('tx',ntptime.tx_time)
    # print('orig',ntptime.orig_time)
    # print('recv_timestamp',ntptime.recv_timestamp)
    # print('t2',t2)
    
    # print('local',local)
    # print('ntp',ntptime.tx_time)
    # print('diff',local-ntptime.tx_time)

    # t_1 = time()
    # t_2 = time()
    # t_3 = time()
    # print(t_3-t_1)

    # print()
    # pprint(ntptime.__dict__)


