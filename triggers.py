# import asyncio
import logging

import redcap

# Implement trigger functions here!!! Their names should match the names of triggers in triggers.json
# These trigger functions are all fed 2 arguments from main.py:process_post_data():
#   * task_id: random hex string generated in main.py
#   * form_data: the actual POST data from REDCap

# If "async":   Starlette will run them asynchronously
#               (better for waiting on IO- or network-bound operations)
# If defined as regular functions:  Starlette will run them in separate threads
#                                   (better for waiting on CPU-bound operations)

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("[{asctime} {levelname}] [triggers] {message}", style="{")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def dev_trigger_test_instrument(task_id: str, form_data: dict) -> None:
    """A sample trigger function that runs when a specific data collection instrument is completed."""
    instrument = form_data["instrument"]
    instrument_complete = f"{instrument}_complete"
    if instrument_complete in form_data and form_data[instrument_complete] == "2":
        logger.debug(
            f"{task_id} This trigger is running because '{instrument}' was completed"
        )
        # task = asyncio.create_task(redcap.simulate_network_request(5, f"{task_id}-form2"))
        # await task
        redcap.simulate_network_request(1, task_id)
    else:
        logger.debug(
            f"{task_id} ERROR: '{instrument}' data is not marked as 'complete'!"
        )


def dev_trigger_test_username(task_id: str, form_data: dict) -> None:
    """A sample trigger function that runs when a specific user saves a record."""
    logger.debug(
        f"{task_id} This trigger is running because '{form_data['username']}' saved a record",
    )
    redcap.simulate_network_request(1, task_id)


def dev_trigger_test_record_id(task_id: str, form_data: dict) -> None:
    """A sample trigger function that runs when a specific record is saved."""
    logger.debug(
        f"{task_id} This trigger is running because record '{form_data['record']}' was saved",
    )
    redcap.simulate_network_request(1, task_id)


def dev_trigger_test_survey_respondent(task_id: str, form_data: dict) -> None:
    """A sample trigger function that runs when an anonymous survey user completes a survey."""
    # For anonymous survey respondents, this will always be true:
    # form_data["username"] == "[survey respondent]"
    logger.debug(
        f"{task_id} This trigger is running because a survey respondent completed the survey '{form_data['instrument']}' (record ID={form_data['record']})",
    )
    redcap.simulate_network_request(1, task_id)


def dev_trigger_test_dag(task_id: str, form_data: dict) -> None:
    """A sample trigger function that runs when a record in a specific Data Access Group is saved."""
    logger.debug(
        f"{task_id} This trigger is running because a record in the Data Access Group '{form_data['redcap_data_access_group']}' was saved! (record ID={form_data['record']})",
    )
    redcap.simulate_network_request(1, task_id)


def dev_trigger_test_event(task_id: str, form_data: dict) -> None:
    """A sample trigger function that runs when a record in a specific longitudinal event is saved."""
    logger.debug(
        f"{task_id} This trigger is running because a record in the longitudinal event '{form_data['redcap_event_name']}' was saved! (record ID={form_data['record']})",
    )
    redcap.simulate_network_request(1, task_id)


def dev_trigger_test_rpt(task_id: str, form_data: dict) -> None:
    """A sample trigger function that runs when a specific instance of a repeating instrument is saved."""
    logger.debug(
        f"{task_id} This trigger is running because instance {form_data['redcap_repeat_instance']} of repeating instrument '{form_data['redcap_repeat_instrument']}' was saved! (record ID={form_data['record']})",
    )
    redcap.simulate_network_request(1, task_id)


def dev_trigger_test_proj(task_id: str, form_data: dict) -> None:
    """A sample trigger function that runs when any record within a specific project is saved."""
    logger.debug(
        f"{task_id} This trigger is running on a project-wide scope! Be careful with this one!! (PID={form_data['project_id']})",
    )
    # task = asyncio.create_task(redcap.simulate_network_request(7, f"{task_id}-proj"))
    # await task
    redcap.simulate_network_request(2, task_id)
