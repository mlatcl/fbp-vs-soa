#!/bin/bash

function prepend() {
    while read line; do echo "${1}${line}"; done;
}

function collect-metrics() {
    echo "######### Collecting metrics for file $1 #########"
    echo -e "\nHalstead complexity metrics"
    radon hal $1
    echo -e "\nMaintainability Index"
    radon mi -s $1
    echo -e "\nCyclomatic Complexity"
    radon cc -as $1 | grep Average
    echo "######### ############################## #########"
}

collect-metrics fbp_app_min.py
echo -e "\n"
collect-metrics fbp_app_data.py
echo -e "\n"
collect-metrics fbp_app_ml.py