import yaml

def load_config(config_path:str="config/config.yaml") -> dict:
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        print(f"Configuration loaded from {config_path}")
        if not config:
            raise ValueError("Configuration file is empty or invalid.")
        print(config)
      
    return config

load_config("config/config.yaml")
