import math
from tkinter import *
import requests
from tkinter import ttk
import time as timing
import datetime
"""
typical request is: http://192.168.4.1/update?maxtime=5000&delaytime=1000 - TO update
"""

def day():
    return str(datetime.date.today().isoformat())
def time():
    return str(datetime.datetime.now().time())

def startlogging():
    l=open('logs.txt','a')
    l.write('\n------------------------------------\n'+'START LOGGING at '+day()+' '+time())
def logging(logtext):
    l=open('logs.txt','a')
    l.write('\n'+time()+':'+logtext)

def parsefile(fromfile):
    logging('GOT PARSEFILE REQUEST:')
    with open('data.txt', 'r') as info:
        if fromfile:
            rawdata = info.read().split('\n')
        elif not(fromfile):
            logging('opened fiile data.txt and get current RAWDATA, which is:'+'\n'+str(rawdata))
            rawdata=rawdata.split('<br>')
            rawdata.pop()
        logging('after spliting RAWDATA by <br> or ; :'+'\n'+str(rawdata))
    time = []
    data = []
    for i in range (len(rawdata)):
        rawdata[i]=rawdata[i].split(';')
        time.append(rawdata[i][0])
        data.append(rawdata[i][1])
        logging('RAWDATA['+str(i)+']'+'\n'+str(rawdata[i]))
    logging('after parsing RAWDATA we get time:'+'\n'+str(time))
    logging('after parsing RAWDATA we get data:'+'\n'+str(data))
    return (data,time)

def swapoints(data):
    logging('GOT SWAP POINTS REQUEST IN MASSIVE:'+str(data))
    allelements = int(0)
    amountofelements = len(data)
    for i in range (amountofelements):
        allelements += float(data[i])
    avg = allelements/amountofelements
    points = []
    i=0
    for i in range (1,len(data)):
        if (float(data[i-1])<=avg) and (float(data[i])>avg):
            points.append(i)
    logging('found indexex of swappoints:'+str(points))
    return(points)

def minmaxarrays(data):

    def findmax(data):
        logging('GOT FINDMAXREQUST IN MASSIVE:'+str(data))
        min = float(data[0])
        max = float(data[0])
        for i in range (len(data)):
            if (float(data[i])) > max:
                max = float(data[i])
            if (float(data[i])) < min:
                min = float(data[i])
        logging('founded min= '+str(min)+'max= '+str(max))
        return(min,max)
    
    logging('GOT REQUEST TO FIND MIN/MAX IN WHOLE ARARAYS MASSIVE:'+str(data))
    start=0
    count=1
    minarray =[]
    maxarray =[]
    while (count !=4):
        end=swapoints(data)[count]
        minarray.append(findmax(data[start:end])[0])
        maxarray.append(findmax(data[start:end])[1])
        start=end
        count+=1
    logging('founded mins= '+str(minarray)+'maxs= '+str(maxarray))
    return(minarray,maxarray)

def getdecrement(data):
    logging('GOT DECREMENT FIND REQUEST OF'+str(data))
    a=minmaxarrays(data)[1][0]
    b=minmaxarrays(data)[1][1]
    v=minmaxarrays(data)[1][2]
    d=minmaxarrays(data)[0][0]
    g=minmaxarrays(data)[0][1]
    y1=abs(a-d)
    y2=abs(b-d)
    y3=abs(b-g)
    y4=abs(g-v)
    result = math.log(0.5*(y1/y3+y2/y4))
    logging('a='+str(a)+' b='+str(b)+' v='+str(v)+' g='+str(g)+' d='+str(d)+' y1='+str(y1)+' y2='+str(y2)+' y3='+str(y3)+' y4='+str(y4))
    return(result)

def interface():

    def ondata():
        data,time = parsefile(True)
        lbl.configure(text="Декримент="+str(getdecrement(data)))  

    def clicked():  
        mtime = format(value1.get())  
        dtime = format(value2.get())  
        logging('sent request for measuring with maxtime = '+mtime+' and delaytime='+dtime)
        requests.get('http://192.168.4.1/update?maxtime='+mtime+'&delaytime='+dtime)
        timing.sleep((int(mtime)//1000)+2)
        with open('data.txt', 'w') as file:
            file.write(requests.get('http://192.168.4.1/data').text)
        data,time = parsefile(False)
        lbl.configure(text="Декримент="+str(getdecrement(data)))  

    window = Tk()  
    window.title("Расчет декримента")  
    window.geometry('400x250')  

    lbl1 = Label(window, text="maxtime=", font=("Arial Bold", 10))  
    lbl1.grid(column=0, row=1)   
    
    lbl2 = Label(window, text="delaytime=", font=("Arial Bold", 10))  
    lbl2.grid(column=0, row=2)   

    value1 = Entry(window,width=10)  
    value1.grid(column=1, row=1)

    value2 = Entry(window,width=10)  
    value2.grid(column=1, row=2)

    lbl = Label(window, text="Декримент=", font=("Arial Bold", 10))  
    lbl.grid(column=0, row=3)   

    btn = Button(window, text="Расчет декримента", command=clicked)
    btn.grid(column=0, row=0)  
    
    btn1 = Button(window, text="Расчет декримента из data.txt", command=ondata)
    btn1.grid(column=1, row=0)  

    window.mainloop()

startlogging()

interface()
