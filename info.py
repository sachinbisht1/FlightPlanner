"""All information related to Botlab dynamics 3d mapping survey project."""
import os
APP_NAME = "3d Mapping"

APP_SUMMARY = """

Botlab Dynamics 3d-Mapping recce flight planner backend API

"""

APP_DESCRIPTION = """

3d Mapping recce flight planner software backend api which was integrated with aws
dynamodb and s3.

"""

APP_CONTACT = {
    "name": os.environ.get('BOTLAB_DYNAMICS'),
    "url": os.environ.get('BOTLAB_DYNAMICS_URL'),
    "email": os.environ.get('BOTLAB_DYNAMICS_EMAIL')
}
APP_VERSION = "0.0.1"
