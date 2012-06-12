#!/usr/bin/python

#Server monitor and statistics logging script made for mineOS.

__author__ = "Shaun McCarty"
__license__ = "GNU GPL v3.0"
__version__ = "0.4"
__email__ = "teslapirate@sentrygun.com"

import sys
import argparse
import subprocess
import logging
import time
import smtplib
import base64
import os

#Python will freak the heck out if you try to import mineos 
#from anywhere other than the mc_path. :(
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

import mineos

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='statlog')
    parser.add_argument('a_servername', metavar='Server Name')

    args = parser.parse_args()

    server_name = args.a_servername

#Check server every x seconds.
#Can change fixed delay for responsiveness,
#BUT NUMBER MUST MAKE 60%ping_delay == 0 !!!!
#Otherwise stat logging will never fire!!
    ping_delay = 30
    error = 'none'

    try:
        instance = mineos.mc(server_name)
        pid = instance.server_getpid()
        port = instance.server_config['minecraft']['port']
        delay = int(instance.server_config['custom']['stats_delay']) * 60
        print 'Server monitor enabled.'
    except Exception as x:
        sys.exit('Daemon failed to start: ' + str(x))

    if delay < 60 or 60%ping_delay > 0:
        print 'Stat logging delay is less than 60 seconds or ping_delay is invalid value, disabling.'
        stat_enable = False
    else:
        print 'Stat logging enabled.'
        stat_enable = True

    if pid > 0:
        if stat_enable:
            logfile = '/home/mc/servers/' + server_name + '/' + 'mc-' + server_name + '.csv'
            FORMAT='%(asctime)s %(message)s'
            logging.basicConfig(filename=logfile,level=logging.DEBUG,format=FORMAT)
            delay_count = 0
        while instance.status() == 'up': #Keeps monitor up as long as server's running.
            if stat_enable:
                delay_count = delay_count + ping_delay
                if delay_count == delay:
                    try:
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
                        delay_count = 0
                    except Exception as x:
                        error = x
                        print 'Stat logging encountered an error and is disabled until restart: ' + error
                        stat_enable = False
            time.sleep(ping_delay)
    else:
        sys.exit('Invalid pid encountered! Server not running?')
        
#Uncomment the following line to insert a line of 0 use upon server shutdown or abnormal termination
#            logging.info('%s %s %s','0','0','0','0')

#On server down

#Uncomment this line for testing/development to prevent email spam.
#    sys.exit('Temporary exit point.')
    message = 'Your mineOS server ' + server_name + ' has gone offline due to '

    logfilename = 'hs_err_pid' + pid + '.log'
    logfile = os.path.join(mineos.mc().mineos_config['paths']['world_path'], server_name, logfilename)
#Check if server crashed or not.
    if os.access(logfile, os.R_OK): #java error file exists with matching pid
        print 'logfile found.'
        message = message + 'server crash. Java crash log is included below, server will attempt to restart.\n<hr>\n'
        try:
            errorlog = open(logfile, mode='r')
            log_contents = errorlog.read()
        except:
            log_contents = 'There was an error reading the logfile. Please check ' + logfile + ' for details.'
        finally:
            errorlog.close()
        message = message + log_contents
        instance.start()
    else:
        message = message + "manual shutdown and/or restart."

    if error != 'none':
        message = message + '\n' + 'Additionally, stat collection encountered an error and was shut down prematurely: ' + error
        
    print message
        
#Send email notification
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    sender = mineos.mc().mineos_config['email']['em_sendfrom']
    receivers = ','.join(mineos.mc().mineos_config['email']['em_sendto'].split(','))

    msg = MIMEMultipart()
    msg["Subject"] = "mineOS Server Monitor Notification"
    msg["From"] = 'mineOS Server Monitor <' + sender + '>'
    msg["To"] = receivers
    body = MIMEText(message)
    msg.attach(body)

    mailserver = mineos.mc().mineos_config['email']['em_server']
    mailport = mineos.mc().mineos_config['email']['em_port']
#SSL and login management
    try:
        if mineos.mc().mineos_config['email']['em_type'] == 'normal':
            smtpObj = smtplib.SMTP(mailserver, mailport)
        elif mineos.mc().mineos_config['email']['em_type'] == 'ssl':
            smtpObj = smtplib.SMTP_SSL(mailserver, mailport)
        if mineos.mc().mineos_config['email']['em_login'] != "none":
            smtpObj.login(mineos.mc().mineos_config['email']['em_login'], base64.b64decode(mineos.mc().mineos_config['email']['em_pw']))
        smtpObj.sendmail(sender, receivers, msg.as_string() )
        smtpObj.quit()
        print "Successfully sent email"
    except Exception as x:
        print "Error: unable to send email - "
        print x
