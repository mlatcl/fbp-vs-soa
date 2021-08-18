MBlogger is heavily inspired by Kafker: https://github.com/mlatcl/kafker . In fact it is almost a complete rewrite of Kafker to flowpipe. As the app no longer runs on Apache Kafka though, its name is updated to reflect the business entity better.


To run any of the individual files go to the root folder of the package and do

```
python -m mblogger.<module>.app
```

for example

```
python -m mblogger.fbp_app_min.app
```