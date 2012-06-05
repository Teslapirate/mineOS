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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='statlog')
    parser.add_argument('a_pid', metavar='Process ID')
    parser.add_argument('a_servername', metavar='Server name')
    parser.add_argument('a_email', metavar='E-mail address')

    args = parser.parse_args()

    pid = args.a_pid
    server_name = args.a_servername
    email = args.a_email

    server = mineos.mc(server_name)
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
    sendmail_location = "/usr/sbin/sendmail" # sendmail location
    p = os.popen("%s -t" % "/usr/sbin/sendmail", "w")
    p.write("From: %s\n" % "servermonitor@sentrygun.com")
    p.write("To: %s\n" % email)
    p.write("Subject: %s\n" % (server_name + "has gone offline"))
    p.write("\n") # blank line separating headers from body
    p.write(message)
    status = p.close()
    if status != 0:
           print "Sendmail exit status", status