#!/bin/bash


# each FBP app is in a single file, so we just analyze that file
function collect-fbp-metrics() {
    echo "######### Collecting metrics for app $1 #########"
    echo -e "\nHalstead complexity metrics"
    radon hal $1/$1.py | grep 'volume\|difficulty\|effort'
    echo -e "\nMaintainability Index"
    radon mi -s $1/$1.py
    echo -e "\nCyclomatic Complexity"
    radon cc -as $1/$1.py | grep Average
    echo -e "\nAverage Cognitive Complexity"
    flake8 --select=CCR001 --max-cognitive-complexity=-1 $1 | grep -E -o '\(.*>' | grep -o -E '[0-9]+' | awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'
    echo "######### ############################## #########"
}

# each SOA app consists of multiple files. Concretely we analyze main file and all files inside "flaskr" folder, but excluding data access layer which goes inside "data" folder
# radon cannot handle such filtering logic, so we use find, cat all files together, and pipe that stdin stream to radon
function collect-soa-metrics() {
    echo "######### Collecting metrics for app $1 #########"
    echo -e "\nHalstead complexity metrics"
    find $1 -iname '*.py' -a -not -path '*/data/*' -exec cat {} \; | radon hal - | grep 'volume\|difficulty\|effort'
    echo -e "\nMaintainability Index"
    find $1 -iname '*.py' -a -not -path '*/data/*' -exec cat {} \; | radon mi -s -
    echo -e "\nAverage Cyclomatic Complexity"
    find $1 -iname '*.py' -a -not -path '*/data/*' -exec cat {} \; | radon cc -as - | grep Average
    echo -e "\nAverage Cognitive Complexity"
    flake8 --select=CCR001 --max-cognitive-complexity=-1 --exclude "*/data/*" $1 | grep -E -o '\(.*>' | grep -o -E '[0-9]+' | awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'
    echo "######### ############################## #########"
}

collect-fbp-metrics fbp_app_min
echo -e "\n"
collect-fbp-metrics fbp_app_data
echo -e "\n"
collect-fbp-metrics fbp_app_ml
echo -e "\n"

echo -e "\n"
collect-soa-metrics soa_app_min
echo -e "\n"
collect-soa-metrics soa_app_data
echo -e "\n"
collect-soa-metrics soa_app_ml