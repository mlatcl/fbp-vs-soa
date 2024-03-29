# FBP vs SOA for ML

This repo contains code for comparison flow-based programming (FBP) and software services (SOA) in the context of machine learning deployment. It accompanies the paper "An Empirical Evaluation of Flow Based Programming in the Machine Learning Deployment Context" presented at [CAIN 2022 conference](https://conf.researchr.org/track/cain-2022/cain-2022). ArXiv version of the paper is here: https://arxiv.org/abs/2204.12781. Published versions are openly available in [ACM](https://dl.acm.org/doi/abs/10.1145/3522664.3528601) and [IEEE](https://ieeexplore.ieee.org/document/9796395) libraries.

Earlier version of this repository accompanied paper "Towards better data discovery and collection with flow-based programming" presented at [Data-centric AI workshop](https://datacentricai.org/neurips21/) at NeurIPS 2021. The paper is also available on [ArXiv](https://arxiv.org/abs/2108.04105) and its code now lives in a [separate branch](https://github.com/mlatcl/fbp-vs-soa/tree/ride-allocation).

### Structure

The repository contains four applications: Ride Allocation, MBlogger, Insurance Claims and Playlist Builder. Each app is implemented six times, these implementations represent the same software at different stages of development using one of the aforementioned paradigms. Here is the complete list:

* __fbp_app_min__ - basic functionality implemented with FBP
* __fbp_app_data__ - same as above, plus data collection
* __fbp_app_ml__ - same as above, plus deployment of a trained ML model

* __soa_app_min__ - basic functionality implemented with SOA
* __soa_app_data__ - same as above, plus data collection
* __soa_app_ml__ - same as above, plus deployment of a trained ML model

Other source files are used to define common data types and generate some input data.

### How to run the code
Before running any apps, make sure you have all dependencies, by running

```
pip install -r requirements.txt
```

#### Running FBP apps

To run FBP apps, use this command from root of the project:

```
python -m <app_name>.main fbp_app_<stage>
```

For example, to run `insurance_claims` at stage `data`, use

```
python -m insurance_claims.main fbp_app_data
```

#### Running SOA apps
SOA apps are implemented as Flask web services, and thus requires flask process to run to serve requests. Each SOA app has a `flaskr/README.md` file that explains how to do that.

### How to collect metrics

Bash script [code_metrics.sh](code_metrics.sh) can collect code metrics for all the apps. We collect several [Halstead metrics](https://en.wikipedia.org/wiki/Halstead_complexity_measures), [cyclomatic](https://en.wikipedia.org/wiki/Cyclomatic_complexity) and [cognitive](https://blog.sonarsource.com/cognitive-complexity-because-testability-understandability) complexities, [maintainability index](https://radon.readthedocs.io/en/latest/intro.html#maintainability-index), as well as number of words and logical lines of code.

To output metrics data in the console:

```
./code_metrics.sh
```

To write metrics data to a CSV file:

```
./code_metrics.sh file_name_goes_here.csv
```

We also define and collect a metric "Number of Affected Components", which we understand as the number of components that were created or changed between any two moments in development. We collect it by generating a diff between two stages with:

```
git diff --no-index <app_name>/<stage1> <app_name>/<stage2>
```

for example

```
git diff --no-index mblogger/fbp_app_data mblogger/fbp_app_ml
```

All diffs are collected in "<app_name>/diffs" folder, and overall metric is available in component_diff.yml in the root of the project.
