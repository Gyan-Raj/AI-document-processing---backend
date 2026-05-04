def build_folder_structure(contracts, configs):
    folder_map = {}

    # contracts
    for c in contracts:
        folder = c["folder_name"] or ""

        if folder not in folder_map:
            folder_map[folder] = []

        folder_map[folder].append({
            "fileName": c["contract_name"],
            "type": "contract",
            "id": c["id"]
        })

    # configs
    for cfg in configs:
        folder = cfg["folder_name"] or ""

        if folder not in folder_map:
            folder_map[folder] = []

        folder_map[folder].append({
            "fileName": cfg["config_name"],
            "type": "config",
            "id": cfg["id"]
        })

    return [
        {"folderName": folder, "files": files}
        for folder, files in folder_map.items()
    ]

