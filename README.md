# API-QA

## What is it ?
In all companies, there is a lot of applications in the IT environment, and many of them used in the quality strategy.
From monitors, messages, functional tests, API tests, U.T, load tests, bug tracking, deployments, testbooks,... many many applications and framefork are involved in the quality strategy. 
The purpose of the ```api-qa``` is to coordinate interactions between all applications, it is a product to indistrualize quality workflows and strategies

supported applications : 
- Slack
- Newman
- MongoDb
- Cypress

## Getting started
The best way to work with this API is to build your docker container
You need to initialise some variables (in an ```.env``` or ```Dockerfile``` file) : 
- ```MONGODB_SRV```: SRV url to your mango Atlas database
- ```SLACK_WEBHOOK_URL```: The webhook to alert execution results
- ```API_QA_EXT_URL```: self url
- ``CY_RUNNER_INT_URL``: Cyress runner url ([remidqa/cy-runner](https://github.com/remidqa/cy-runner))
- ```NEWMAN_RUNNER_INT_URL```: Newman runner url ([remidqa/newman-runner](https://github.com/remidqa/newman-runner))
Then just run the build command, example : ```docker build -t api-qa .```
Finaly, run the created container, example : ```docker run -d api-qa```

## Routes
### Cypress
The cypress routes connect to a cypress runner ([remidqa/cy-runner](https://github.com/remidqa/cy-runner))
- ```[POST] /cypress/run```:
    - expected input body :
    ```json
    {
        "app": "app_name" // [MANDATORY] name of the application to test in cypress
    }
    ``` 

### Newman
The cypress routes connect to a cypress runner ([remidqa/cy-runner](https://github.com/remidqa/cy-runner))
- ```[POST] /newman/run```:
    - expected input body :
    ```json
    {
        "coll_id": "id of the collection", // [MANDATORY] postman id of the collection
        "env_id": "id of the environment" // [OPTIONAL] postman id of the environment
    }
    ``` 

### Reports
- ```[POST] /runner/:runner```
    - expected params: 
        - ```runner```: [MANDATORY] can be ```cypress``` or ```newman```
    - expected input body:
    ```json
    /// .json report from the newman or cypress reporter
    ```
- ```[GET] /runner/:runner```
    - expected params: 
        - ```runner```: [MANDATORY] can be ```cypress``` or ```newman```
    - expected input body:
    ```json
    {
        "query": {} // mongodb query 
    }
    ```
- ```[DELETE] /runner/:runner```
    - expected params: 
        - ```runner```: [MANDATORY] can be ```cypress``` or ```newman```
    - expected input body:
    ```json
    {
        "query": {} // mongodb query 
    }
    ```