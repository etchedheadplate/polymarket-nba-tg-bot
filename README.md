This repository is part of a system for technical analysis of a Polymarket NBA data. You can learn more [here](https://sonyn.dev/blog/2026-04-07-a-random-walk-down-diamond-district/).

Telegram bot service provides access to [Polymarket NBA Reports](https://github.com/etchedheadplate/polymarket-nba-report) and [Polymarket NBA Oracle](https://github.com/etchedheadplate/polymarket-nba-oracle) database.

## Demo

![demo](media/demo.gif)

## Usage

The system is built around a RabbitMQ-based task processing model. A consumer subscribes to task queues, executes incoming tasks, and publishes results back to response queues.

Start Telegram bot with RabbitMQ consumer:

```bash
python -m main
```
