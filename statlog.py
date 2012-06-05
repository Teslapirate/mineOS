#!/usr/bin/python

#Statistics logging script made for mineOS.

__author__ = "Shaun McCarty"
__license__ = "GNU GPL v3.0"
__version__ = "0.4"
__email__ = "teslapirate@sentrygun.com"

import sys
import argparse
import subprocess
import logging
import time

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='statlog')
    parser.add_argument('a_pid', metavar='Process ID')
    parser.add_argument('a_delay', metavar='Polling delay')
    parser.add_argument('a_port', metavar='Port')

    args = parser.parse_args()

    pid = args.a_pid
    delay = int(args.a_delay)
    port = args.a_port
    if delay < 60:
        sys.exit('Stat logging delay is less than 60 seconds, disabling')
    
    if pid > 0 and delay > 59:
        getppid = subprocess.Popen(['ps','-p',pid,'-o','ppid='],stdout=subprocess.PIPE)
        (ppid,perr) = getppid.communicate()
        ppid = ppid.strip()
        time.sleep(10)
        getpname = subprocess.Popen(['ps','-p',ppid,'-o','cmd='],stdout=subprocess.PIPE)
        (pname,perr) = getpname.communicate()
        pname = pname.split(' ')
        if not pname[2].startswith('mc-'):
            sys.exit('Logging failed to start: non-Minecraft process!')
        try:
            logfile = '/home/mc/servers/' + pname[2].replace('mc-','',1) + '/' + pname[2] + '.csv'
            FORMAT='%(asctime)s %(message)s'
            logging.basicConfig(filename=logfile,level=logging.DEBUG,format=FORMAT)
#Needed to give pout a length :)
            pout = 'hooray'
            while len(pout) > 0:
                checkproc_process = subprocess.Popen(['ps','-p',pid,'-o','vsz=','-o','rss='],stdout=subprocess.PIPE)
                (pout,serr) = checkproc_process.communicate()
                proclist=pout.split('\n')
                checktop = subprocess.Popen(['top','-p',pid,'-b','-n','1'],stdout=subprocess.PIPE)
                (tout,serr) = checktop.communicate()
                toplist=tout.split('\n')
                waitdata = toplist[2].split()
                waitp = waitdata[5].rstrip('%wa,')
                cpudata = toplist[7].split()
#Cheaper way of getting # of connected players
                checknet = subprocess.Popen(['netstat', '--protocol=inet'],stdout=subprocess.PIPE)
                (nout,nerr) = checknet.communicate()
                netlist = nout.split('\n')
                netcount = 0
                for x in netlist:
                    if port in x:
                        netcount = netcount+1
                logging.info('%s %s %s %s %s', cpudata[8],proclist[0],proclist[1],netcount,waitp)
                print('%s %s %s %s %s') % (cpudata[8],proclist[0],proclist[1],netcount,waitp)
                time.sleep(delay)
        except Exception as x:
#Uncomment the following line to insert a line of 0 use upon server shutdown or abnormal termination
#            logging.info('%s %s %s','0','0','0','0')
            sys.exit('Server down, logging disabled')
    else:
        sys.exit('Logging failed to start!')
