#!/usr/bin/bash

set -e -x

cd /usr/src/app
pip3 install -r requirements.txt --only-binary --upgrade --target ./package
cd /usr/src/app/package
zip -r ../infrastructure/lambda_function.zip .
cd /usr/src/app/mtgcrawler
zip -g -r ../infrastructure/lambda_function.zip scrapy.cfg launcher.py mtgcrawler/
