#!/bin/bash
docker build -t gcr.io/programare-cetatenie-tr/selenium-script:$1 -f Dockerfile.selenium .

docker tag gcr.io/programare-cetatenie-tr/selenium-script:$1 gcr.io/programare-cetatenie-tr/selenium-script:$1
docker push gcr.io/programare-cetatenie-tr/selenium-script:$1



