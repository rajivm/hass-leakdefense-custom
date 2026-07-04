DOMAIN = "lds"
BASE_URL = "https://www.catchaleak.com/rest/v1/api"
CONF_DEVICE_ID = "device_id"
DEFAULT_SCAN_INTERVAL = 20  # seconds — matches API UpdateInterval
USER_AGENT = "leakdefense/116 CFNetwork/3826.600.41 Darwin/24.6.0"

SCENE_HOME = "HOME"
SCENE_STANDBY = "STANDBY"
SCENE_AWAY = "AWAY"

SCENE_API_TO_LABEL = {
    SCENE_HOME: "Home",
    SCENE_STANDBY: "Standby",
    SCENE_AWAY: "Away",
}
SCENE_LABEL_TO_API = {label: api for api, label in SCENE_API_TO_LABEL.items()}
SCENE_LABELS = list(SCENE_API_TO_LABEL.values())
