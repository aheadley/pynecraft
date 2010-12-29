import time
import subprocess
import select
import sys
import os.path
import re
import ConfigParser

import plugins
import events

class Wrapper(object):
    def __init__(self):
        self._config = {}
        self._plugins = {}
        self._commands = {}
        self._events = {}
        self._file_dir = ''
        self._server_connection = None
        self._server_start_time = None
        self._running = False

        self.add_event('command', events.basic_events['command'])
        self.register_event('command', self.dispatch_command)

        self.init()

    def __del__(self):
        self.stop()

    def _init_plugins(self):
        return
        for plugin in plugins:
            plugin(self)

    def _start_plugins(self):
        return
        for plugin in self._plugins:
            plugin.start()

    def _stop_plugins(self):
        return
        for plugin in self._plugins:
            plugin.stop()

    def _load_config(self):
        if os.path.exists(os.path.join(self._file_dir, 'config.ini')):
            config_file = os.path.join(self._file_dir, 'config.ini')
        else:
            config_file = os.path.join(self._file_dir, 'config-default.ini')
        config = ConfigParser.SafeConfigParser()
        config.read(config_file)
        self._config = {}
        for section in config.sections():
            self._config[section] = {}
            for option in config.options(section):
                self._config[section][option] = config.get(section,option)

    def _start_server(self):
        command = [
            'java',
            self._config['java']['extra_options'],
            '-Xms%s' % self._config['java']['heap_min'],
            '-Xmx%s' % self._config['java']['heap_max'],
            '-jar',
            self._config['java']['server_jar'],
            'nogui',
        ]
        self._server_connection = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE)
        self._server_outputs = [
            self._server_connection.stderr,
            self._server_connection.stdout,
            sys.stdin]
        self._server_inputs = []
        self._server_start_time = time.time()

    def _stop_server(self):
        if self._server_connection.poll() is None:
            self.raw_server_command('stop')
            self._server_connection.wait()
        self._server_connection = None

    def _run(self):
        while self._running:
            try:
                read_ready, write_ready, except_ready = select.select(
                    self._server_outputs,
                    self._server_inputs,
                    [], 1.0)
            except Exception:
                continue
            for sock in read_ready:
                line = sock.readline()
                print line
                if sock is sys.stdin:
                    self.log('stdin', line)
                    self.raw_server_command(line)
                else:
                    if not line:
                        self.stop()
                    else:
                        self.dispatch_event(line)

    def init(self):
        self._load_config()
        self._init_plugins()

    def start(self):
        if not self._running:
            self._running = True
            self._start_plugins()
            self._start_server()
            self._run()

    def stop(self):
        if self._running:
            self._stop_plugins()
            self._stop_server()
            self._running = False

    def log(self, source, action, info=[]):
        message = '[%s] (%s): %s' % (source, action.strip(), '|'.join(map(
            lambda line: line.strip(), info)))
        print message

    def register_plugin(self, plugin):
        self._plugins[plugin.name] = plugin

    def add_command(self, command, **command_options):
        self._commands[command] = command_options

    def register_command(self, command, callback):
        try:
            self._commands[command]['callbacks'].append(callback)
        except KeyError:
            self._commands[command]['callbacks'] = [callback]

    def unregister_command(self, command):
        try:
            del self._commands[command]
        except KeyError:
            pass

    def add_event(self, event_name, event_patterns):
        event_patterns = map(re.compile, event_patterns)
        try:
            self._events[event_name]['patterns'].extend(event_patterns)
        except KeyError:
            self._events[event_name] = {
                'patterns': event_patterns}

    def register_event(self, event_name, callback):
        try:
            self._events[event_name]['callbacks'].append(callback)
        except KeyError:
            self._events[event_name]['callbacks'] = [callback]

    def unregister_event(self, event_name):
        pass

    def get_file_lines(self, relative_file):
        with open(os.path.join(self._file_dir, relative_file)) as f:
            lines = map(lambda line: line.strip(), f)
        return lines

    def dispatch_command(self, player_name, command, args, **kwargs):
        try:
            for callback in self._commands[command]['callbacks']:
                callback(player_name, args)
        except KeyError:
            pass

    def dispatch_event(self, event_line):
        for event_name in self._events:
            for event_pattern in self._events[event_name]['patterns']:
                match = event_pattern.search(event_line)
                if match:
                    for callback in self._events[event_name]['callbacks']:
                        callback(**match.groupdict())
                    break

    def raw_server_command(self, command):
        self._server_connection.stdin.write(command.rstrip() + '\n')