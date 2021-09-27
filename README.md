This repo contains code for comparison flow-based programming (FBP) and software services (SOA) in the context of machine learning deployment.

The repository contains three applications: Ride Allocation, MBlogger and Insurance Claims. Each app is implemented six times, these implementations represent the same software at different stages of development using one of the aforementioned paradigms. Here is the complete list:

* __fbp_app_min__ - basic functionality implemented with FBP
* __fbp_app_data__ - same as above, plus dataset collection
* __fbp_app_ml__ - same as above, plus deployment of a trained ML model

* __soa_app_min__ - basic functionality implemented with SOA
* __soa_app_data__ - same as above, plus dataset collection
* __soa_app_ml__ - same as above, plus deployment of a trained ML model

Other source files are used to define common data types and generate some input data.

### How to run the code
todo

Note that SOA apps are implemented as Flask web services, and thus requires flask process to run to serve requests. Each SOA app has a `flaskr/README.md` file that explains how to do that.

### How to collect metrics

Run [code_metrics.sh](code_metrics.sh) can collect code metrics for all the apps. We collect several [Halstead metrics](https://en.wikipedia.org/wiki/Halstead_complexity_measures), [cyclomatic](https://en.wikipedia.org/wiki/Cyclomatic_complexity) and [cognitive](https://blog.sonarsource.com/cognitive-complexity-because-testability-understandability) complexities, [maintainability index](https://radon.readthedocs.io/en/latest/intro.html#maintainability-index).

To output metrics data in the console: todo
