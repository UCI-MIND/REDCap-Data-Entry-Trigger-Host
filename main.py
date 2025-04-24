import logging
import random

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Request

import triggers
import triggers_setup
import utils

# Only used when this script is ran directly
PORT = 8000  # Default: 8000

# Parameters that we expect to receive in every POST request from REDCap (should work with any project)
# Used to defend against bogus POST requests that this server may receive
ESSENTIAL_POST_PARAMETERS = {
    "redcap_url",
    "project_url",
    "project_id",
    "username",
    "record",
    "instrument",
}

# Disable default API docs
app = FastAPI(openapi_url=None)

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("[{asctime} {levelname}] {message}", style="{")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

logger.info(f"Running on: {utils.get_system_information()}")
logger.info(f"System time: {utils.timestamp_now()} ({utils.get_system_timezone()})")

TRIGGERS: list[triggers_setup.DataEntryTrigger] = triggers_setup.load_triggers()
logger.info(
    f"Loaded {len(TRIGGERS)} triggers from triggers.json: {', '.join([t.name for t in TRIGGERS])}"
)
for trigger_obj in TRIGGERS:
    if not hasattr(triggers, trigger_obj.name):
        logger.warning(f"'{trigger_obj.name}' not defined/implemented in triggers.py")


@app.post("/")
async def process_post_data(
    request: Request, background_tasks: BackgroundTasks
) -> dict:
    # Load data from request object (requires "python-multipart" package)
    form_data_raw = await request.form()
    form_data = dict(form_data_raw)

    # Transforms ("123.456.789", 4040) to "123.456.789:4040":
    client = ":".join([str(i) if type(i) is not str else i for i in request["client"]])

    # All items in request object (for dev/debugging):
    logger.debug(f"{client} ( {', '.join([f'{k}={v}' for k, v in request.items()])} )")

    # Check if this request is missing expected POST data
    # (if it is, someone is snooping and trying to see how the server responds)
    if any((p for p in ESSENTIAL_POST_PARAMETERS if p not in form_data)):
        logger.warning(f"{client} Denied: {form_data}")
        return {}

    # Load data
    # Build Python dict of data that we care about (accounts for not-guaranteed trigger parameters)
    # This dict is used to check which trigger functions to run
    redcap_data = dict()
    redcap_data["redcap_url"] = form_data["redcap_url"]
    # redcap_data["project_url"] = form_data["project_url"]
    redcap_data["project_id"] = form_data["project_id"]
    redcap_data["username"] = form_data["username"]
    redcap_data["record"] = form_data["record"]
    redcap_data["instrument"] = form_data["instrument"]

    # Not guaranteed to be in DET POST data:
    redcap_data["dag"] = form_data.get("redcap_data_access_group", "")
    redcap_data["event_name"] = form_data.get("redcap_event_name", "")
    redcap_data["repeat_instance"] = int(form_data.get("redcap_repeat_instance", "0"))
    redcap_data["repeat_instrument"] = form_data.get("redcap_repeat_instrument", "")

    logger.info(
        f"{client} {redcap_data['username']}: {redcap_data['redcap_url']} PID {redcap_data['project_id']}, record {redcap_data['record']}, '{redcap_data['instrument']}'"
    )

    # Process data
    # Could optimize for large installations here if you have hundreds of triggers (see README)
    task_ids = []
    for trigger_obj in TRIGGERS:
        if set(trigger_obj.comparison_dict.items()).issubset(redcap_data.items()):
            if hasattr(triggers, trigger_obj.name):
                logger.debug(f"{client} Triggering function: {trigger_obj.name}()")
                trigger_func = getattr(triggers, trigger_obj.name)
                # Generate random ID for logging concurrent tasks
                task_id = f"{random.getrandbits(32):08x}"  # "apply 0-padding to make the ID 8 chars long in hex"
                task_ids.append((task_id, trigger_obj.name))
                # https://fastapi.tiangolo.com/tutorial/background-tasks/
                background_tasks.add_task(trigger_func, task_id, form_data)
            else:
                logger.warning(
                    f"{client} Trigger function '{trigger_obj.name}' not found"
                )
    logger.info(
        f"{client} This request invoked {len(task_ids)} triggers: {', '.join([f'{name}({taskid})' for taskid, name in task_ids])}"
    )
    return {}


if __name__ == "__main__":
    uvicorn.run(app, port=PORT)
