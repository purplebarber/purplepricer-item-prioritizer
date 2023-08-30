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
    

def get_pricelist_path(ecosystem: dict, account_name_to_check: str) -> str:
    config = get_config()
    autobot_directory = config["path_to_autobot_directory"]

    if not ecosystem:
        ecosystem = get_ecosystem_file()

    if not ecosystem.get("apps"):
        raise Exception("apps not found in ecosystem.json")

    ecosystem_apps = ecosystem["apps"]
    
    account_name = str()
    
    for app in ecosystem_apps:
        app_env = app["env"]
        if account_name_to_check == app_env["STEAM_ACCOUNT_NAME"]:
            account_name = app_env["STEAM_ACCOUNT_NAME"]
            break
    
    if not account_name:
        raise Exception(f"Steam account {account_name_to_check} not found in ecosystem.json, please check config.json")
    
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


def post_skus(skus: list, prioritize_url: str, access_token: str) -> tuple:
    if not skus:
        raise Exception("No SKUs found in pricelist.json")

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
    return (req.json(), req.status_code)


def main() -> None:
    config, ecosystem = get_config(), get_ecosystem_file()
    print_events = config["print_events"]

    for account_name in config.get("steam_account_name"):
        pricelist_path = get_pricelist_path(ecosystem, account_name)

        pricer_url = str()
        access_token = str()

        for app in ecosystem["apps"]:
            if not app["env"]["STEAM_ACCOUNT_NAME"] == account_name:
                continue
            pricer_url = app["env"]["CUSTOM_PRICER_URL"]
            access_token = app["env"]["CUSTOM_PRICER_API_TOKEN"]

        if not pricer_url:
            raise Exception(f"pricer_url not found in ecosystem.json for {account_name}")

        if not access_token:
            raise Exception(f"access_token not found in config.json for {account_name}")

        pricelist = get_pricelist(pricelist_path)
        skus = get_skus(pricelist)
        post_response = post_skus(skus, pricer_url, access_token)

        (print("Response:", post_response[0]), print("Status Code:", post_response[1])) if print_events else None


if __name__ == "__main__":
    main()
