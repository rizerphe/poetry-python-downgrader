# This is for the github action
FROM python:3.12-alpine

RUN pip install poetry-python-downgrader==0.1.2

ENTRYPOINT ["python", "-m", "poetry_python_downgrader.gh_actions_cli"]
