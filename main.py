from requests import post
from json import load



def get_config() -> dict:
    with open("config.json", "r") as f:
        config = load(f)
        
    if not config.get("path_to_autobot_directory"):
        raise Exception("path_to_autobot_directory not found in config.json")
    
    if not config["path_to_autobot_directory"].endswith("/"):
        config["path_to_autobot_directory"] = config["path_to_autobot_directory"] + "/"
    
    return config


def get_ecosystem_file() -> dict:
    config = get_config()
    autobot_directory = config["path_to_autobot_directory"]
    
    with open(autobot_directory + "ecosystem.json", "r") as f:
        ecosystem = load(f)
    
    return ecosystem
    

def get_pricelist_path() -> str:
    config = get_config()
    autobot_directory = config["path_to_autobot_directory"]
    
    ecosystem = get_ecosystem_file()
    ecosystem_apps = ecosystem["apps"]
    
    account_name = str()
    
    for app in ecosystem_apps:
        app_env = app["env"]
        if config.get("steam_account_name") == app_env["STEAM_ACCOUNT_NAME"]:
            account_name = app_env["STEAM_ACCOUNT_NAME"]
            break
    
    if not account_name:
        raise Exception("Steam account name not found in ecosystem.json, please check config.json")
    
    return f"{autobot_directory}files/{account_name}/pricelist.json"


def get_pricelist(pricelist_path) -> dict:
    with open(pricelist_path, "r") as f:
        pricelist = load(f)
        
    return pricelist


def get_skus(pricelist: dict) -> list:
    skus = list()
    
    for sku in pricelist:
        skus.append(sku) if sku not in skus else None
    
    return skus


def post_skus(skus: list) -> None:
    if not skus:
        raise Exception("No SKUs found in pricelist.json")
    
    config = get_config()
    prioritize_url = config["pricer_url"]
    access_token = config["access_token"]
    
    if not prioritize_url:
        raise Exception("prioritize_url not found in config.json")
    
    if not access_token:
        raise Exception("access_token not found in config.json")
    
    if prioritize_url.endswith("/"):
        prioritize_url = prioritize_url[:-1]
    
    prioritize_url = prioritize_url + "/priority/add/"

    data = {
        "sku_list": skus
    }
    
    req = post(prioritize_url, params={"token": access_token}, json=data)
    print(req.json())

def main() -> None:
    pricelist_path = get_pricelist_path()
    pricelist = get_pricelist(pricelist_path)
    skus = get_skus(pricelist)
    post_skus(skus)


if __name__ == "__main__":
    main()
