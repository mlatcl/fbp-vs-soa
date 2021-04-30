This repo contains code for comparison flow-based programming (FBP) and software services (SOA) in the context of machine learning deployment.

The repository contains six implementations of Ride Allocation app, which allocates taxi drivers to incoming taxi ride requests. These implementations represent the same software at different stages of development using one of the aforementioned paradigms. Here is the complete list:

* [fbp_app_min](fbp_app_min/) - basic functionality implemented with FBP
* [fbp_app_data](fbp_app_data/) - same as above, plus dataset collection for wait time estimation
* [fbp_app_ml](fbp_app_ml/) - same as above, plus deployment of trained ML model that outputs estimated wait time for each allocated ride

* [soa_app_min](soa_app_min/) - basic functionality implemented with SOA
* [soa_app_data](soa_app_data/) - same as above, plus dataset collection for wait time estimation
* [soa_app_ml](soa_app_ml/) - same as above, plus deployment of trained ML model that outputs estimated wait time for each allocated ride

Other source files are used to define common data types and generate some input data. Entry point for running any of the applications is [main.py](main.py).
