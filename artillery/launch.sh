#!/usr/bin/env bash

set -e
set -x
set -u

TEST_ID=$(uuidgen)
SCRIPT="script-${ENVIRONMENT}.yml"

cat > script.patch << EOF
---
- op: replace
  path: /config/plugins/influxdb/tags
  value:
    environment: ${ENVIRONMENT}
    testId: ${TEST_ID}

- op: replace
  path: /config/target
  value: ${APP_TARGET_URL}

- op: replace
  path: /config/grafana/host
  value: ${GRAFANA}

- op: replace
  path: /config/plugins/influxdb/influx/host
  value: ${INFLUX_DB}
EOF

cat script.yml | /tmp/go/bin/yaml-patch -o script.patch > ${SCRIPT}
echo $(cat ${SCRIPT})

slsart invoke --stage perf --path ${SCRIPT}

python3 ./check.py --script ${SCRIPT} --pass-rate-success ${PASS_RATE_SUCCESS} --pass-rate-p95 ${PASS_RATE_P95}

