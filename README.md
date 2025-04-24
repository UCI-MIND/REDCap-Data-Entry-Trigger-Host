# REDCap Data Entry Trigger Host
FastAPI server to ingest POST requests from REDCap Data Entry Trigger events

# Details

REDCap projects can be configured to send record metadata to a server of your choice when any record is saved using a setting called "Data Entry Trigger" (DET). To enable this for your own projects, go to any REDCap project's "Project Setup" page, then under the "Enable optional modules and customizations" section, click "Additional customizations", and scroll down to "Data Entry Trigger". In the "URL of website" box, input the URL that leads to your deployment of this server.

This FastAPI server is intended to be a self-hosted ingestion point for these DET events, acting as a sort of filter to react to DET events that contain a specific combination of data. **Python >= 3.12.10** is recommended.

The files `triggers.json` and `triggers.py` should be edited in tandem to define triggers for your REDCap forms and/or projects ahead of time. See `triggers.py` for Pythonic details on implementing a trigger function.
* Since this server only receives metadata about saved records, trigger functions should use the REDCap API to obtain and process actual data pertaining to each updated record.

List of supported parameters to define triggers in `triggers.json`:

| Parameter name      | Required? | Description |
|---------------------|:---------:|-------------|
| `name`              |     ✅     | The name of this trigger. Should have a function with a matching name in `triggers.py`. |
| `redcap_url`        |     ✅     | URL of the REDCap site that will invoke this trigger. Could be useful if your institute manages multiple REDCap sites. |
| `project_id`        |     ✅     | Numeric project ID (PID) of the DET-enabled REDCap project that the saved record exists in. |
| `record`            |     ❌     | Record ID of the saved record. |
| `instrument`        |     ❌     | Name of the saved record's Data Collection Instrument as it appears in the REDCap API (check the project's Codebook or API Playground). |
| `username`          |     ❌     | Username of the REDCap user that saved the record. Value should be `[survey respondent]` to allow this trigger to be invoked by anonymous survey users. |
| `dag`               |     ❌     | Name of the data access group that the saved record belongs to. Only applies if the record belongs to a data access group. |
| `event_name`        |     ❌     | Name of the longitudinal event that the saved record belongs to. Only applies if the project has longitudinal events enabled. |
| `repeat_instrument` |     ❌     | Name of the saved record's repeating Data Collection Instrument. Only applies if the saved record belongs to a repeating instrument. |
| `repeat_instance`   |     ❌     | Number of the current instance of the saved record. Only applies if the saved record belongs to a repeating instrument _or_ repeating event. |

## Trigger examples

These examples showcase basic use cases for the parameters described above, but keep in mind that any number of optional parameters can be specified for even greater granularity in defining your triggers.

```json
{
    "name": "dev_trigger_test_proj",
    "redcap_url": "https://redcap.example.edu/",
    "project_id": "18"
}
```

This is the bare minimum trigger that can be defined and recognized by this server, but is also the most dangerous. The trigger function named `dev_trigger_test_proj` will be invoked when _any instrument_ is saved in project `18` by _any user_, in _every event_ (for longitudinal projects), and for _every repeating instrument/instance_ (if project `18` has that feature enabled). This set of trigger conditions could cause the FastAPI server to process lots of requests and should be implemented carefully, especially if this is a high-traffic REDCap project!

```json
{
    "name": "dev_trigger_test_instrument",
    "redcap_url": "https://redcap.example.edu/",
    "project_id": "18",
    "instrument": "form_2"
}
```

The trigger function named `dev_trigger_test_instrument` will be invoked when the Data Collection Instrument called `form_2` is saved in project `18`. Note that the trigger definition here doesn't specify if the instrument is _completed_; that is left as an implementation detail for the Python function: should something different happen if the record is completed (green/2) vs. unverified (yellow/1) vs. incomplete (red/0)?

```json
{
    "name": "dev_trigger_test_username",
    "redcap_url": "https://redcap.example.edu/",
    "project_id": "18",
    "username": "jsmith"
}
```

The trigger function named `dev_trigger_test_username` will be invoked when the user `jsmith` saves any record in project `18`. Could be useful for user accounts that require special attention, like production API users or specific people in your institute.

```json
{
    "name": "dev_trigger_test_record_id",
    "redcap_url": "https://redcap.example.edu/",
    "project_id": "18",
    "record": "99"
}
```
The trigger function named `dev_trigger_test_record_id` will be invoked when any form associated with record `99` in project `18` is saved. If the project is configured with longitudinal events or repeating instruments, this trigger will be invoked when any form in record `99` is saved during each longitudinal event or repeating instance.

```json
{
    "name": "dev_trigger_test_survey_respondent",
    "redcap_url": "https://redcap.example.edu/",
    "project_id": "18",
    "username": "[survey respondent]",
    "instrument": "form_1"
}
```

The trigger function named `dev_trigger_test_survey_respondent` will be invoked when the Data Collection Instrument called `form_1` is saved in project `18` by an anonymous survey user. This implies that the REDCap project has already been configured with surveys enabled on `form_1`. If the `instrument` field was omitted in this example, _every_ respondent across _every_ survey-enabled instrument in project `18` would invoke this trigger.

```json
{
    "name": "dev_trigger_test_dag",
    "redcap_url": "https://redcap.example.edu/",
    "project_id": "18",
    "dag": "controls"
}
```

The trigger function named `dev_trigger_test_dag` will be invoked when any record in the Data Access Group `controls` is saved in project `18`.

```json
{
    "name": "dev_trigger_test_event",
    "redcap_url": "https://redcap.example.edu/",
    "project_id": "18",
    "event_name": "event_1_arm_1"
}
```

The trigger function named `dev_trigger_test_event` will be invoked when any record in the longitudinal event `event_1_arm_1` is saved in project `18`. This implies that the REDCap project has longitudinal events enabled in the first place.

```json
{
    "name": "dev_trigger_test_rpt",
    "redcap_url": "https://redcap.example.edu/",
    "project_id": "18",
    "repeat_instance": 2,
    "repeat_instrument": "repeating_form"
}
```

The trigger function named `dev_trigger_test_rpt` will be invoked when the second instance of the repeating instrument named `repeating_form` is saved in project `18`. This implies that the REDCap project has repeating instruments enabled in the first place.

# Deployment

These basic instructions assume you would like to deploy the server on a Linux system. Ideally, you should have a domain name and SSL certificate installed for this server so traffic is encrypted in transit between your REDCap server and this DET endpoint. This is especially important if, to quote the REDCap documentation, "the names of your records (i.e. the values of your first field) are considered identifiers (e.g., SSN, MRN, name)".

First, get the code by cloning this repository. There are several ways to do this:
* Download this repository as a ZIP file with your web browser and use an FTP client to transfer it to your server, then use a shell command like `unzip` to extract it
* Use the `wget` shell command on your server machine to download the ZIP directly to the server, then use `unzip` to extract it
* Use `git clone` on your server machine, which will completely bypass extracting a ZIP file

Once you have the server code extracted somewhere on your server, you should now decide _how_ you want to serve it. **We recommend Docker**, but you may be in a situation where hosting it on a dedicated system would work best for you, so we provide some guidance here for both:

## Docker

The files `start_container.sh` and `Dockerfile` are related to Docker deployment, and we encourage looking at these files beforehand to verify what they do. [If you already have Docker installed](https://docs.docker.com/engine/install/), starting the FastAPI server is just a few commands:

```sh
chmod +x ./start_container.sh
./start_container.sh
```

Please note that the ports in `start_container.sh` and `Dockerfile` should match!
* The port specified in `start_container.sh` will map a port on your system to the same port on the Docker container
* The port specified in the final `CMD` directive in `Dockerfile` will determine which port the app will listen on

## Dedicated system

Running the server on a dedicated system (hardware or software/VM) requires manual steps that aren't too different from setting up a dev environment. Key points:
* The version of Python that comes with your Linux distro's package manager may not be sufficient to run this server. To fix this, you can create an alternate installation by [building the desired version of Python from source](https://docs.python.org/3/using/unix.html#building-python) (ideally making an `altinstall` so your system's Python installation is unaffected).
* You should still set up a virtual environment and install packages to that virtual environment.
* Use the Python binary _from the virtual environment_ to run the server script.
  * i.e. DO NOT start the server program with a command like `python main.py` (it will not work). Instead use something like `/path/to/.venv/bin/python main.py`, as the virtual environment's Python binary is able to access the packages installed in the virtual environment.

You can change the port the server listens on near the top of `main.py`.

This server uses [Uvicorn](https://www.uvicorn.org/) to serve the FastAPI ASGI app. You may want to consider using alternative web server tech to improve performance. More reading:

* https://fastapi.tiangolo.com/deployment/
* https://www.uvicorn.org/deployment/

# Development

## Windows

Run `setup.bat` to create and prepare a Python virtual environment for running this server locally.

## Mac/Linux

We don't have a setup script for you, but see the comments in `setup.bat` for equivalent commands.

## Sample POST data

To develop this FastAPI server, it is necessary to send it POST data that mimics the format sent by REDCap. There are many apps available that can send arbitrary POST data, but here are some suggestions:

* [Advanced REST Client](https://github.com/advanced-rest-client/arc-electron) - Graphical interface. Supports Windows, Mac, and Linux. To modify the POST request's Body content easier, select "application/x-www-form-urlencoded" from the dropdown instead of "Raw data".

* [curl](https://curl.se/) - Command-line interface. Should be preinstalled on macOS and can be installed easily on most Linux distros. Windows machines should have curl preinstalled too, but there is also a PowerShell cmdlet `Invoke-WebRequest` that does similar things.

* An actual REDCap project - we recommend setting up a practice project with DET enabled and pointing it to a "staging" deployment of this FastAPI server. This would most closely mimic a real production environment and can be used to test new features and specific edge cases.

Here is some starter data that you can send to a local instance of the FastAPI server using apps like Advanced REST Client or curl. Adjust to taste.

```
ADDRESS
http://127.0.0.1:8000

HEADERS
Content-Type: application/x-www-form-urlencoded
Accept: */*

BODY (Raw input)
redcap_url=https%3A%2F%redcap.example.edu%2F&project_url=https%3A%2F%redcap.example.edu%2Fredcap_v15.0.1%2Findex.php%3Fpid%3D18&project_id=18&username=jsmith&record=4&instrument=form_1&form_1_complete=2
```

## Implementation notes

### REDCap Data Entry Trigger documentation

REDCap documentation lists the following named parameters that can be sent to the DET endpoint:

> * `project_id` - The unique ID number of the REDCap project (i.e. the 'pid' value found in the URL when accessing the project in REDCap).
>
> * `username` - The username of the REDCap user that is triggering the Data Entry Trigger. Note: If it is triggered by a survey page (as opposed to a data entry form), then the username that will be reported will be '[survey respondent]'.
>
> * `instrument` - The unique name of the current data collection instrument (all your project's unique instrument names can be found in column B in the data dictionary).
>
> * `record` - The name of the record being created or modified, which is the record's value for the project's first field.
>
> * `redcap_event_name` - The unique event name of the event for which the record was modified (for longitudinal projects only).
>
> * `redcap_data_access_group` - The unique group name of the Data Access Group to which the record belongs (if the record belongs to a group).
>
> * `[instrument]_complete` - The status of the record for this particular data collection instrument, in which the value will be 0, 1, or 2. For data entry forms, 0=Incomplete, 1=Unverified, 2=Complete. For surveys, 0=partial survey response and 2=completed survey response. This parameter's name will be the variable name of this particular instrument's status field, which is the name of the instrument + '_complete'.
>
> * `redcap_repeat_instance` - The repeat instance number of the current instance of a repeating event OR repeating instrument. Note: This parameter is only sent in the request if the project contains repeating events/instruments *and* is currently saving a repeating event/instrument.
>
> * `redcap_repeat_instrument` - The unique instrument name of the current repeating instrument being saved. Note: This parameter is only sent in the request if the project contains repeating instruments *and* is currently saving a repeating instrument. Also, this parameter will not be sent for repeating events (as opposed to repeating instruments).
>
> * `redcap_url` - The base web address to REDCap (URL of REDCap's home page).
>   * i.e., https://redcap.example.edu/
>
> * `project_url` - The base web address to the current REDCap project (URL of its Project Home page).
>   * i.e., https://redcap.example.edu/redcap_v15.0.1/index.php?pid=XXXX

REDCap sends these attributes in POST data using the `application/x-www-form-urlencoded` format, which is the same as standard HTML forms. FastAPI expects JSON data by default (`application/json`), so we use Starlette's underlying `Request` class to arbitrarily read all these form parameters.

### Performance bottleneck with large amounts of predefined triggers

One potential performance bottleneck is how incoming REDCap POST data determines which trigger object/function to invoke (see the `for` loop in `main:process_post_data`). The current implementation scales linearly with the amount of trigger objects defined on the server in `triggers.json` (`O(num_of_trigger_objects)`). For installations that use a large amount of trigger functions, it would be better to reimplement this to scale better or differently.

* One previous iteration of this server used a key lookup system: on server startup, trigger objects are created and stored in a _dictionary_ whose keys are unique strings produced from trigger object data and whose values are the trigger objects themselves. When a REDCap DET event is processed, the server would use data from that DET event to generate keys for _every possible trigger_ that could be invoked. Every key would be checked for inclusion in this dictionary and, because dictionary lookup is fast, applicable trigger objects would be quickly found and scheduled to run. Because of the key generation step, this process scales at `O(2^num_of_optional_trigger_params)`, which isn't great, but would technically be constant and potentially smaller than the number of triggers for large installations (unless future REDCap updates add new data to DET events...). Sample code for key generation is provided below.
  ```python
    from itertools import chain, combinations

    def generate_keys(redcap_data: dict) -> list[str]:
        """Generates a list of keys using POST data received from a REDCap Data Entry Trigger event.
        This list consists of all essential conditions with every combination of optional conditions.
        Used to determine the trigger functions to be executed with this request."""
        essential_conditions = (redcap_data["redcap_url"], redcap_data["project_id"])
        optional_conditions = (
            redcap_data["username"],
            redcap_data["record"],
            redcap_data["instrument"],
            redcap_data["dag"],
            redcap_data["event_name"],
            str(redcap_data["repeat_instance"]),
            redcap_data["repeat_instrument"],
        )
        # Adding a new optional parameter results in *doubling* the amount of keys generated here!!
        result = []
        # Generate powerset of an iterable: https://stackoverflow.com/a/1482316
        for combination in chain.from_iterable(
            combinations(optional_conditions, r)
            for r in range(len(optional_conditions) + 1)
        ):
            # String created here should match keys for trigger functions created on server startup
            # Up to you how to implement this
            result.append("|".join(essential_conditions + combination))
        return result
  ```
  * The minimum amount of triggers to consider implementing this is about **128**. This number doesn't account for the overhead of generating the keys on startup (per trigger) and at runtime (per incoming request) and should probably be a bit higher.
    * For example: if your installation has 300 different trigger functions, implementing this would scale your server's performance better because 128 keys would be generated, iterated through, and checked for validity _per DET event_. In contrast, using the default system would mean 300 trigger objects would be iterated through _per DET event_ to find applicable triggers.

### Alternative API design

Another way to structure a DET ingestion server is to build specific API endpoint functions per project and use project-specific function parameters ([see here](https://fastapi.tiangolo.com/tutorial/request-forms/)), but our intention with this server is to be more flexible and allow multiple REDCap projects to use the same URL for DET events. An sample based on FastAPI's documentation is below:

```python
from typing import Annotated

from fastapi import FastAPI, Form

# For projects where you can expect specific variables from DET events, you can also
# declare expected POST parameters in the function signature without using a Request
# object. This would expose the parameters in the FastAPI /docs endpoint, so be careful!

@app.post("/project1form1")
async def project1form1(
    redcap_url: Annotated[str, Form()],
    project_url: Annotated[str, Form()],
    project_id: Annotated[str, Form()],
    username: Annotated[str, Form()],
    record: Annotated[str, Form()],
    instrument: Annotated[str, Form()],
    form_1_complete: Annotated[str, Form()],
) -> dict:
    ...
```

# Funding

To support our work and ensure future opportunities for development, please acknowledge the software and funding.
The project was funded by The University of California, Irvine's Institute for Memory Impairments and Neurological Disorders (UCI MIND) grant, P30AG066519.
