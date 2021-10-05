#!/bin/bash

################ Common ################

function extract-number() {
    grep -E -o "[0-9]+[0-9.]*" $1
}

function write-csv-header() {
    # notice order of metrics
    # each function that writes lines to this file has to follow that order
    filename=$1
    echo "App,Key,Logical Lines of Code,Halstead Volume,Halstead Difficulty,Halstead Effort,Maintainability Index,Cyclomatic Complexity,Cognitive Complexity,Number of Words" >> $filename
}

function average() {
    # computes average of the list of numbers, one number per line
    awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'
}

function median() {
    # computes median of the list of numbers, one number per line
    sort -n $1 |  awk '{all[NR] = $1} END{print all[int(NR*0.50 - 0.50)]}'
}

function p99() {
    # computes 99th percentile of the list of numbers, one number per line
    sort -n $1  |  awk '{all[NR] = $1} END{print all[int(NR*0.99 - 0.50)]}'
}

function write-metrics-to-csv() {
    app=$1
    key=$2
    filename=$3
    stat=$4
    paradigm=$(echo $key | cut -c1-3) # fbp or soa
    echo -n "$app," >> $filename
    echo -n "$key," >> $filename
    $paradigm-lloc $app $key | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-halstead-metric $app $key 'volume' | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-halstead-metric $app $key 'difficulty' | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-halstead-metric $app $key 'effort' | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-maintainability-index $app $key | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-cyclomatic-complexity $app $key $stat | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    $paradigm-cognitive-complexity $app $key $stat | extract-number | xargs echo -n >> $filename
    echo -n ',' >> $filename
    #$paradigm-cohesion $app $key $stat | extract-number | xargs echo -n >> $filename
    #echo -n ',' >> $filename
    $paradigm-words $app $key | extract-number | xargs echo >> $filename
}

################ FBP ################
# each FBP app is in a single file, so we just analyze that file

function fbp-lloc() {
    app=$1
    key=$2
    radon raw $app/$key/$key.py | grep "LLOC"
}

function fbp-halstead-metric() {
    app=$1
    key=$2
    metric=$3
    radon hal $app/$key/$key.py | grep $metric
}

function fbp-maintainability-index() {
    app=$1
    key=$2
    radon mi -s $app/$key/$key.py
}

function fbp-cyclomatic-complexity() {
    app=$1
    key=$2
    stat=$3
    radon cc -as $app/$key/$key.py | grep -E -o '[M|C].*' | grep -E -o '\(*[0-9]+)' | grep -o -E '[0-9]+' | $stat
}

function fbp-cognitive-complexity() {
    app=$1
    key=$2
    metric=$3
    flake8 --select=CCR001 --max-cognitive-complexity=-1 $app/$key/$key.py | grep -E -o '\(.*>' | grep -o -E '[0-9]+' | $stat
}

function fbp-cohesion() {
    app=$1
    key=$2
    metric=$3
    flake8 $app/$key/$key.py  | grep -E -o '\(.*' | grep -o -E '[0-9]+[.][0-9]+' | $stat
}

function fbp-words() {
    app=$1
    key=$2
    wc -w $app/$key/$key.py | grep -o -E '[0-9]+'
}

function print-fbp-metrics() {
    echo "######### Collecting metrics for app $1 #########"
    echo -e "\nLogical lines of code"
    fbp-lloc $1 $2
    echo -e "\nHalstead complexity metrics"
    fbp-halstead-metric $1 $2 'volume'
    fbp-halstead-metric $1 $2 'difficulty'
    fbp-halstead-metric $1 $2 'effort'
    #radon hal $1/$1.py | grep 'volume\|difficulty\|effort'
    echo -e "\nMaintainability Index"
    fbp-maintainability-index $1 $2
    echo -e "\nCyclomatic Complexity"
    fbp-cyclomatic-complexity $1 $2 $3
    echo -e "\nAverage Cognitive Complexity"
    fbp-cognitive-complexity $1 $2 $3
    echo -e "\nAverage Cohesion"
    fbp-cohesion $1 $2 $3
    echo -e "\nNumber of Words"
    fbp-words $1 $2
    echo "######### ############################## #########"
}

################ SOA ################
# each SOA app consists of multiple files. Concretely we analyze main file and all files inside "flaskr" folder
# radon cannot handle such filtering logic, so we use find, cat all files together, and pipe that stdin stream to radon

function soa-lloc() {
    app=$1
    key=$2
    find $app/$key -iname '*.py' -a -not -name 'soa_model_training.py' -a -not -name "text_generator.py" -exec cat {} \; | radon raw - | grep "LLOC"
}

function soa-halstead-metric() {
    app=$1
    key=$2
    metric=$3
    find $app/$key -iname '*.py' -a -not -name 'soa_model_training.py' -a -not -name "text_generator.py" -exec cat {} \; | radon hal - | grep $metric
}

function soa-maintainability-index() {
    app=$1
    key=$2
    find $app/$key -iname '*.py' -a -not -name 'soa_model_training.py' -a -not -name "text_generator.py" -exec cat {} \; | radon mi -s -
}

function soa-cyclomatic-complexity() {
    app=$1
    key=$2
    stat=$3
    find $app/$key -iname '*.py' -a -not -name 'soa_model_training.py' -a -not -name "text_generator.py" -exec cat {} \; | radon cc -as - | grep -E -o '[M|C].*' | grep -E -o '\(*[0-9]+)' | grep -o -E '[0-9]+' | $stat
}

function soa-cognitive-complexity() {
    app=$1
    key=$2
    stat=$3
    flake8 --select=CCR001 --max-cognitive-complexity=-1 --exclude 'schema.sql */training_artifacts/* soa_model_training.py text_generator.py' $app/$key | grep -E -o '\(.*>' | grep -o -E '[0-9]+' | $stat
}

function soa-cohesion() {
    app=$1
    key=$2
    stat=$3
    find $app/$key -iname '*.py' -a -not -name 'soa_model_training.py' -a -not -name "text_generator.py" -exec cat {} \; | flake8 --select=H601 - | grep -E -o '\(.*' | grep -o -E '[0-9]+[.][0-9]+' | $stat
}

function soa-words() {
    app=$1
    key=$2
    find $app/$key -iname '*.py' -a -not -name 'temp.py' -a -not -name 'soa_model_training.py' -a -not -name "text_generator.py" -exec cat {} \; > $app/$key/temp.py
    wc -w $app/$key/temp.py | grep -o -E '[0-9]+'
    rm $app/$key/temp.py
}

function print-soa-metrics() {
    echo "######### Collecting metrics for app $1 #########"
    echo -e "\nLogical lines of code"
    soa-lloc $1 $2
    echo -e "\nHalstead complexity metrics"
    soa-halstead-metric $1 $2 'volume'
    soa-halstead-metric $1 $2 'difficulty'
    soa-halstead-metric $1 $2 'effort'
    echo -e "\nMaintainability Index"
    soa-maintainability-index $1 $2
    echo -e "\nAverage Cyclomatic Complexity"
    soa-cyclomatic-complexity $1 $2 $3
    echo -e "\nAverage Cognitive Complexity"
    soa-cognitive-complexity $1 $2 $3
    echo -e "\nAverage Cohesion"
    soa-cohesion $1 $2 $3
    echo -e "\nNumber of Words"
    soa-words $1 $2
    echo "######### ############################## #########"
}

if [ -z "$1" ]
then
    for application in insurance_claims mblogger ride_allocation
    do
        # filename not provided, print metrics to the screen
        print-fbp-metrics $application fbp_app_min average
        echo -e "\n"
        print-fbp-metrics $application fbp_app_data average
        echo -e "\n"
        print-fbp-metrics $application fbp_app_ml average
        echo -e "\n"

        echo -e "\n"
        print-soa-metrics $application soa_app_min average
        echo -e "\n"
        print-soa-metrics $application soa_app_data average
        echo -e "\n"
        print-soa-metrics $application soa_app_ml average
    done
    
    exit 0
else
    if [ -z "$2" ]
    then
        stat=average
    else
        stat=$2
    fi

    # filename provided, write metrics to this file
    echo -n "" > $1
    write-csv-header $1
    for application in insurance_claims mblogger ride_allocation
    do
        write-metrics-to-csv $application fbp_app_min $1 $stat
        write-metrics-to-csv $application fbp_app_data $1 $stat
        write-metrics-to-csv $application fbp_app_ml $1 $stat
        write-metrics-to-csv $application soa_app_min $1 $stat
        write-metrics-to-csv $application soa_app_data $1 $stat
        write-metrics-to-csv $application soa_app_ml $1 $stat
    done
    exit 0
fi
