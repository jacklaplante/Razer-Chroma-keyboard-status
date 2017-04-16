import psutil
import time
import os

download_trend = [1,1,1,1,1,1,1,1,1,1]
upload_trend = [1,1,1,1,1,1,1,1,1,1]

# cd /sys/bus/hid/drivers/razerkbd/0003:1532:0220.0006
# echo -n -e "\x3\x0\x1\x0\x0\x0\xFF\xFF\x0" > matrix_custom_frame
# echo -n "1" > matrix_effect_custom
# mpstat | grep -A 5 "%idle" | tail -n 1 | awk -F " " '{print 100 - $13}'

def row0(kb):
    # get battery level as x out of 15 (15 keys on top row)
    level = round((psutil.sensors_battery()[0]/100)*15)
    values = [0,0,15,0,0,0]
    for i in range(15):
        if i <= level:
            values+=[0,0xff,0]
        else:
            values+=[0xff,0xff,0xff]
    kb.write(bytes(values))
    return

def row1(kb):
    # fuckin cpu bitch
    level = round((psutil.cpu_percent()/100)*15)
    values = [1,0,15,0,0,0]
    for i in range(15):
        if i <= level:
            values+=[0xff,0,0]
        else:
            values+=[0xff,0xff,0xff]
    kb.write(bytes(values))
    return

def row2(kb):
    # yup it's memory
    level = round((psutil.virtual_memory()[2]/100)*15)
    values = [2,0,15,0,0,0]
    for i in range(15):
        if i <= level:
            values+=[0xff,153,0]
        else:
            values+=[0xff,0xff,0xff]
    kb.write(bytes(values))
    return

def row3(kb):
    # network usage
    global download_trend
    global upload_trend

    # get average network download/upload over past 10 iterations
    download_sum = 0
    upload_sum = 0
    for i in range(10):
        download_sum+=download_trend[i]
        upload_sum+=upload_trend[i]
    download_avg = download_sum/10
    upload_avg = upload_sum/10
    download = psutil.net_io_counters()[1]
    upload = psutil.net_io_counters()[0]

    # update the trend
    download_trend = download_trend[1:10] + [download]
    upload_trend = upload_trend[1:10] + [upload]

    download_level = round(15*(download/(download_avg*2)))
    upload_level = round(15*(upload/(download_avg*2)))
    values = [3,0,15,0,0,0]
    for i in range(15):
        if i <= upload_level:
            values+=[0,0xff,0xff]
        elif i <= download_level:
            values+=[0,0,0xff]
        else:
            values+=[0xff,0xff,0xff]
    kb.write(bytes(values))
    return

def row4(kb):
    level = 0
    values = [4,0,15,0,0,0]
    for i in range(15):
        if i <= level:
            values+=[0xff,0xff,0xff]
        else:
            values+=[0xff,0xff,0xff]
    kb.write(bytes(values))
    return

def row5(kb):
    level = 0
    values = [5,0,15,0,0,0]
    for i in range(15):
        if i <= level:
            values+=[0xff,0xff,0xff]
        else:
            values+=[0xff,0xff,0xff]
    kb.write(bytes(values))
    return

def main():
    dev_path = '/sys/bus/hid/drivers/razerkbd/'
    #list of possible device paths (they may change so when it does add the new path to this list)
    devices = ['0003:1532:0220.0003', '0003:1532:0220.0006']
    for device in devices:
        if os.path.exists(dev_path+'/'+device+'/matrix_custom_frame'):
            break

    while True:
        with open(dev_path+'/'+device+'/matrix_custom_frame', 'wb') as kb:
            row0(kb)
            row1(kb)
            row2(kb)
            row3(kb)
            row4(kb)
            row5(kb)

            kb.close()
            open(dev_path+'/'+device+'/matrix_effect_custom', 'w').write("1")
        # wait 2 seconds to run again
        time.sleep(2)

if __name__ == '__main__':
    main()
