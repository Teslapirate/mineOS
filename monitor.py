#!/usr/bin/python

#Server status daemon for mineOS.
#Monitors server, sends restart upon crash
#Email notification upon down

__author__ = "Shaun McCarty"
__license__ = "GNU GPL v3.0"
__version__ = "0.1"
__email__ = "teslapirate@sentrygun.com"

import sys
import os
import argparse
import mineos
import time
import smtplib
import base64

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='monitor')
    parser.add_argument('a_servername', metavar='Server name')

    args = parser.parse_args()

    server_name = args.a_servername

    server = mineos.mc(server_name)
    pid = server.server_getpid()
    message = 'Your mineOS server ' + server_name + ' has gone offline due to '
    print 'Server monitor active'
    while server.status() == 'up': #keeps daemon up as long as server's running.
        time.sleep(30)
        print  '.'
    
    logfilename = 'hs_err_pid' + pid + '.log'
    logfile = os.path.join(mineos.mc().mineos_config['paths']['world_path'], server_name, logfilename)
    if os.access(logfile, os.R_OK): #java error file exists with matching pid#
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
        server.start()
    else:
        message = message + "manual shutdown and/or restart."

    print message
        
    #send email notification
    #needs vars: Email, SSL, server, port, login, pw
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