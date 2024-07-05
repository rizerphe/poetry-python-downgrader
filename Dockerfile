# This is for the github action
FROM python:3.12-alpine

RUN pip install poetry-python-downgrader

ENTRYPOINT ["downgrade-pyproject-for-python"]
