#!/bin/bash
docker build -t gcr.io/programare-cetatenie-tr/mitmdump-script:$1 -f Dockerfile.mitmdump .
docker tag gcr.io/programare-cetatenie-tr/mitmdump-script:$1 gcr.io/programare-cetatenie-tr/mitmdump-script:$1
docker push gcr.io/programare-cetatenie-tr/mitmdump-script:$1
