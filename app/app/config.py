from vyper import v

def get_config():
    v.set_config_name('pruner_config')
    v.add_config_path('.')
    v.watch_config()    
    conf=v.read_in_config()
    return conf

