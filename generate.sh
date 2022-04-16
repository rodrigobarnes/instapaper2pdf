#!/bin/bash
# Python environment
source .venv/bin/activate
# Credentials for instapaper
source .env
# Create the pdf
python instapaper2pdf.py
