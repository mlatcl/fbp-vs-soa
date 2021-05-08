#!/bin/bash

################ Common ################

function extract-number() {
    grep -E -o "[0-9]+[0-9.]*" $1
}

function write-csv-header() {
    # notice order of metrics
    # each function that writes lines to this file has to follow that order
    filename=$1
    echo "app_key,halstead_volume,halstead_difficulty,halstead_effort,maintainability_index,cyclomatic_complexity,cognitive_complexity" >> $filename
}

function average() {
    # computes average of the list of numbers, one number per line
    awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'
}

function write-metrics-to-csv() {
    key=$1
    filename=$2
    paradigm=$(echo $key | cut -c1-3) # fbp or soa
    echo -n "$key," >> $filename
    $paradigm-halstead-metric $key 'volume' | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-halstead-metric $key 'difficulty' | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-halstead-metric $key 'effort' | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-maintainability-index $1 | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-cyclomatic-complexity $1 | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-cognitive-complexity $1 | extract-number | xargs echo >> $filename
}

################ FBP ################
# each FBP app is in a single file, so we just analyze that file

function fbp-halstead-metric() {
    key=$1
    metric=$2
    radon hal $key/$key.py | grep $metric
}

function fbp-maintainability-index() {
    key=$1
    radon mi -s $key/$key.py
}

function fbp-cyclomatic-complexity() {
    key=$1
    radon cc -as $key/$key.py | grep Average
}

function fbp-cognitive-complexity() {
    key=$1
    flake8 --select=CCR001 --max-cognitive-complexity=-1 $key | grep -E -o '\(.*>' | grep -o -E '[0-9]+' | average
}

function print-fbp-metrics() {
    echo "######### Collecting metrics for app $1 #########"
    echo -e "\nHalstead complexity metrics"
    fbp-halstead-metric $1 'volume'
    fbp-halstead-metric $1 'difficulty'
    fbp-halstead-metric $1 'effort'
    #radon hal $1/$1.py | grep 'volume\|difficulty\|effort'
    echo -e "\nMaintainability Index"
    fbp-maintainability-index $1
    echo -e "\nCyclomatic Complexity"
    fbp-cyclomatic-complexity $1
    echo -e "\nAverage Cognitive Complexity"
    fbp-cognitive-complexity $1
    echo "######### ############################## #########"
}

################ SOA ################
# each SOA app consists of multiple files. Concretely we analyze main file and all files inside "flaskr" folder, but excluding data access layer which goes inside "data" folder
# radon cannot handle such filtering logic, so we use find, cat all files together, and pipe that stdin stream to radon

function soa-halstead-metric() {
    key=$1
    metric=$2
    find $key -iname '*.py' -a -not -path '*/data/*' -a -not -name 'soa_model_training.py' -exec cat {} \; | radon hal - | grep $metric
}

function soa-maintainability-index() {
    key=$1
    find $key -iname '*.py' -a -not -path '*/data/*' -a -not -name 'soa_model_training.py' -exec cat {} \; | radon mi -s -
}

function soa-cyclomatic-complexity() {
    key=$1
    find $key -iname '*.py' -a -not -path '*/data/*' -a -not -name 'soa_model_training.py' -exec cat {} \; | radon cc -as - | grep Average
}

function soa-cognitive-complexity() {
    key=$1
    flake8 --select=CCR001 --max-cognitive-complexity=-1 --exclude "*/data/*,soa_model_training.py" $key | grep -E -o '\(.*>' | grep -o -E '[0-9]+' | average
}

function print-soa-metrics() {
    echo "######### Collecting metrics for app $1 #########"
    echo -e "\nHalstead complexity metrics"
    soa-halstead-metric $1 'volume'
    soa-halstead-metric $1 'difficulty'
    soa-halstead-metric $1 'effort'
    echo -e "\nMaintainability Index"
    soa-maintainability-index $1
    echo -e "\nAverage Cyclomatic Complexity"
    soa-cyclomatic-complexity $1
    echo -e "\nAverage Cognitive Complexity"
    soa-cognitive-complexity $1
    echo "######### ############################## #########"
}

if [ -z "$1" ]
then
    # filename not provided, print metrics to the screen
    print-fbp-metrics fbp_app_min
    echo -e "\n"
    print-fbp-metrics fbp_app_data
    echo -e "\n"
    print-fbp-metrics fbp_app_ml
    echo -e "\n"

    echo -e "\n"
    print-soa-metrics soa_app_min
    echo -e "\n"
    print-soa-metrics soa_app_data
    echo -e "\n"
    print-soa-metrics soa_app_ml
    
    exit 0
else
    # filename provided, write metrics to this file
    echo -n "" > $1
    write-csv-header $1
    write-metrics-to-csv fbp_app_min $1
    write-metrics-to-csv fbp_app_data $1
    write-metrics-to-csv fbp_app_ml $1
    write-metrics-to-csv soa_app_min $1
    write-metrics-to-csv soa_app_data $1
    write-metrics-to-csv soa_app_ml $1
    exit 0
fi
