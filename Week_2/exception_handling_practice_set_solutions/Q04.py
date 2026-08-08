def load_config(path):
    """Read and print each line of an application config file."""
    try:
        f = open(path, "r")
        for line in f:
            print(line.strip())
        f.close()
    except FileNotFoundError:
        print(f'{path} file doesnt exist')
    except (OSError, IOError):
        print(f'error occured while getting the configs')
    finally:
        print('config load attempt finished')
    
load_config("app.config")
load_config("does_not_exist.cfg") 