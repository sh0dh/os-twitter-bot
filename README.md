# vandul-twitter-bot

## Setup

* Install `poetry` for your local setup
* For python setup, I use `asdf`

## Installing the repo libs

* Run: `poetry install` from the root repository
* This should create a new `.venv` folder in the root repository
* Make sure you have created a `db` folder and `.env` file in the root folder. `.env` format is laid out in `env-local`
* You need to setup a Twitter app as well
* `env-local`
* Run migration using: `poetry run db:migrate`, this will create all the necessary tables in a sqlite db
* The bot can be run as a standalone script for any collection on Opensea:
  * `poetry run twitter-bot --collection <opensea-collection-name> --start_time "2022-01-27 00:00:00" --is_tweet False`
* For prod usage, I used a hacky solution:
  * Used `scheduler` library to run all the cron jobs (see `schedulers` folder)
  * User [`overmind`](https://github.com/DarthSim/overmind) to keep the scheduler alive
* For a saner (more robust) solution, job-queues using redis or kubernetes based jobs are appropriate

## Where's the bot running
* We are running this on a $5 per month DigitalOcean machine. No fancy setup. Though I'd like to make this more automated, something like a one-click deploy

## Roadmap or Good things I would like?
* Move to queue based or light weight cron based processing of jobs. Hard to run Airflow on a budget, which is the perfect choice. FYI: First version of this bot was an airflow setup.
* One-click deploy
* Cheaper hosting than $5 per month, there are alternatives (like Railway) but no cron jobs (sad noises)

## You want to get one setup?
* Feel free to modify and use it. If your project wants to set one up, hmu @sh0xdh on twitter or info@shodh.co
