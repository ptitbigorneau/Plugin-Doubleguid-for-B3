# DoubleGuid Plugin

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.1'

import b3, threading, thread, time
import b3.plugin
import b3.events
from b3 import clients

class DoubleguidPlugin(b3.plugin.Plugin):
    
    _adminPlugin = None   
    _pluginactived = "on"
    _adminlevel = 100
    _immunityminlevel = 20

    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False

        self.registerEvent(b3.events.EVT_CLIENT_AUTH)

        self._adminPlugin.registerCommand(self, 'doubleguid',self._adminlevel, self.cmd_doubleguid)

    def onLoadConfig(self):

        try:
            self._pluginactived = self.config.get('settings', 'pluginactived')
        except Exception, err:
            self.warning("Using default value %s for DoubleGuid. %s" % (self._pluginactived, err))
        self.debug('DoubleGuid : %s' % self._pluginactived)

        try:        
            self._adminlevel = self.config.getint('settings', 'adminlevel')
        except Exception, err:
            self.warning("Using default value %s for adminlevel. %s" % (self._adminlevel, err))
        self.debug('adminlevel : %s' % self._adminlevel)

        try:
            self._immunityminlevel = self.config.getint('settings', 'immunityminlevel')
        except Exception, err:
            self.warning("Using default value %s for immunityminlevel. %s" % (self._immunityminlevel, err))
        self.debug('immunityminlevel : %s' % self._immunityminlevel)

    def onEvent(self, event):

        if self._pluginactived == 'off':

           return False

        if self._pluginactived == 'on':

           
            if event.type == b3.events.EVT_CLIENT_AUTH:
            
                client = event.client
            
                for x in self.console.clients.getList():

                    if x.guid == client.guid and x.cid != client.cid:

                        if x.ip == client.ip:
                            
                            if client.maxLevel < self._immunityminlevel:
                                self._adminPlugin.warnClient(x, '%s ^3connects with your guid, same IP'%client.exactName, None, False, '', 60)
                                client.kick("Double Guid - Same IP",  None)
                        
                        if x.ip != client.ip:
                            
                            if client.maxLevel >= self._immunityminlevel:
                                
                                x.message("%s ^3connects with your guid and IP Different"%(client.exactName))
                                x.message("^3Please Quickly Contact the Server Administrator")
                                x.message("^3You will lose your level and be kicker")
                                
                                client.kick("Admin Double Guid - IP Different",  None)
                                
                                self.tgroups()

                                try:

                                    group = clients.Group(keyword=self.rgkeyword)
                                    group = self.console.storage.getGroup(group)
                
                                except:
                                    self.console.write('Error change level!') 
                    
                                x.setGroup(group)
                                x.save()
                                
                                thread.start_new_thread(self.pause, (x,))
                            
                            else:

                                self._adminPlugin.warnClient(x, '%s ^3connects with your guid, IP Different'%client.exactName, None, False, '', 60)
                                client.kick("Double Guid - IP Different",  None)

    def cmd_doubleguid(self, data, client, cmd=None):
        
        """\
        activate / deactivate doubleguid 
        """
        
        if data:
            
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
        
            if self._pluginactived == 'on':

                client.message('^3DoubleGuid ^2activated^7')

            if self._pluginactived == 'off':

                client.message('^3DoubleGuid ^1deactivated^7')

            client.message('!doubleguid <on / off>')
            return

        if input[0] == 'on':

            if self._pluginactived != 'on':

                self._pluginactived = 'on'
                message = '^2activated'

            else:

                client.message('^3DoubleGuid is already ^2activated^7') 

                return False

        if input[0] == 'off':

            if self._pluginactived != 'off':

                self._pluginactived = 'off'
                message = '^1deactivated'

            else:
                
                client.message('^3DoubleGuid is already ^1disabled^7')                

                return False

        client.message('^3DoubleGuid %s^7'%(message))

    def tgroups(self):

        self.rgkeyword = None
    
        cursor = self.console.storage.query("""
        SELECT *
        FROM groups n 
        """)

        if cursor.EOF:
  
            cursor.close()            
            
            return False

        while not cursor.EOF:
        
            sr = cursor.getRow()
            gkeyword = sr['keyword']
            glevel= sr['level']
       
            if int(glevel) == 0:
                self.rgkeyword = gkeyword

            cursor.moveNext()
    
        cursor.close()
        
        return

    def pause(self, xclient):

        time.sleep(30)

        xclient.kick("Admin Double Guid - IP Different",  None)
