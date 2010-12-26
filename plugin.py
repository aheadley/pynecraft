class Plugin(object):
    def __init__(self, wrapper):
        self._wrapper = wrapper
        self._wrapper.register_plugin(self)

    def init(self):
        self.name = 'Plugin'

    def add_command(self, command, public=False, help_text=None, callback=None):
        self._wrapper.add_command(command, public, help_text)
        if callback is not None:
            self.register_command(command, callback)

    def register_command(self, command, callback):
        self._wrapper.register_command(command, callback)

    def unregister_command(self, command):
        self._wrapper.unregister_command(command)
        
    def add_event(self, event_name, event_patterns, callback=None):
        self._wrapper.add_event(event_name, event_patterns)
        if callback is not None:
            self.register_event(event_name, callback)

    def register_event(self, event_name, callback):
        self._wrapper.register_event(event_name, callback)

    def unregister_event(self, event_name):
        self._wrapper.unregister_event(event_name)

    def log(self, action, *info):
        self._wrapper.log(self.name, action, info)

    def raw_server_command(self, server_command):
        self._wrapper.raw_server_command(server_command)

    def tell(self, player, message, wrap_message=True):
        if player not in self.get_players():
            raise Pynecraft_Message_Exception(player, 'Not Online')
        else:
            self.log('tell', player, message)
            if wrap_message:
                for line in self._wrap_message(message):
                    self.raw_server_command('tell %s %s' % (player, line))
            else:
                self.raw_server_command('tell %s %s' % (player, message))

    def say(self, message, wrap_message=True):
        self.log('say', message)
        if wrap_message:
            for line in self._wrap_message(message):
                self.raw_server_command('say %s' % (player, line))
        else:
            self.raw_server_command('say %s' % (player, message))
        

    def ban_player(self, player, reason=None):
        if player in self.get_banned_players():
            raise Pynecraft_Ban_Exception(player, 'Already Banned')
        else:
            self.log('ban_player', player, reason)
            if reason is not None:
                self.say('Banning player (%s) because: %s' % (player, reason))
            self.raw_server_command('ban %s' % (player))

    def pardon_player(self, player):
        if player not in self.get_banned_players():
            raise Pynecraft_Ban_Exception(player, 'Not Banned')
        else:
            self.log('pardon', player)
            self.raw_server_command('pardon %s' % (player))

    def is_player_banned(self, player):
        return player in self.get_banned_players()

    def get_banned_players(self):
        return self._wrapper.get_file_lines('banned-players.txt')

    def ban_ip(self, ip, reason=None):
        if ip in self.get_banned_ips():
            raise Pynecraft_Ban_Exception(ip, 'Already Banned')
        else:
            self.log('ban_ip', ip, reason)
            if reason is not None:
                self.say('Banning IP (%s) because: %s' % (ip, reason))
            self.raw_server_command('ban-ip %s' % (ip))

    def pardon_ip(self, player):
        if ip not in self.get_banned_ips():
            raise Pynecraft_Ban_Exception(ip, 'Not Banned')
        else:
            self.log('pardon_ip', ip)
            self.raw_server_command('ban-ip %s' % (ip))

    def is_ip_banned(self, ip):
        return ip in self.get_banned_ips()

    def get_banned_ips(self):
        return self._wrapper.get_file_lines('banned-ips.txt')

    def kick(self, player, reason=None):
        if not self.is_player_online(player):
            raise Pynecraft_Kick_Exception(player, 'Not Online')
        else:
            self.log('kick', player, reason)
            if reason is not None:
                self.say('Kicking player (%s) because: %s')
            self.raw_server_command('kick %s' % (player))

    def op(self, player):
        if self.is_op(player):
            raise Pynecraft_Op_Exception(player, 'Already An Op')
        else:
            self.log('op', player)
            self.raw_server_command('op %s')

    def deop(self, player):
        if not self.is_op(player):
            raise Pynecraft_Op_Exception(player, 'Not An Op')
        else:
            self.log('deop', player)
            self.raw_server_command('deop %s')

    def is_op(self, player):
        return player in self.get_ops()

    def get_ops(self):
        return self._wrapper.get_file_lines('ops.txt')

    def give(self, player, item_id, amount=1):
        amount = max(amount,1)
        if not self.is_player_online(player):
            raise Pynecraft_Give_Exception(player, 'Not Online')
        elif not self._validate_item_id(item_id):
            raise Pynecraft_Item_Exception(item_id)
        else:
            stack_size = 64
            stacks,leftover = divmod(amount, stack_size)
            self.log('give', player, item_id, amount)
            for stack in stacks:
                self.raw_server_command('give %s %i %i' % (player, item_id, stack_size))
            if leftover is not 0:
                self.raw_server_command('give %s %i %i' % (player, item_id, leftover))

    def tp(self, src_player, dest_player):
        if not self.is_player_online(src_player):
            raise Pynecraft_Teleport_Exception(src_player, 'Not Online')
        elif not self.is_player_online(dest_player):
            raise Pynecraft_Teleport_Exception(dest_player, 'Not Online')
        else:
            self.log('tp', src_player, dest_player)
            self.raw_server_command('tp %s %s' % (src_player, dest_player))

    def stop(self):
        self.raw_server_command('stop')

    def set_saving(self, enable=True):
        if enable:
            self.raw_server_command('save-on')
        else:
            self.raw_server_command('save-off')

    def save(self):
        self.raw_server_command('save-all')

    def is_player_online(self, player):
        return player in self.get_online_players()

    def get_online_players(self):
        pass