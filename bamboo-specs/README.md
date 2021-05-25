# Bamboo specs (JAVA)
Creates a plan and a deployment as code for a given repository. It also handless permissions, for plan deployment and enviroments.


## Installation

* Make sure the repository is setup as a spec repo:
[In bamboo](http://bamboo.cdk.com/userlogin!doDefault.action?os_destination=%2Fbuild%2Fadmin%2Fcreate%2FnewSpecs.action). Set a desired branch, sometimes during testing a feature could be set.

* Put bamboo-specs folder into repo root
* Open ./platform-core-app-<APP>/bamboo-specs/src/main/java/build/PlanSpec.java
```
 Edit GIT_REPO,PROJECT_NAME,PROJECT_KEY and PLAN_KEY
 Edit permissions if required
 Go trough tasks in createPlan and for each environment to make sure they do what you need.
```
* Modify ./platform-core-app-<APP>/bamboo-specs/scripts/build.sh as needed
* Go trough environment variables in platform-core-app-<APP>/bamboo-specs/environments/ 

## Usage

Once merged to mater or linked ot feature branch a plan spec will be loaded and plan/deployment will be created.

A deployment project will need to be linked to plan.