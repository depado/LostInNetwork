#!/bin/bash

celery -A app.celery worker --beat
