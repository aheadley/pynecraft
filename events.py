tokens = {
    'time_stamp': r'^(?P<time_stamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
    'log_level': r'\[(?P<log_level>[A-Z]+)\]',
    'player_name': r'\b(?P<player_name>\w+)\b',
    'player_varname': r'\b(?P<player_%s>\w+)\b',
    'ip_address':  r'\b(?P<ip_address>(?:\d{1,3}\.){3}\d{1,3})\b',
}

basic_events = {
    'event_type': ['event_patterns'],
    'tell_message': [
        ' '.join([
            tokens['time_stamp'],
            tokens['log_level'],
            r'§7' + tokens['player_varname'] % 'src',
            'whispers (?P<message>.*) to',
            tokens['player_varname'] % 'dest'] + '$')],
    'chat_message': [
        ' '.join([
            tokens['time_stamp'],
            tokens['log_level'],
            tokens['player_name'],
            r'(?P<message>.*)$'])],
    'console_chat_message': [
        ' '.join([
            tokens['time_stamp'],
            tokens['log_level'],
            r'\[CONSOLE\]',
            '(?P<message>.*)$'])],
    'command': [
        ' '.join([
            tokens['time_stamp'],
            tokens['log_level'],
            tokens['player_name'],
            'tried command:',
            '(?P<command>\w+) ?(?P<args>.*)$']),
        ' '.join([
            tokens['time_stamp'],
            tokens['log_level'],
            tokens['player_name'],
            'issued server command:',
            '(?P<command>\w+) ?(?P<args>.*)$'])],
}