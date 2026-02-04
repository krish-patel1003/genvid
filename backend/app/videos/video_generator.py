# todo
'''
TODO:
enqueue a generation job

worker generates a video (fake) - use sleep to simuate time taken

store result - (create a fake object storage url) - aysnc persisting to object storage

update video status - set to READY

FastAPI (API)
   |
   | enqueue task
   v
Broker (Redis / RabbitMQ)
   |
   v
Celery Worker
   |
   +--> video generation (ML / dummy)
   |
   +--> object storage (local / S3)
   |
   +--> update DB

'''