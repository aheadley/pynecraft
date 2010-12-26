class Wrapper(object):
    def __init__(self):
        self._plugins = {}
        self._commands = {}
        self._events = {}
        self._file_dir = ''
        self._server_connection = None
        self._keep_running = True

    def init(self):
        pass

    def log(self, source, action, info):
        message = '[%s] (%s): %s' % (source, action, '|'.join(info))
        print message

    def register_plugin(self, plugin):
        plugin.init()
        self._plugins[plugin.name] = plugin

    def add_command(self, command, **command_options):
        self._commands[command] = command_options

    def register_command(self, command, callback):
        try:
            self._commands[command].append({
                'caller':caller,
                'callback':callback,
            })
        except KeyError:
            self._commands[command] = [{
                'caller':caller,
                'callback':callback,
            }]

    def unregister_command(self, command):
        pass

    def add_event(self, event_name, event_patterns):
        try:
            self._events[event_name]['patterns'].extend(map(re.compile, event_patterns))
        except KeyError:
            self._events[event_name] = {
                'patterns' :map(re.compile, event_patterns) }

    def register_event(self, event_name, callback):
        pass

    def unregister_event(self, event_name):
        pass

    def get_file_lines(self, relative_file):
        with open(os.path.join(self._file_dir, relative_file)) as f:
            lines = map(lambda line: line.strip(), f)
        return lines

    def handle_event(self, event):
        pass