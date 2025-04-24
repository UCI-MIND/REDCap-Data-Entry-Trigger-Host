import json
from dataclasses import dataclass, field

# Parameters that are required to be in every trigger in triggers.json
# Used to ensure that every trigger has at least these parameters defined;
# the server will not start if any of these are missing in any trigger
ESSENTIAL_TRIGGER_PARAMETERS = [
    "name",
    "redcap_url",
    "project_id",
]


@dataclass
class DataEntryTrigger:
    name: str

    # Data we expect to get from REDCap with *every* DET POST request
    redcap_url: str
    project_id: str
    username: str = ""
    record: str = ""
    instrument: str = ""

    # Data that *isn't guaranteed* from every REDCap DET POST request
    # (depends on REDCap project configuration)
    dag: str = ""
    event_name: str = ""
    repeat_instance: int = -1  # Default = -1, instance 0 could be valid
    repeat_instrument: str = ""

    # Cache of trigger conditions; populated in __post_init__() method
    # Used to determine which trigger functions should be ran for a given DET POST request
    comparison_dict: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.comparison_dict["redcap_url"] = self.redcap_url
        self.comparison_dict["project_id"] = self.project_id
        if self.instrument:
            self.comparison_dict["instrument"] = self.instrument
        if self.username:
            self.comparison_dict["username"] = self.username
        if self.record:
            self.comparison_dict["record"] = self.record
        if self.dag:
            self.comparison_dict["dag"] = self.dag
        if self.event_name:
            self.comparison_dict["event_name"] = self.event_name
        if self.repeat_instance != -1:
            self.comparison_dict["repeat_instance"] = self.repeat_instance
        if self.repeat_instrument:
            self.comparison_dict["repeat_instrument"] = self.repeat_instrument


def load_triggers() -> list[DataEntryTrigger]:
    with open("./triggers.json") as infile:
        triggers_in: list[dict] = json.load(infile)
    result = []
    for json_tr in triggers_in:
        if any(
            [
                essential_key not in json_tr
                for essential_key in ESSENTIAL_TRIGGER_PARAMETERS
            ]
        ):
            raise ValueError(
                f"Missing essential keys in trigger definition; check triggers.json for this object:\n    {json_tr}"
            )
        det = DataEntryTrigger(**json_tr)
        result.append(det)
    return result
