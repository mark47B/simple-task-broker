# simple-task-broker

A simple application consisting of three components: producer is an application on aiohttp, which on request `localhost:8080/make_tasks?n=10` creates n requests, which fall into RabbitMQ, if there is a connection to consumer, the requests are passed on. Interaction with RabbitMQ is done with the help of aio-pilka library

## Run 

```
docker-compose up
```

Simple test
```
`localhost:8080/make_tasks?n=10`
```


