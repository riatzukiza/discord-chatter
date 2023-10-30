# Docker compose files
These files describe the desired state of containers
running each of our individual services.

There are two types of compose file we are making a meaningful
distinguishment between. Modules, and standalones.

## Modules

Modules are not meant to be used by themselves. For example, several of these modules
require the `mongo` network and service to be available to function.
If no service ever creates these, these processes will wait forever. These
other services will wait for the network to exist. so If I have nothing
else running, and I wanted to spin up the message indexer, and trainer,
we will need to run the following command:

The modules were added to avoid redefining redis, chroma, mongo, and so on for every
service I wanted to run in isolation at some point to run a test or validate an assumption, 
and to make it easy to run different configurations of services with out constantly temporarily editing a YML file.
This way each of these ways are saved forever.

```bash
docker compose \
  -f docker/compose/modules/mongodb.yml \
  -f docker/compose/modules/trainer.yml \
  -f docker/compose/modules/discord-message-processor.yml config > \
  docker-compose.generated.yml
```

If you want to string together all of the modules and generate a master
docker compose file:

```bash
docker compose   \
  -f docker/compose/modules/mongodb.yml   \
  -f docker/compose/modules/trainer.yml   \
  -f docker/compose/modules/discord-message-processor.yml \
  -f docker/compose/modules/discord-message-indexer.yml \
  -f docker/compose/modules/redis.yml \
  -f docker/compose/modules/chroma.yml \
  config >   \
    docker-compose.live_training.yml
```

This will create a more verbose version of the default compose file.

## Bundles/standalones

These are docker compose files that initiate commonly used configurations of
services. For example, when working on the trainer, it may be desirable to only
run the trainer and not any of the rest of our user defined services, but
it depends on mongo db. To run only these two docker containers
you could use either of the following strategies:

```bash
docker compose up mongodb gpt-trainer -d
docker compose logs mongodb gpt-trainer -f --tail 100
docker compose restart mongodb gpt-trainer
docker compose down mongodb gpt-trainer
```

```bash
docker compose \
  -f docker/compose/modules/mongodb.yml \
  -f docker/compose/modules/trainer.yml  \
  up -d

docker compose \
  -f docker/compose/modules/mongodb.yml \
  -f docker/compose/modules/trainer.yml \
  logs -f --tail 100

docker compose \
  -f docker/compose/modules/mongodb.yml \
  -f docker/compose/modules/trainer.yml \
  restart -f --tail 100

docker compose \
  -f docker/compose/modules/mongodb.yml \
  -f docker/compose/modules/trainer.yml \
  down -f --tail 100
```

or... you could just run 

```bash
docker compose -f docker/compose/bundles/training-loop up -d
docker compose -f docker/compose/bundles/training-loop logs -f --tail 100
docker compose -f docker/compose/bundles/training-loop restart
docker compose -f docker/compose/bundles/training-loop down
```

remember we can generate new docker compose files from other files (thats how all of these were initially made)
Using the modules we've created, we can run the following command to
get a compose file that is the composition of the applied docker
compose files in the order they were written.


```bash
docker compose   \
  -f docker/compose/modules/mongodb.yml   \
  -f docker/compose/modules/trainer.yml   \
  config >   \
    docker/compose/bundles/training-loop.yml
```

This will give you a version of training loop from the current versions of mongodb and trainer.


If you wanted one that could generate messages using previously indexed messages,
and send them if they are valid, you could do this:

```bash
docker compose   \
  -f docker/compose/modules/mongodb.yml   \
  -f docker/compose/modules/generator.yml   \
  -f docker/compose/modules/discord-message-dispatcher.yml   \
  config >   \
    docker/compose/bundles/live-inference-loop.yml
```

If you wanted one, but didn't want to send the messages yet. You could allow them to build up in
the generated message table, and run the dispatcher later. All you need to do is:

```bash
docker compose   \
  -f docker/compose/modules/mongodb.yml   \
  -f docker/compose/modules/generator.yml   \
  config >   \
    docker/compose/bundles/non-dispatching-inference-loop.yml
```

If you only wanted to run the dispatcher, like if you ran the non dispatching inference
loop for a while and your ready to release your maddness onto the world:

```bash
docker compose   \
  -f docker/compose/modules/mongodb.yml   \
  -f docker/compose/modules/discord-message-dispatcher.yml   \
  config >   \
    docker/compose/bundles/dispatch-only.yml
```

If you only wanted to run the message processor, and store up a bunch of new messages with out them being trained on:

```bash
docker compose   \
  -f docker/compose/modules/mongodb.yml   \
  -f docker/compose/modules/discord-message-processor.yml config > \
    docker/compose/bundles/non-dispatching-inference-loop.yml
```
