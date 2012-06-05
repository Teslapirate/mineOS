#!/usr/bin/python
"""A python script web-management interface to manage minecraft servers
   Designed for use with MineOS: http://minecraft.codeemo.com
"""

__author__ = "William Dizon"
__license__ = "GNU GPL v3.0"
__version__ = "0.4.11b"
__email__ = "wdchromium@gmail.com"

print "Content-Type: text/html"
print

import sys, cgi, cgitb, os
import mineos
import subprocess


cgitb.enable()

def cgi_to_dict(fieldStorage):
    params = {}
    for key in fieldStorage.keys():
        params[key] = fieldStorage[key].value
    return params

def display_about():
    print '''
    <p>MineOS is a Linux distribution designed for the sole purpose of hosting Minecraft worlds.
    It comes complete with web-admin interface, SSH interaction, and SCP capability for easy filesystem access.<p>

    <p>MineOS is created and maintained by
    William Dizon - <a href="mailto:wdchromium@gmail.com">wdchromium@gmail.com</a></p>
    
    <p>First edition of MineOS CRUX made public on July 28, 2011.</p>
    
    <p>MineOS home page: <a href="http://minecraft.codeemo.com/">http://minecraft.codeemo.com/</a></p>
    <p>This Linux distribution is designed from CRUX Linux 2.7. <br>
    MineOS CRUX / MineOS2 licensed as GNU GPL v3.0;<br>
    please cite accordingly and contact me if you have any questions or concerns on usage/derivatives.</p>

    <p>A copy of the GNU GPL can be found on the disc/install: <br>
    /root/LICENSE or online at <br>
    <a href="http://www.gnu.org/licenses/gpl-3.0.txt">http://www.gnu.org/licenses/gpl-3.0.txt</a></p>

    <p>Minecraft is copyright 2009-2011 Mojang AB.</p>

    <p>As per Markus Persson's request from Minecraft's website,
    this Linux distro does not contain ANY Minecraft files.
    The scripts are, however, designed to download/update
    files directly from the source: <a href="http://minecraft.net">http://minecraft.net</a></p>

    <p>These terms can be seen at: <a href="http://minecraft.net/copyright.jsp">http://minecraft.net/copyright.jsp</a></p>
    '''

def display_setup():
    print '''
    <script type="text/javascript">
        $('#savesetup').click(function(event){
            event.preventDefault();
            $.post("cgi-bin/server.py", { command: "act",
                                      action: "savesetup",
                                      server: 'none',
                                      arg01: $('#type').val(),
                                      arg02: $('#server').val(),
                                      arg03: $('#port').val(),
                                      arg04: $('#login').val(),
                                      arg05: $('#pw').val(),
                                      arg06: $('#sendto').val() },
            function(data){ $('#main').html(data); });
    });
    </script>'''

    print '<table><tr>'
    print '<td><h2>mineOS Setup</h2></td>'
    print '</tr></table>'
    print '''
        <form id="setup" name="setup">
        <table><tr>
            <td><h4>Email configuration</h4></td>
        </tr><tr>
            <td colspan="1"><label for="mode">Mode</label></td>
            <td colspan="2">
                <select id="switch" name="type">
    '''
#Can add additional mail server types if necessary.
    for item in ['ssl','normal']:    
        if mineos.mc().mineos_config['email']['server'] == item:
            print '<option SELECTED>%s</option>' % item
        else:
            print '<option>%s</option>' % item
    print '''
                </select>
            </td>
    </tr><tr>
            <td colspan="1"><label for="server">E-mail server</label></td>
            <td colspan="2"><input type="text" size="60" name="server" id="server" value="%s" /></td>
        </tr><tr>
            <td colspan="1"><label for="port">Port #</label></td>
            <td colspan="2"><input type="text" size="60" name="port" id="port" value="%s" /></td>
        </tr><tr>
            <td colspan="1"><label for="login">Login</label></td>
            <td colspan="2"><input type="text" size="60" name="login" id="login" value="%s" /></td>
        </tr><tr>
            <td colspan="1"><label for="pw">Password</label></td>
            <td colspan="2"><input type="password" size="60" name="pw" id="pw" value="********" /></td>
        </tr><tr>
            <td colspan="1"><label for="sendto">Recipient(s)*</label></td>
            <td colspan="2"><input type="text" size="60" name="sendto" id="sendto" value="%s" /></td>
        </tr>
        </table>
        *Separate recipients with a comma.<br>
        <a href="#" id="savesetup" class="actionbutton">Save config</a>

        ''' % (mineos.mc().mineos_config['email']['server'], 
                    mineos.mc().mineos_config['email']['port'],
                    mineos.mc().mineos_config['email']['login'],
                    mineos.mc().mineos_config['email']['sendto'])
    
def display_macros(server_name):
    def load_macros(instance):
        selects = []
        for x in ['01','02','03','04','05','06','07','08','09','10']:
            name = instance.server_config['macros']['macro' + x]
            selects.append('<tr><td colspan="2"><label for="macro%s">Macro %s:</label></td><td colspan="2"><input type="text" id="macro%s" size="70" value="%s" /></td></tr>' % (x, x, x, name))
        return ' '.join(selects)
        
    print '''
    <script type="text/javascript">
        $('.display').one("click", (function(event){
            event.preventDefault();
            $.post("cgi-bin/server.py", { command: "display",
                                      server: $('#switch').val(),
                                      page: "macros" },
            function(data){ $('#main').html(data); });
        }));
        $('#savemacros').click(function(event){
            event.preventDefault();
            $.post("cgi-bin/server.py", { command: "act",
                                      action: "savemacros",
                                      server: $('#servername').val(),
                                      arg01: $('#macro01').val(),
                                      arg02: $('#macro02').val(),
                                      arg03: $('#macro03').val(),
                                      arg04: $('#macro04').val(),
                                      arg05: $('#macro05').val(),
                                      arg06: $('#macro06').val(),
                                      arg07: $('#macro07').val(),
                                      arg08: $('#macro08').val(),
                                      arg09: $('#macro09').val(),
                                      arg10: $('#macro10').val() },
            function(data){ $('#main').html(data); });
    });
    </script>'''
    currentserver = mineos.mc(server_name)
    print 'Input macros here. May be as long as you need. Separate different commands with a comma.'
    print '<a href="#" class="display actionbutton">Display</a>'
    print '<select id="switch" name="server">'
    for server, port, status in mineos.mc.ports_reserved():
        if status in ['up', 'down', 'foreign', 'unclean']:
            if server == server_name:
                print '<option SELECTED>%s</option>' % server
            else:
                print '<option>%s</option>' % server
    print '</select>'
    if currentserver.status() in ['up', 'down', 'foreign', 'unclean']:
        print '''
            <form id="macroform">
                <input name="command" type="hidden" value="act">
                <input name="action" type="hidden" value="command">
                <input name="servername" id="servername" type="hidden" value="%s">
                <table>
                    %s
                    <tr> 
                        <td colspan="4"><a href="#" id="savemacros" class="actionbutton">Save macros</a></td>
                    </tr>
                </table>
            </form>''' % (server_name, load_macros(currentserver))

def listusers(userlist):
    selects = []
    selects.append('<option value="none" SELECTED>                    </option>')
    for x in userlist:
        selects.append('<option value="%s">%s</option>' % (x, x))
    return ' '.join(selects)

            
def display_lists(page, message):
    def listdump(filename):
        try:
            list_contents = open(filename, mode='r')
            newlist = list_contents.read()
            newlist = newlist.split()
        except:
            list_contents = []
            list_contents = open(configfile, mode='w')
            print '%s not found, generating.' % filename
            newlist = []
        finally:
            list_contents.close()
        return newlist

    print '''
    <script type="text/javascript">
    $('#list_add').click(function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "act",
                                      action: "list_add",
                                      server: "None",
                                      list_name: $('#listname').val(),
                                      value: $('#playername').val(),
                                      page: $('#pagename').val() },
         function(data){ $('#main').html(data); });
    });
    $('#list_remove').click(function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "act",
                                      action: "list_remove",
                                      server: "None",
                                      list_name: $('#listname').val(),
                                      value: $('#playername2').val(),
                                      page: $('#pagename').val() },
         function(data){ $('#main').html(data); });
    });

    $('.opslist').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "display",
                                      server: "None",
                                      page: 'opslist' },
         function(data){ $('#main').html(data); });
    }));
    $('.whitelist').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "display",
                                      server: "None",
                                      page: 'whitelist' },
         function(data){ $('#main').html(data); });
    }));
    $('.banlist').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "display",
                                      server: "None",
                                      page: 'banlist' },
         function(data){ $('#main').html(data); });
    }));
    $('.ipbans').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "display",
                                      server: "None",
                                      page: 'ipbans' },
         function(data){ $('#main').html(data); });
    }));
    $('.syncall').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "act",
                                      action: "synclists",
                                      server: "None",
                                      page: 'lists' },
         function(data){ $('#main').html(data); });
    }));
    </script>
    '''

    print '<h3>List Management'
    if page == 'opslist':
        print '- Manage Operator list'
        configfile = os.path.join(mineos.mc().mc_path, 'lists', 'ops.txt')
    elif page == 'whitelist':
        print '- Manage Whitelist'
        configfile = os.path.join(mineos.mc().mc_path, 'lists', 'white-list.txt')
    elif page == 'banlist':
        print '- Manage Ban list'
        configfile = os.path.join(mineos.mc().mc_path, 'lists', 'banned-players.txt')
    elif page == 'ipbans':
        print '- Manage IP Ban list'
        configfile = os.path.join(mineos.mc().mc_path, 'lists', 'banned-ips.txt')

    print '</h3>'
    print '<pre>'
    print '<a href="#" class="opslist smallcaps">%s</a>%s' % ('Manage ops list', '{:<8}'.format('&nbsp')),
    print '<a href="#" class="whitelist smallcaps">%s</a>%s' % ('Manage whitelist', '{:<8}'.format('&nbsp')),
    print '<a href="#" class="banlist smallcaps">%s</a>%s' % ('Manage banlist', '{:<8}'.format('&nbsp')),
    print '<a href="#" class="ipbans smallcaps">%s</a>%s' % ('Manage IP bans', '{:<8}'.format('&nbsp')),
    print '<br><br><a href="#" class="syncall smallcaps">%s</a>%s' % ('Sync all servers', '{:<8}'.format('&nbsp')),
    print '<br><span>%s</span>' % (message)
    print '</pre>'
    print '<hr>'

    if page in ['opslist', 'whitelist', 'banlist', 'ipbans']:
        newlist = listdump(configfile)
        print '''
        <form id="listform">
            <input name="command" type="hidden" value="act">
            <input id="listname" type="hidden" value="%s">
            <input id="pagename" type="hidden" value="%s">
            <table>
                <tr> 
                    <td colspan="1"><label for="command">User name:</label></td>
                    <td colspan="1"><input type="text" id="playername" size="20" value="" /></td>
                    <td colspan="1"><a href="#" id="list_add" class="actionbutton">Add user</a></td>
                </tr>
                <tr> 
                    <td colspan="1"><label for="command">Select user:</label></td>
                    <td colspan="1"><select name="playername2" id="playername2" tabindex="6">
                        %s
                    </select></td>
                    <td colspan="1"><a href="#" id="list_remove" class="actionbutton">Remove user/IP</a></td>
                </tr>
            </table>
        </form>''' % (configfile, page, listusers(newlist))
        print '<textarea id="list_contents" cols="60" rows="8" readonly="readonly">'
        for x in newlist:
            print x
        print '</textarea>'

def list_edit(listfile, action, value):
    def sendcmd(listfile, action, value, server):
        instance = mineos.mc(server)
        if 'white-list.txt' in listfile:
            if action == 'add':
                instance.command('whitelist add ' + value)
            elif action == 'remove':
                instance.command('whitelist remove ' + value)
        elif 'ops.txt' in listfile:
            if action == 'add':
                instance.command('op '+ value)
            elif action == 'remove':
                instance.command('deop ' + value)
        elif 'banned-players.txt' in listfile:
            if action == 'add':
                instance.command('ban ' + value)
            elif action == 'remove':
                instance.command('pardon ' + value)
        elif 'banned-ips.txt' in listfile:
            if action == 'add':
                instance.command('ban-ip ' + value)
            elif action == 'remove':
                instance.command('pardon-ip ' + value)

    str = '\n'
#Needs the 'or' since . isn't considered alnum
    if value.isalnum() or 'banned-ips' in listfile:
        try:
            list_contents = open(listfile, mode='r')
            newlist = list_contents.read()
            newlist = newlist.split()
            list_contents.close()
            list_contents = open(listfile, mode='w')
            if action=='add':
                newlist.append(value)
                newlist.sort()
                joined = str.join(newlist)
                list_contents.write(joined)
                result = 'Added %s to %s' % (value, listfile)
            elif action=='remove':
                newlist.remove(value)
                joined = str.join(newlist)
                list_contents.write(joined)
                result = 'Removed %s from %s' % (value, listfile)
            else:
                return 'Invalid action "%s"!' % action
            for server, port, status in mineos.mc.ports_reserved():
                instance = mineos.mc(server)
                if status == 'up' and instance.server_config['custom']['list_mgmt'] == 'true':
                    sendcmd(listfile, action, value, server)
            return result
        except Exception as x:
            return '%s not found!' % listfile
        list_contents.close()
    else:
        return 'Invalid username!'

def sync_lists():
    updated = []
    updated.append('Synced:')
    path1 = os.path.join(mineos.mc().mc_path, 'lists', '*.txt')
    for server, port, status in mineos.mc.ports_reserved():
        instance = mineos.mc(server)
        if instance.server_config['custom']['list_mgmt'] == 'true':
            try:
                path2 = os.path.join(mineos.mc().mineos_config['paths']['world_path'], instance.server_name)
#To prevent potential abuse of shell=True
                if ';' in path1 or ';' in path2:
                    return 'Illegal parameters!'
                cmd = 'cp %s %s' % (path1, path2)
#                hooray = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
#                print hooray
                updated.append(instance.server_name)
            except Exception as x:
#                print 'Failed: %s' % (x)
                updated.append('(Failed: %s)' % instance.server_name)
    str = ', '
    rstr = str.join(updated)
    return rstr

def user_actions(action, server, userlist):
    instance = mineos.mc(server)
    splitlist = userlist.split(';')
    message = ''
    if action=='kickuser':
        for x in splitlist:
            instance.command('kick ' + x)
    elif action=='banuser':
        if instance.server_config['custom']['list_mgmt'] == 'true':
            for x in splitlist:
                message = list_edit('banlist', 'add', x)
                message = message + '\n' + list_edit(whitelist, 'remove', x)
        else:
            for x in splitlist:
                instance.command('ban ' + x)
    elif action=='opuser':
        if instance.server_config['custom']['list_mgmt'] == 'true':
            for x in splitlist:
                message = list_edit('oplist', 'add', x)
        else:
                instance.command('op ' + x)
    print message
    
def display_crontabs():
    print '''
    <script type="text/javascript">
    $('.sc').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "display",
                                      server: $(this).attr("id"),
                                      page: 'server.config' },
         function(data){ $('#main').html(data); });
    }));
    </script>
    '''
    print '<h2>System Crontabs</h2>'
    print '<p><span class="green">%s</span> servers were located in <span class="green">%s</a>:</p>' % (len(mineos.mc.ports_reserved()),
                                                     mineos.mc().mineos_config['paths']['world_path'])
    print '<pre><b>%s%s%s%s%s</b><br>' % ('{:<20}'.format('server'),
                                      '{:<14}'.format('archive'),
                                      '{:<14}'.format('backup'),
                                      '{:<14}'.format('map'),
                                      '{:<14}'.format('restart'))

    for server, port, status in mineos.mc.ports_reserved():
        instance = mineos.mc(server)
        print '<a href="#" class="sc stats" id="%s">%s</a>%s%s%s%s' % (server,
                                                               '{:<20}'.format(server),
                                                               '{:<14}'.format(instance.server_config['crontabs']['freq_archive']),
                                                               '{:<14}'.format(instance.server_config['crontabs']['freq_backup']),
                                                               '{:<14}'.format(instance.server_config['crontabs']['freq_map']),
                                                               '{:<14}'.format(instance.server_config['crontabs']['freq_restart']))

def display_initial():
    print '''
    <script type="text/javascript">
    $('.stats').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "display",
                                      server: $(this).attr("id"),
                                      page: 'stats' },
         function(data){ $('#main').html(data); });
    }));
    $('.fixconfigs').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "act",
                                      server: "none",
                                      action: "fixconfigs" },
         function(data){ $('#main').html(data); });
    }));
    </script>
    <p>Welcome to the MineOS admin panel!</p>
    <p>Using this web admin interface, you can handle all actions of your MineOS server:</p>
    <ul>
      <li>create new servers</li>
      <li>change memory allocated to each java instance, as well as edit server.properties</li>
      <li>backup, restore, map, archive your servers</li>
      <li>view the server logs</li>
      <li>import worlds from existing archives</li>
      <li>set scheduled tasks for backups and mapping</li>
    </ul>
    '''
    print '<h3>Server List</h3>'
    print '<pre>'
#    print '<a href="#" class="createnew green">Create a server</a>'

    colors = {
        'template': '<span class="black">%s</span>' % '{:<6}'.format('template'),
        'down': '<span class="red">%s</span>' % '{:<6}'.format('down'),
        'up': '<span class="green">%s</span>' % '{:<6}'.format('up'),
        'unclean': '<span class="red">%s</span>' % '{:<6}'.format('unclean'),
        'foreign': '<span class="purple">%s</span>' % '{:<6}'.format('foreign'),
        }

    server_list = mineos.mc.ports_reserved()
    try:
        for server, port, status in server_list:
            print '<a href="#" class="stats" id="%s">%s</a>%s' % (server,
                                                                '{:<20}'.format(server),
                                                                colors.get(status))
    except:
        print 'No servers set up!'
#Remove/comemnt out for any kind of official release!
    print '<a href="#" class="fixconfigs" id="fixconfigs">Manually update configs</a>'
    print '</pre>'
            
def display_status():
    print '''
    <script type="text/javascript">
    $('.status').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "act",
                                      server: $(this).attr("id"),
                                      action: $(this).html() },
         function(data){ $('#main').html(data); });
         $(this).html("Executing command...");
         $(this).addClass("plaintext");
    }));
    $('.stats').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "display",
                                      server: $(this).attr("id"),
                                      page: 'stats' },
         function(data){ $('#main').html(data); });
    }));
    $('.stopall').one("click", (function(event){
        event.preventDefault();
        $('.stopall').html("stopping servers...");
        $('.stopall').addClass('plaintext');
        $.post("cgi-bin/server.py", { command: "act", 
                                      action: "stopall",
                                      server: "none"},
        function(data){  $('.stopall').html("Servers sent stop command."); });
    }));
    $('.forcestop').one("click", (function(event){
        event.preventDefault();
        $('.forcestop').html("killing servers...");
        $('.forcestop').addClass('plaintext');
        $.post("cgi-bin/server.py", { command: "act", 
                                      action: "forcestop",
                                      server: "none"},
        function(data){  $('.forcestop').html("killall java executed."); });
    }));
    </script>'''

    print '<h2>%s</h2>' % 'All Servers'
    print '<span class="red smallcaps">All-server actions: <a href="#" class="stopall">Stop</a> <a href="#" class="forcestop">Kill</a></span>'
    print '<p><span class="green">%s</span> servers were located in <span class="green">%s</a>:</p>' % (len(mineos.mc.ports_reserved()),
                                                     mineos.mc().mineos_config['paths']['world_path'])
    print '<pre><b>%s%s%s</b><br>' % ('{:<20}'.format('server'),
                                      '{:<11}'.format('status'),
                                      '{:<8}'.format('online'))

    colors = {
        'template': '<span class="black">%s</span>' % '{:<11}'.format('template'),
        'down': '<span class="red">%s</span>' % '{:<11}'.format('down'),
        'up': '<span class="green">%s</span>' % '{:<11}'.format('up'),
        'unclean': '<span class="red">%s</span>' % '{:<11}'.format('unclean'),
        'foreign': '<span class="purple">%s</span>' % '{:<11}'.format('foreign'),
        }

    config = mineos.mc().mineos_config
    
    for server, port, status in mineos.mc.ports_reserved():
        print '<a href="#" class="stats" id="%s">%s</a>%s' % (server,
                                                                '{:<20}'.format(server),
                                                                colors.get(status)),
        instance = mineos.mc(server)
        print '{:<8}'.format('%s/%s' % (len(instance.list_players()),
                                        instance.server_config['minecraft']['max_players'])),
        print {
            'template': '<a href="#" class="status %s" id="%s">%s</a>' % (status, server, 'start'),
            'up': '<a href="#" class="status %s" id="%s">%s</a>' % (status, server, 'stop'),
            'down': '<a href="#" class="status %s" id="%s">%s</a>' % (status, server, 'start'),
            'unclean': '<a href="#" class="status %s" id="%s">%s</a>' % (status, server, 'clean'),
            'foreign': '<a href="#" class="status %s" id="%s">%s</a>' % (status, server, 'create'),
            }.get(status),

        print '{:<6}'.format('&nbsp'),
        
        if status == 'up':
            print '<a href="#" class="status up" id="%s">%s</a>' % (server, 'restart'),
        print ''
    print '</pre>'

def display_logdump():
    print '''
    <script type="text/javascript">

        $('#commandtext').keypress(function(e){
            if(e.which == 13){
                e.preventDefault();
                $.post("cgi-bin/server.py", { command: "act",
                                              action: "consolecommand",
                                              server: $('#switch').val(),
                                              argument: $('#commandtext').val() },
                                              function(data){ $('#response').html(data);
                                                            $.post("cgi-bin/server.py", { command: "act",
                                                                                          action: "logdump",
                                                                                          server: $('#switch').val() },
                                                             function(data){ $('#logdumptext').html(data); });
                                                            });
            }
        });
    
        $('.display').click(function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "act",
                                      action: "logdump",
                                      server: $('#switch').val() },
         function(data){ $('#logdumptext').html(data); });
    });
        $('#sendcommand').click(function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "act",
                                      action: "consolecommand",
                                      server: $('#switch').val(),
                                      argument: $('#commandtext').val() },
                                      function(data){ $('#response').html(data);
                                                    $.post("cgi-bin/server.py", { command: "act",
                                                                                  action: "logdump",
                                                                                  server: $('#switch').val() },
                                                     function(data){ $('#logdumptext').html(data); });
                                                    });
    });
    </script>'''
    print '<h2>Console and Server Logs</h2>'
    print '<a href="#" class="display actionbutton">Display</a>'
    print '<select id="switch" name="server">'
    print '<option>mineos</option>'
    print '<option>----------</option>'
    for server, port, status in mineos.mc.ports_reserved():
        if status in ['up', 'down', 'foreign', 'unclean']:
            print '<option>%s</option>' % server
    print '</select>'
    print '<textarea id="logdumptext" cols="60" rows="20" readonly="readonly"></textarea><br>'
    print '''
    <form id="commandform">
        <input name="command" type="hidden" value="act">
        <input name="action" type="hidden" value="command">
        <table>
            <tr> 
                <td colspan="2"><label for="command">command:</label></td>
                <td colspan="2"><input type="text" id="commandtext" size="45" value="" /></td>
            </tr>
            <tr> 
                <td colspan="2"><a href="#" id="sendcommand" class="actionbutton">Send Command</a></td>
                <td colspan="2"><span id="response"></span></td>
            </tr>
        </table>
    </form>'''

def display_mineoslogdump():
    import fileinput
    import shlex
    filepath = os.path.join(mineos.mc().mc_path, 'mineos.log')
    execute_command = 'tail -n 200 %s' % filepath
#    output = subprocess.check_output(shlex.split(execute_command))
    getlog = subprocess.Popen(shlex.split(execute_command),stdout=subprocess.PIPE)
    (sout,serr) = getlog.communicate()
    print str(sout)
        
def display_bam(page):
    print '''
    <script type="text/javascript">
        $('.%s').one("click", (function(event){
        event.preventDefault();
        $(this).addClass("plaintext");
        $.post("cgi-bin/server.py", { command: "act", 
                                      server: $(this).attr("id"), 
                                      action: $(this).html() },
         function(data){ $('#main').html(data); });
         $(this).html("Executing command...");
    }));

        $('.archive_logs').one("click", (function(event){
        event.preventDefault();
        $(this).addClass("plaintext");
        $.post("cgi-bin/server.py", { command: "act", 
                                      server: $(this).attr("id"), 
                                      action: 'log_archive' },
         function(data){ $('#main').html(data); });
         $(this).html("Executing command...");
    }));
    </script>''' % page
    print '<h2>%s</h2>' % page.title()

    print '<p><span class="green">%s</span> servers were located in <span class="green">%s</a>:</p>' % (len(mineos.mc.ports_reserved()),
                                                                                                        mineos.mc().mineos_config['paths']['world_path'])
    print '<pre><b>%s%s%s</b><br>' % ('{:<20}'.format('server'),
                               '{:<12}'.format('freq'),
                               '{:<12}'.format('status'))

    colors = {
        'template': '<span class="black">%s</span>' % '{:<12}'.format('template'),
        'down': '<span class="red">%s</span>' % '{:<12}'.format('down'),
        'up': '<span class="green">%s</span>' % '{:<12}'.format('up'),
        'unclean': '<span class="red">%s</span>' % '{:<12}'.format('unclean'),
        'foreign': '<span class="purple">%s</span>' % '{:<12}'.format('foreign'),
        }
    
    for server, port, status in mineos.mc.ports_reserved():
        print '%s%s%s' % ('{:<20}'.format(server),
                          '{:<12}'.format(mineos.mc(server).server_config['crontabs']['freq_%s' % page]),
                          colors.get(status)),

        if status in ['up', 'down', 'unclean']:
            print '<a href="#" class="%s" id="%s">%s</a>' % (page, server, page),
        else:
            print '%s'% page,

        if status == 'down' and page == 'archive':
            print '<a href="#" class="%s" id="%s">%s</a>' % ('archive_logs', server, 'gzip server.log'),
        print

    print '</pre>'

def display_rename(server_name):
    print '''
    <script type="text/javascript">
        $('#renamebutton').one("click", (function(event){
            event.preventDefault();
            $.post("cgi-bin/server.py", $('#renameform').serialize(),
            function(data){ $('#main').html(data); });
        }));
    </script>'''
    print '<h2>Renaming server %s</h2>' % server_name
    print '''
    <form id="renameform" class="renameform">
        <input name="command" type="hidden" value="act">
        <input name="action" type="hidden" value="rename">
        <input name="server" type="hidden" value="%s">
        <table>
            <tr> 
                <td colspan="2"><label for="rename">rename to:</label></td>
                <td colspan="2"><input type="text" name="newname" value="" /></td>
            </tr>
            <tr> 
                <td colspan="4"><a href="#" id="renamebutton" class="actionbutton">Rename</a></td>
            </tr>
        </table>
    </form>''' % server_name

def display_stats(server_name):
    def cmd_dropdown(instance):
        selects = []
        selects.append('<option value="none" title="stats" id="none" SELECTED>Select an action to perform</option>')
        selects.append('<option value="update" title="server.properties" id="display">Edit server.properties')
        selects.append('<option value="update" title="server.config" id="display">Edit server.config')
        selects.append({
            'template': '<option value="start" title="none" id="act">Start server</option>',
            'up': '<option value="stop" title="none" id="act">Stop server</option>',
            'down': '<option value="start" title="none" id="act">Start server</option>',
            'unclean': '<option value="clean" title="none" id="act">Clean lock files</option>',
            'foreign': '<option value="create" title="none" id="act">Create from import</option>',
            }.get(status)),

        if status == 'up':
            selects.append('<option value="restart" title="0" id="act">Restart now</option>')
            selects.append('<option value="restart" title="30" id="act">Restart in 30 seconds</option>')
            selects.append('<option value="restart" title="60" id="act">Restart in one minute</option>')
            selects.append('<option value="restart" title="120" id="act">Restart in two minutes</option>')
            selects.append('<option value="restart" title="300" id="act">Restart in five minutes</option>')
            selects.append('<option value="none" title="stats" id="none">--------------------</option>')
            for x in ['01','02','03','04','05','06','07','08','09','10']:
                name = instance.server_config['macros']['macro' + x]
                if len(name) > 0:
                    selects.append('<option value="macro" title="macro%s" id="act">%s</option>' % (x, name))
        elif status in ['down', 'foreign', 'unclean']:
            selects.append('<option value="rename" title="none" id="display">Rename server</option>')
            selects.append('<option value="archive_log" title="none" id="act">Archive & clear server.log</option>')
        return ' '.join(selects)
    
    print '''
    <script type="text/javascript">
        $('.status').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "act",
                                      server: $(this).attr("id"),
                                      action: $(this).html() },
         function(data){ $('#main').html(data); });
         $(this).html("Executing command...");
         $(this).addClass("plaintext");
    }));
    $('.stats').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "display",
                                      server: $(this).attr("id"),
                                      page: 'stats' },
         function(data){ $('#main').html(data); });
    }));
    $('#sendcommand').click(function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: $('#commandtext').find("option:selected").attr("id"),
                                      action: $('#commandtext').val(),
                                      page: $('#commandtext').find("option:selected").attr("title"),
                                      server: $('#servername').val(),
                                      argument: $('#commandtext').find("option:selected").attr("title") },
        function(data){ $('#main').html(data) });
    });
        $('#kickuser').click(function(event){
        event.preventDefault();
        try{
            var templist = document.getElementsByName("items[]");
            var userlist = "";
            for (x = 0;x < templist.length;x++){
                if (templist[x].checked){
                    userlist = (userlist + (templist[x].value) + ";");
                }
            }
        }
        catch (fail){
            alert(fail.message);
        }
        $.post("cgi-bin/server.py", { command: "act",
                                    server: $('#servername').val(),
                                    action: "kickuser",
                                    argument: userlist },
        function(data){ $('#main').html(data); });
    });
    </script>'''

    server = mineos.mc(server_name)
    status = server.status()
    config = mineos.mc().mineos_config
    port = server.server_config['minecraft']['port']
    
    colors = {
        'template': '<span class="black">%s</span>' % '{:<6}'.format('template'),
        'down': '<span class="red">%s</span>' % '{:<6}'.format('down'),
        'up': '<span class="green">%s</span>' % '{:<6}'.format('up'),
        'unclean': '<span class="red">%s</span>' % '{:<6}'.format('unclean'),
        'foreign': '<span class="purple">%s</span>' % '{:<6}'.format('foreign'),
        }

    print '<table><tr>'
    print '<td valign="baseline"><h2>Server Status:</h2></td>'
    print '<td>&nbsp;</td>'
    print '<td valign="baseline"><h2>%s</h2></td>' % (server_name)
    print '</tr><tr>'
    print '<td valign="baseline"><h4>Server is currently: %s</h4></td>' % (colors.get(status))
    print '<td>&nbsp;</td>'
    print '<td valign="baseline"><a href="#" class="stats" id="%s">[Refresh Page]</a></td>' % (server_name)
    print '</tr></table>'

    print '<pre><b>%s%s%s%s%s</b><br>' % ('{:<10}'.format('port'),
                                      '{:<13}'.format('size'),
                                      '{:<14}'.format('ram use'),
                                      '{:<16}'.format('connections'),
                                      '{:<8}'.format('uptime'))
                                      
    paths = config['paths']['world_path'] + '/' + server_name
    try:
        size = int(sumdirs(paths))
        if (size / 1000000000) > 1:
            size = size / 1000000000
            sizetype = 'GB'
        elif (size / 1000000) > 1:
            size = size / 1000000
            sizetype = 'MB'
        elif (size / 1000) > 1:
            size = size / 1000
            sizetype = 'KB'
        else:
            sizetype = 'B'
    except:
        size = sumdirs(paths)
        sizetype = 'B'

    print '%s%s%s' % ('{:<9}'.format(port),
                                                                '{:<4}'.format(size),
                                                                '{:<6}'.format(sizetype)),
#RAM is reported in KB!
    if status == 'up':
        try:
            server_pid = server.server_getpid()
            ram_use = int(server.server_info_ps(server_pid, 'ram'))
            if (ram_use / 10000000) > 1:
                ram_use = ram_use / 10000000
                sizetype = 'GB'
            elif (ram_use / 1000) > 1:
                ram_use = ram_use / 1000
                sizetype = 'MB'
            else:
                sizetype = 'KB'
        except:
            ram_use = 0
            sizetype = 'KB'
        try:
            uptime = server.server_info_ps(server_pid, 'uptime')
            uptime = uptime.strip()
        except:
            uptime = "down"
    else:
        ram_use = 0
        sizetype = 'KB'
        uptime = 'down'


    if ram_use > int(server.server_config['minecraft']['mem']):
        print '{:<20}'.format('<span class="red">%s%s</span>/%sMB' % ('{:<4}'.format(ram_use),
                                                                '{:<2}'.format(sizetype),
                                                                '{:<4}'.format(server.server_config['minecraft']['mem']))),
    else:
        print '{:<20}'.format('%s%s/%sMB' % ('{:<4}'.format(ram_use),
                                                                '{:<2}'.format(sizetype),
                                                                '{:<4}'.format(server.server_config['minecraft']['mem']))),

    print '{:<11}'.format('%s/%s' % (len(server.list_players()), 
                                                            server.server_config['minecraft']['max_players'])),
    print '{:<0}'.format('%s' % uptime)
    print '<br></pre>'

    print '''
        <form id="dropdownmenu">
            <input name="servername" id="servername" type="hidden" value="%s">
            <label for="commandtext"> </label>
            <select name="commandtext" id="commandtext" style="width: 350px">
                %s
            </select>
            <a href="#" id="sendcommand" class="actionbutton">Send</a>
        </form>''' % (server_name, cmd_dropdown(server))
    
    selectlist = []
    for x in server.list_players():
        selectlist.append('<label><input type="checkbox" name="items[]" value="%s"/>%s</label><br />' % (x, x))
    selectlist.sort()
    selectlist = ' '.join(selectlist)
    print '''
        <form id="playeractions" name="playeractions">
            <input name="servername" id="servername" type="hidden" value="%s">
            <table cols=2><tr>
            <td valign="top"><p style="height: 150px; width: 345px; overflow: auto; border: 1px solid #eee; background: #eee; color: #000; margin-bottom: 1.5em;">%s</p></td>
            <td valign="top">
                <br>
                <a href="#" id="kickuser" class="actionbutton">Kick users</a><br>
                <a href="#" id="banuser" class="actionbutton">Ban users</a><br>
                <a href="#" id="opuser" class="actionbutton">OP users</a><br>
            </td>
            </tr></table>
        </form>''' % (server_name, selectlist)
        
#Moved out of display_overview for use in other functions.
def sumdirs(base):
    try:
        return sum(os.path.getsize(os.path.join(dirpath,filename)) for dirpath, dirnames, filenames in os.walk(base) for filename in filenames)
    except OSError as e:
        return e       

def display_overview():
    print '''
    <script type="text/javascript">

    $('.updatemc').one("click", (function(event){
        event.preventDefault();
        $('.updatemc').addClass('plaintext');
        $('.updatemc').html("Updating Minecraft Server Jars...");
        $.post("cgi-bin/server.py", { command: "act", 
                                      action: "updatemc",
                                      server: "none"},
        function(data){  $('.updatemc').html("Updating Complete."); });
    }));

     $('.updatemos').one("click", (function(event){
        event.preventDefault();
        $('.updatemos').addClass('plaintext');
        $('.updatemos').html("Updating MineOS...");
        $.post("cgi-bin/server.py", { command: "act", 
                                      action: "updatemos",
                                      server: "none"},
        function(data){  $('.updatemos').html("Update Complete."); });
    }));

    $('.updatechooser').click( (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "display",
                                      server: "none",
                                      page: "jars" },
         function(data){ $('#main').html(data); });
    }));
    </script>'''
    print '<h1>MineOS Server Overview</h1>'
    print '<pre>'
    print '<b>Machine uptime:',
    try:
        server_uptime = subprocess.Popen(['ps','-p','1','-o','etime='],stdout=subprocess.PIPE)
        (sout,serr) = server_uptime.communicate()
        print sout, '</b>'
    except:
        print 'unavailable</b>'
    print '<b>Minecraft file timestamps</b>:', '<a href="#" class="updatemc">%s</a>' % 'Update Minecraft Server Jars',
    print ' <a href="#" class="updatechooser">%s</a>' % 'Jar selection'
    for filename in [mineos.mc().mineos_config['downloads']['mc_jar'],
                     mineos.mc().mineos_config['downloads']['bukkit_jar'],
                     mineos.mc().mineos_config['downloads']['c10t_tgz']]:
        filepath = os.path.join(mineos.mc().mineos_config['paths']['mc_path'], filename)
        if os.access(filepath, os.F_OK):
            print mineos.mc.list_build_date(filepath), '{:<30}'.format(filename),
            if os.access(filepath, os.R_OK):
                print '<span class="green smallcaps">Read OK</span>'
            else:
                print '<span class="red smallcaps">Read failure - CHECK PERMISSIONS</span>'
        else:
            print 'Not found ', '{:<30}'.format(filename), '<a href="#" class="updatemc">DOWNLOAD</a>'  

    filename = mineos.mc().mineos_config['downloads']['canary_jar']
    filepath = os.path.join(mineos.mc().mineos_config['paths']['mc_path'], 'canary', filename)
    if os.access(filepath, os.F_OK):
        print mineos.mc.list_build_date(filepath), '{:<30}'.format(filename),
        if os.access(filepath, os.R_OK):
            print '<span class="green smallcaps">Read OK</span>'
        else:
            print '<span class="red smallcaps">Read failure - CHECK PERMISSIONS</span>'
    else:
        print 'Not found ', '{:<30}'.format(filename), '<a href="#" class="updatemc">DOWNLOAD</a>'

    print
    print '<b>MineOS Scripts</b>:', '<a href="#" class="updatemos">%s</a>' % 'Update MineOS'
    print '{:<18}'.format('server.py'), __version__
    import mineos_console
    print '{:<18}'.format('mineos_console.py'), mineos_console.__version__
    print '{:<18}'.format('mineos.py'), mineos.__version__
    import statlog
    print '{:<18}'.format('statlog.py'), statlog.__version__

    print
    print '<b>MineOS Disk Usage</b>:'
    config = mineos.mc().mineos_config

    print '{:<25}'.format(config['paths']['mc_path']), sumdirs(config['paths']['mc_path']) / 1000000, 'MB'

    for paths in [config['paths']['world_path'],
                  config['paths']['backup_path'],
                  config['paths']['archive_path'],
                  config['paths']['snapshot_path'],
                  config['paths']['import_path'],
                  config['paths']['http_snapshot_path']]:
        try:
            size = sumdirs(paths)
            print '{:<25}'.format(paths), size / 1000000, 'MB'
        except TypeError:
            print size

    print '{:<25}'.format('Approx. free space'), os.statvfs('/').f_bfree * os.statvfs('/').f_frsize / 1024000, 'MB'
    print '</pre>'
        
def display_importer():
    print '''
    <script type="text/javascript">
        $('.import').one("click", (function(event){
        var clicked = $(this);
        event.preventDefault();
        $(clicked).addClass('plaintext');
        $.post("cgi-bin/server.py", { command: "act",
                                      action: "import",
                                      archive: $(clicked).html(),
                                      server: "none"},
         function(data){  $('#main').html(data); });
         $(clicked).html($(clicked).html() + ' -- saving to server: imported');
    }));
    </script>'''
    print '<h2>Available Imports</h2>'
    print '<p>The following archives were located in <span class="green">%s</span>:</p>' % mineos.mc().mineos_config['paths']['import_path']
    print '<p>'
    print '<ul>'
    for archive in mineos.mc.list_imports():
        print '<li><a href="#" class="import">%s</a></li>' % archive
    print '</ul>'
    print '</p>'

def display_jars():
    def selects_mod(mod):
        selects = []
        if mineos.mc().mineos_config['update'][mod] == 'true':
            selects.append('<option value="true" SELECTED>true</option>')
            selects.append('<option value="false">false</option>')
        else:
            selects.append('<option value="true">true</option>')
            selects.append('<option value="false" SELECTED>false</option>')                
        return ' '.join(selects)
    print '''
    <script type="text/javascript">
     $('#updatelist').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", $('#jarform').serialize(),
             function(data){ $('#main').html(data); });
    }));
    </script>
    <h2>Choose which jars to download and update</h2>
    <p>Note, existing downloaded mods marked 'false' will still function! They simply will not be downloaded/updated when
    'Update Minecraft Server Jars' is clicked.</p>
    <form id="jarform">
      <table>
        <tr> 
          <td colspan="2"><label for="pure">pure</label></td>
          <td colspan="2"><select name="pure" id="pure" tabindex="6">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="bukkit">bukkit</label></td>
          <td colspan="2"><select name="bukkit" id="bukkit" tabindex="6">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="canary">canary</label></td>
          <td colspan="2"><select name="canary" id="canary" tabindex="6">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="c10t">c10t</label></td>
          <td colspan="2"><select name="c10t" id="c10t" tabindex="6">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="4"><a href="#" id="updatelist" class="actionbutton">Update</a></td>
        </tr>
      </table>
      <input name="server" type="hidden" value="none">
      <input name="command" type="hidden" value="act">
      <input name="action" type="hidden" value="updatejars">
    </form>''' % (selects_mod('pure'),
                  selects_mod('bukkit'),
                  selects_mod('canary'),
                  selects_mod('c10t'))

def display_createnew():
    def selects_mod():
        selects = []

        for mods in mineos.mc.list_server_jars():
            if mods == mineos.mc().mineos_config['downloads']['mc_jar']:
                selects.append('<option value="%s" SELECTED>%s</option>' % (mods, mods))
            else:
                selects.append('<option value="%s">%s</option>' % (mods, mods))
        return ' '.join(selects)
    
    print '''
    <script type="text/javascript">
     $('#createserver').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", $('#newserver').serialize(),
             function(data){ $('#main').html(data); });
    }));
    </script>
    <h2>Create a new Minecraft Server</h2>
    <form id="newserver">
      <table>
        <tr> 
          <td colspan="2"><label for="server">Server Name</label></td>
          <td colspan="2"><input type="text" name="server" id="server" tabindex="1" /></td>
        </tr>
        <tr> 
          <td colspan="4"><em>server names may not contain spaces or non-alphanumerics.</em></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="port">Port</label></td>
          <td colspan="2"><input type="text" name="port" id="port" tabindex="2" value="25565" /></td>
        </tr>
        <tr> 
          <td colspan="4"><em>non-default ports will need to be opened in the iptables firewall</em></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="max_players">Max Players</label></td>
          <td colspan="2"><input type="text" name="max_players" id="max_players" tabindex="3" value="20" /></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="max_players">RAM</label></td>
          <td colspan="2"><input type="text" name="mem" id="mem" tabindex="4" value="1024" /></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="server_jar">Minecraft Jar</label></td>
          <td colspan="2"><select name="server_jar" id="server_jar" tabindex="5">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2">&nbsp</td>
          <td colspan="2"></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="level_seed">level-seed</label></td>
          <td colspan="2"><input type="text" name="level_seed" id="level_seed" tabindex="10" value="" /></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="gamemode">gamemode</label></td>
          <td colspan="2"><select name="gamemode" id="gamemode" tabindex="">
              <option value="0" SELECTED>Survival (0)</option>
              <option value="1">Creative (1)</option>
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="level_type">level-type</label></td>
          <td colspan="2"><select name="level_type" id="level_type" tabindex="">
              <option value="DEFAULT" SELECTED>DEFAULT</option>
              <option value="FLAT">FLAT</option>
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="difficulty">difficulty</label></td>
          <td colspan="2"><select name="difficulty" id="difficulty" tabindex="">
              <option value="0">Peaceful (0)</option>
              <option value="1" SELECTED>Easy (1)</option>
              <option value="2">Normal (2)</option>
              <option value="3">Hard (3)</option>
            </select></td>
        </tr>    
        <tr> 
          <td colspan="2">&nbsp</td>
          <td colspan="2"></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="freq_archive">Archive</label></td>
          <td colspan="2"><select name="freq_archive" id="freq_archive" tabindex="6">
              <option value="none">none</option>
              <option value="hourly">hourly</option>
              <option value="daily">daily</option>
              <option value="weekly">weekly</option>
              <option value="monthly">monthly</option>
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="freq_backup">Backup</label></td>
          <td colspan="2"><select name="freq_backup" id="freq_backup" tabindex="7">
              <option value="none">none</option>
              <option value="hourly">hourly</option>
              <option value="daily">daily</option>
              <option value="weekly">weekly</option>
              <option value="monthly">monthly</option>
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="freq_map">Map</label></td>
          <td colspan="2"><select name="freq_map" id="freq_map" tabindex="8">
              <option value="none">none</option>
              <option value="hourly">hourly</option>
              <option value="daily">daily</option>
              <option value="weekly">weekly</option>
              <option value="monthly">monthly</option>
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="freq_restart">Restart</label></td>
          <td colspan="2"><select name="freq_restart" id="freq_restart" tabindex="8">
              <option value="none">none</option>
              <option value="hourly">hourly</option>
              <option value="daily">daily</option>
              <option value="weekly">weekly</option>
              <option value="monthly">monthly</option>
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="restore">Restore on Reboot</label></td>
          <td colspan="2"><select name="restore" id="restore" tabindex="6">
            <option value="true">true</option>
            <option value="false" SELECTED>false</option>
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="start">Start on Reboot</label></td>
          <td colspan="2"><select name="start" id="start" tabindex="6">
            <option value="true">true</option>
            <option value="false" SELECTED>false</option>
            </select></td>
        </tr>
        <tr> 
          <td colspan="2">&nbsp</td>
          <td colspan="2"></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="stats_delay">Log resource use statistics per</label></td>
          <td colspan="2"><select name="stats_delay" id="stats_delay" tabindex="">
              <option value="0">none</option>
              <option value="1">1</option>
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="15">15</option>
              <option value="30">30</option>
              <option value="60">60</option>
            </select> minutes (0 disables)</td>
        </tr>
        <tr> 
          <td colspan="2"><label for="list_mgmt">Manage lists via web? </label></td>
          <td colspan="2"><select name="list_mgmt" id="list_mgmt" tabindex="">
              <option value="false">no</option>
              <option value="true">yes</option>
            </select></td>
        </tr>
        <tr> 
          <td colspan="4"><a href="#" id="createserver" class="actionbutton">Create Server</a></td>
        </tr>
      </table>
      <input name="command" type="hidden" value="act">
      <input name="action" type="hidden" value="create">
    </form>''' % selects_mod()

def display_server_config(server_name):
    def selects_mod():
        selects = []

        for mods in mineos.mc.list_server_jars():
            if mods == mineos.mc(server_name).server_config['java']['server_jar']:
                selects.append('<option value="%s" SELECTED>%s</option>' % (mods, mods))
            else:
                selects.append('<option value="%s">%s</option>' % (mods, mods))
        return ' '.join(selects)   

    def selects_crontab(server_name, crontype):
        selects = []

        for mods in ['none', 'hourly', 'daily', 'weekly', 'monthly']:
            if mods == instance.server_config['crontabs']['freq_' + crontype]:
                selects.append('<option value="%s" SELECTED>%s</option>' % (mods, mods))
            else:
                selects.append('<option value="%s">%s</option>' % (mods, mods))
        return ' '.join(selects)

    def selects_onboot(server_name, activity):
        selects = []

        newinst = mineos.mc(server_name)
        try:
            if newinst.server_config['onreboot'][activity] == 'true':
                selects.append('<option value="true" SELECTED>true</option>')
                selects.append('<option value="false">false</option>')
            else:
                selects.append('<option value="true">true</option>')
                selects.append('<option value="false" SELECTED>false</option>')
        except KeyError:
            raise mineos.NoOnRebootSectionException(server_name,
                                                    os.path.join(newinst.cwd, 'server.config'))
            selects.append('<option value="true">true</option>')
            selects.append('<option value="false" SELECTED>false</option>')           
        return ' '.join(selects)

#Make sure config is updated first for next two functions
    def selects_delay(server_name):
        selects = []

        for mods in ['0','1','5','10','30','60']:
            if mods == mineos.mc(server_name).server_config['custom']['stats_delay']:
                selects.append('<option value="%s" SELECTED>%s</option>' % (mods, mods))
            else:
                selects.append('<option value="%s">%s</option>' % (mods, mods))
        return ' '.join(selects)
        
    def selects_list(server_name):
        selects = []

        newinst = mineos.mc(server_name)
        if newinst.server_config['custom']['list_mgmt'] == 'true':
            selects.append('<option value="true" SELECTED>yes</option>')
            selects.append('<option value="false">no</option>')
        else:
            selects.append('<option value="true">yes</option>')
            selects.append('<option value="false" SELECTED>no</option>')
        return ' '.join(selects)

    instance = mineos.mc(server_name)
    print '''
    <script type="text/javascript">
     $('.updatesc').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", $('#updateserver').serialize(),
             function(data){ $('#main').html(data); });
    }));
    </script>
    <h2>server.config for %s</h2>
    <form id="updateserver">
        <input name="command" type="hidden" value="act">
        <input name="action" type="hidden" value="update_sc">
        <input name="server" type="hidden" value="%s">
      <table>
        <tr> 
          <td colspan="2"><label for="port">Server Port</label></td>
          <td colspan="2"><input type="text" name="port" id="port" tabindex="2" value="%s" /></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="max_players">Max Players</label></td>
          <td colspan="2"><input type="text" name="max_players" id="max_players" value="%s" tabindex="3" /></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="max_players">RAM</label></td>
          <td colspan="2"><input type="text" name="mem" id="mem" value="%s" tabindex="4" /></td>
        </tr>
        <tr> 
          <td colspan="2">&nbsp</td>
          <td colspan="2"></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="mod">Server Jar</label></td>
          <td colspan="2"><select name="server_jar" id="server_jar" tabindex="5">
              %s
                          </select>
          </td>
        </tr>
        <tr> 
          <td colspan="2"><label for="server_jar_args">Jar Arguments</label></td>
          <td colspan="2"><input type="text" name="server_jar_args" id="server_jar_args" value="%s" tabindex="9" /></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="java_tweaks">Java Tweaks</label></td>
          <td colspan="2"><input type="text" name="java_tweaks" id="java_tweaks" value="%s" tabindex="9" /></td>
        </tr>
        <tr> 
          <td colspan="2">&nbsp</td>
          <td colspan="2"></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="freq_archive">Archive</label></td>
          <td colspan="2"><select name="freq_archive" id="freq_archive" tabindex="6">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="freq_backup">Backup</label></td>
          <td colspan="2"><select name="freq_backup" id="freq_backup" tabindex="7">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="freq_map">Map</label></td>
          <td colspan="2"><select name="freq_map" id="freq_map" tabindex="8">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="freq_restart">Restart</label></td>
          <td colspan="2"><select name="freq_restart" id="freq_restart" tabindex="8">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2">&nbsp</td>
          <td colspan="2"></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="restore">Restore on Reboot</label></td>
          <td colspan="2"><select name="restore" id="restore" tabindex="6">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2"><label for="start">Start on Reboot</label></td>
          <td colspan="2"><select name="start" id="start" tabindex="6">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="2">&nbsp</td>
          <td colspan="2"></td>
        </tr>
        <tr>
          <td colspan="2"><label for="stats_delay">Log resource use statistics per</label></td>
          <td colspan="2"><select name="stats_delay" id="stats_delay" tabindex="">
              %s
            </select> minutes (0 disables)</td>
        </tr>
        <tr>
          <td colspan="2"><label for="list_mgmt">Manage white/banlist? </label></td>
          <td colspan="2"><select name="list_mgmt" id="list_mgmt" tabindex="">
              %s
            </select></td>
        </tr>
        <tr> 
          <td colspan="4"><em>Lists include ops, whitelist, banlist, and banned IP list.<br>Managed lists must be updated via web interface.</em></td>
        </tr>
        <tr> 
          <td colspan="4"><em>Server must be restarted for log changes to take effect.</em></td>
        </tr>
        <tr> 
          <td colspan="4"><a href="#" class="updatesc actionbutton">Update</a></td>
        </tr>
      </table>
    </form>''' %(server_name, server_name,
                 instance.server_config['minecraft']['port'],
                 instance.server_config['minecraft']['max_players'],
                 instance.server_config['minecraft']['mem'],
                 selects_mod(),
                 instance.server_config['java']['server_jar_args'],
                 instance.server_config['java']['java_tweaks'],
                 selects_crontab(server_name, 'archive'),
                 selects_crontab(server_name, 'backup'),
                 selects_crontab(server_name, 'map'),
                 selects_crontab(server_name, 'restart'),
                 selects_onboot(server_name, 'restore'),
                 selects_onboot(server_name, 'start'),
                 selects_delay(server_name),
                 selects_list(server_name))

def display_server_properties(server_name):
    print '''
    <script type="text/javascript">
     $('.updatesp').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", $('#changevalues').serialize(),
             function(data){ $('#main').html(data); });
    }));
    </script>'''

    print '<h2>server.properties for %s</h2>' % server_name

    instance = mineos.mc(server_name)
    filename = os.path.join(instance.mineos_config['paths']['world_path'], server_name, 'server.properties')
    status = instance.status()

    if status in ['up', 'down', 'foreign', 'unclean']:
        print '''<form name="changevalues" id="changevalues">
                    <input name="command" type="hidden" value="act">
                    <input name="action" type="hidden" value="update_sp">
                    <input name="server" type="hidden" value="%s">
                     <table>''' % server_name

        for key, value in mineos.mc.attribute_list(filename):
            print '''
                        <tr> 
                            <td colspan="2"><label for="%s">%s</label></td>
                            <td colspan="2"><input type="text" name="%s" id="%s" value="%s" /></td>
                        </tr>''' % (key.replace('-', '_'),
                                key,
                                key.replace('-', '_'),
                                key.replace('-', '_'),
                                value)
        print '''       <tr>
                            <td colspan="4"><a href="#" class="updatesp actionbutton">Update</a></td>
                        </tr>
                    </table>
                 </form>'''

def display_restore():
    print '''
    <script type="text/javascript">
    $('.restore').one("click", (function(event){
        event.preventDefault();
        $.post("cgi-bin/server.py", { command: "act",
                                      action: "restore",
                                      server: $(this).attr("id"),
                                      steps: $(this).html() },
         function(data){ $('#main').html(data); });
    }));
    </script>'''
    print '<h2>%s</h2>' % 'Incremental Backups'

    print '<p>The following backup states were found in <span class="green">%s</a>:</p>' % mineos.mc().mineos_config['paths']['backup_path']
    print '<p><i>Click an increment to restore a server to a previous state.</i><br>Servers currently running cannot be restored until stopped.</p>'

    for server, port, status in mineos.mc.ports_reserved_backup():
        print '<h4>%s</h4>' % server
        try:
            output = mineos.mc(server).list_backups()
            print '<ol class="backupli">'
            for index, item in enumerate(output):
                count = len(output) - index - 2
                if not index:
                    print '<li>%s</li>' % item,
                elif count < 0:
                    pass
                else:
                    if mineos.mc(server).status() != 'up':
                        print '<li><a href="#" class="restore" id="%s">%s</a> %s</li>' % (server,
                                                                                          str(count) + 'B',
                                                                                          item)
                    else:
                        print '<li>%s %s</li>' % (str(count) + 'B',
                                                  item)
            
        except:
            print '<li>None</li>'
        print '</ol>'
        
def act_update_sp(form):
    sp = os.path.join(mineos.mc().mineos_config['paths']['world_path'], form['server'], 'server.properties')
    sc = os.path.join(mineos.mc().mineos_config['paths']['world_path'], form['server'], 'server.config')
    
    for key in form.keys():
        mineos.mc.attribute_change(sp, key.replace('_', '-'), form[key], form['server'])
        
        if key == 'server_port':
            mineos.mc.config_alter(sc, 'minecraft', 'port', form[key], form['server'])
        elif key == 'max_players':
            mineos.mc.config_alter(sc, 'minecraft', key, form[key], form['server'])
            
    print '<pre>'
    for key, value in mineos.mc.attribute_list(sp):
        print '{:<15}'.format(key), '{:<15}'.format(value)
    print '</pre>'

def act_update_sc(form):
    sp = os.path.join(mineos.mc().mineos_config['paths']['world_path'], form['server'], 'server.properties')
    sc = os.path.join(mineos.mc().mineos_config['paths']['world_path'], form['server'], 'server.config')
    
    for key in form.keys():
        if key in ['port', 'max_players', 'mem']:
            mineos.mc.config_alter(sc, 'minecraft', key, form[key], form['server'])
        elif key in ['freq_archive', 'freq_backup', 'freq_map', 'freq_restart']:
            mineos.mc.config_alter(sc, 'crontabs', key, form[key], form['server'])
        elif key in ['server_jar', 'server_jar_args', 'java_tweaks']:
            mineos.mc.config_alter(sc, 'java', key, form[key], form['server'])
        elif key in ['restore', 'start']:
            mineos.mc.config_alter(sc, 'onreboot', key, form[key], form['server'])
        elif key in ['stats_delay', 'list_mgmt']:
            mineos.mc.config_alter(sc, 'custom', key, form[key], form['server'])
            
        if key == 'port':
            mineos.mc.attribute_change(sp, 'server-port', form[key], form['server'])
        elif key == 'max_players':
            mineos.mc.attribute_change(sp, 'max-players', form[key], form['server'])

    for key in form.keys():
        print "%s = %s<br>" % (key, form[key])        

def act_update_jars(form):
    configfile = os.path.join(mineos.mc().mc_path, 'mineos.config')
    for key in form.keys():
        if key not in ['server', 'command', 'action']:
            mineos.mc.config_alter(configfile, 'update', key, form[key], 'None')
        
    for key in form.keys():
        print "%s = %s<br>" % (key, form[key])


def act_fix_server_config():
    print 'Updating...'
    try:
        server_list = mineos.mc.ports_reserved()
        for server, port, status in server_list:
            instance = mineos.mc(server)
            instance.fixconfig()
        print 'Configs updated.\n'
    except:
        print 'No servers found!'
    try:
        attempt = os.path.join(mineos.mc().mc_path, 'lists')
        if not os.path.exists(attempt):
            os.makedirs(attempt)
    except:
        print 'Failed to find/create /usr/games/minecraft/lists'
    try:
        attempt = mineos.mc().mineos_config['email']['server']
    except:
        confpath = os.path.join(mineos.mc().mineos_config['paths']['mc_path'], 'mineos.config')
        mineos.mc.config_section_add(confpath, 'email')
        mineos.mc.config_add(confpath,'email','server','none')
        mineos.mc.config_add(confpath,'email','type','none')
        mineos.mc.config_add(confpath,'email','port','none')
        mineos.mc.config_add(confpath,'email','login','none')
        mineos.mc.config_add(confpath,'email','pass','none')
        mineos.mc.config_add(confpath,'email','sendto','none')
        print 'mineos.config updated.\n'
        
        
form = cgi_to_dict(cgi.FieldStorage(keep_blank_values=1))

#For debug purposes only
#print form

try:
    if form['command'] == 'display':
        if form['page'] == 'status':
            display_status()
        elif form['page'] == 'console':
            display_logdump()
        elif form['page'] == 'logs':
            display_mineoslogdump()
        elif form['page'] in ['backup', 'archive', 'map']:
            display_bam(form['page'])
        elif form['page'] == 'restore':
            display_restore()
        elif form['page'] == 'rename':
            display_rename(form['server'])
        elif form['page'] == 'stats':
            display_stats(form['server'])
        elif form['page'] == 'import':
            display_importer()
        elif form['page'] == 'createnew':
            display_createnew()
        elif form['page'] == 'server.properties':
            display_server_properties(form['server'])
        elif form['page'] == 'server.config':
            display_server_config(form['server'])
        elif form['page'] == 'about':
            display_about()
        elif form['page'] == 'setup':
            display_setup()
        elif form['page'] == 'initial':
            display_initial()
        elif form['page'] == 'overview':
            display_overview()
        elif form['page'] == 'crontabs':
            display_crontabs()
        elif form['page'] in ['lists', 'opslist', 'whitelist', 'banlist', 'ipbans']:
            display_lists(form['page'], '')
        elif form['page'] == 'jars':
            display_jars()
        elif form['page'] == 'macros':
            try:
                x = form['server']
            except:
                form['server'] = "none"
            display_macros(form['server'])
        else:
            display_initial()
        
    elif form['command'] == 'act':
        instance = mineos.mc(form['server'])
        if form['action'] == 'create':
            instance.create(form)
            display_status()
        elif form['action'] == 'start':
            instance.start()
            display_stats(instance.server_name)
        elif form['action'] == 'stop':
            instance.stop()
            display_stats(instance.server_name)
        elif form['action'] == 'restart':
            try:
                temp = form['argument']
            except:
                temp = 0
            instance.restart(temp)
            display_stats(instance.server_name)
        elif form['action'] == 'stopall':
            mineos.mc.stopall()
        elif form['action'] == 'forcestop':
            mineos.mc.forcestop()
        elif form['action'] == 'clean':
            instance.clean()
            display_status()
        elif form['action'] == 'backup':
            instance.backup()
        elif form['action'] == 'archive':
            instance.archive()
        elif form['action'] == 'restore':
            instance.restore(form['steps'], True)
        elif form['action'] == 'map':
            instance.mapworld()
        elif form['action'] == 'rename':
            instance.rename(form['newname'])
        elif form['action'] == 'import':
            mineos.mc('imported').importworld(form['archive'])
        elif form['action'] == 'updatemc':
            mineos.mc.update()
        elif form['action'] == 'updatemos':
            mineos.mc.update_mineos()
            act_fix_server_config()
        elif form['action'] == 'logdump':
            if form['server'] == 'mineos':
                display_mineoslogdump()
            else:
                instance.log_dump()
        elif form['action'] == 'mineoslogdump':
            instance.mineoslog_dump()
        elif form['action'] == 'log_archive':
            instance.log_archive()
        elif form['action'] == 'update_sp':
            act_update_sp(form)
            print '(%s) update server.properties complete' % form['server']
            display_stats(instance.server_name)
        elif form['action'] == 'update_sc':
            act_update_sc(form)
            print '(%s) update server.config complete' % form['server']
            display_stats(instance.server_name)
        elif form['action'] == 'consolecommand':
            mineos.mc(form['server']).command(form['argument'])
        elif form['action'] == 'updatejars':
            act_update_jars(form)
        elif form['action'] == 'list_add':
            message = list_edit(form['list_name'], 'add', form['value'])
#Automatically remove banned players from whitelist
            if form['list_name'] == 'banlist':
                message = message + '\n' + list_edit(whitelist, 'remove', form['value'])
            display_lists(form['page'], message)
        elif form['action'] == 'list_remove':
            message = list_edit(form['list_name'], 'remove', form['value'])
            display_lists(form['page'], message)
        elif form['action'] == 'synclists':
            message = sync_lists()
            display_lists(form['page'], message)
        elif form['action'] == 'fixconfigs':
            act_fix_server_config()
        elif form['action'] == 'savemacros':
            macrolist = []
            for x in ['01','02','03','04','05','06','07','08','09','10']:
                macrolist.append(form['arg' + x])
            instance.savemacros(macrolist)
            display_macros(form['server'])
        elif form['action'] == 'macro':
            print 'Sending command...<br>'
            instance.executemacro(form['argument'])
        elif form['action'] == 'kickuser':
            user_actions(form['action'], form['server'], form['argument'])
            display_stats(form['server'])
        elif form['action'] == 'savesetup':
            pass
            
except KeyError as x:
    print 'invalid number of arguments'
    print 'Exception: %s' % (x)
    print '<br>'
    print form
except:
    pass
