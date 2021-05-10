This repo contains code for comparison flow-based programming (FBP) and software services (SOA) in the context of machine learning deployment.

The repository contains six implementations of Ride Allocation app, which allocates taxi drivers to incoming taxi ride requests. These implementations represent the same software at different stages of development using one of the aforementioned paradigms. Here is the complete list:

* [fbp_app_min](fbp_app_min/) - basic functionality implemented with FBP
* [fbp_app_data](fbp_app_data/) - same as above, plus dataset collection for wait time estimation
* [fbp_app_ml](fbp_app_ml/) - same as above, plus deployment of trained ML model that outputs estimated wait time for each allocated ride

* [soa_app_min](soa_app_min/) - basic functionality implemented with SOA
* [soa_app_data](soa_app_data/) - same as above, plus dataset collection for wait time estimation
* [soa_app_ml](soa_app_ml/) - same as above, plus deployment of trained ML model that outputs estimated wait time for each allocated ride

Other source files are used to define common data types and generate some input data.

### How to run the code

Entry point for running any of the applications is [main.py](main.py). To run a particular version of the app, run:

    python main.py <app_key>

for example for `fbp_app_ml`:

    python main.py fbp_app_ml

Note that SOA apps are implemented as Flask web services, and thus requires flask process to run to serve requests. Each SOA app has a `flaskr/README.md` file that explains how to do that.

### How to collect metrics

Run [code_metrics.sh](code_metrics.sh) can collect code metrics for all the apps. We collect several (Halstead metrics)[https://en.wikipedia.org/wiki/Halstead_complexity_measures], (cyclomatic)[https://en.wikipedia.org/wiki/Cyclomatic_complexity] and (cognitive)[https://blog.sonarsource.com/cognitive-complexity-because-testability-understandability] complexities, (maintainability index)[https://radon.readthedocs.io/en/latest/intro.html#maintainability-index].

To output metrics data in the console:

    ./code_metrics.sh

To write metrics data to a file in CSV format:

    ./code_metrics.sh <filename>
