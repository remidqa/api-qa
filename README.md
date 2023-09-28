# API-QA

## Quick presentation
This Api automate actions between applications to perform industrialized quality strategies.
For a more detailed presentation : [front.remidqa.com/presentation-qa-framework](https://front.remidqa.com/presentation-qa-framework)

## Technologies
- Python
- Flask
- Docker
- remidqa quality workflow
- Pymongo

## Build
- This API is designed for a Docker usage
- To build simple run : ```docker build -t {tag-name} .```
- Then the image will be available on your local repository

## Configuration
- To communicate with a 'Cypress runner' to manage functional tests executions : set env variable ```CY_RUNNER_INT_URL```
- To communicate with an 'Newman runner' to manage API tests executions : set env variable ```NEWMAN_RUNNER_INT_URL```
- To get test srategies by app and env from a github configuration repository : [remidqa/qa-configurations](https://github.com/remidqa/qa-configurations)
- To export results to a mongo-database : set env variable ```MONGODB_SRV```
- To send reports to a Slack webhook : set env variable ```SLACK_WEBHOOK_URL```
- To send reports to a Discord webhook : set env variable ```DISCORD_WEBHOOK```
- To export results to testiny.io : set env variables ```TESTINYIO_URL``` and ```TESTINYIO_TOKEN```

## Usage
- set the appropriate configuration in a .json (full example in [remidqa/qa-configurations](https://github.com/remidqa/qa-configurations) repository)
- call the ```[POST] /run``` route with 2 mandatory paremeters ('app' and 'env') in the body : ```{'app': '${app}', 'env': '${env}'}```
- You can either go away or wait for the report, the results will be available on your test management tool (testiny.io for this version) and you will get a discord notification
