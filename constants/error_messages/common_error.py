"""All common error messages."""
from os import environ
CONTACT_MANAGER = f"Please contact your manager or contact {environ.get('BOTLAB_DYNAMICS')} at {environ.get('BOTLAB_DYNAMICS_EMAIL')}."
