This repository is part of a system for technical analysis of a Polymarket NBA data. You can learn more [here](https://sonyn.dev/blog/2026-04-07-a-random-walk-down-diamond-district/).

Telegram bot service provides access to [Polymarket NBA Reports](https://github.com/etchedheadplate/polymarket-nba-report) and [Polymarket NBA Oracle](https://github.com/etchedheadplate/polymarket-nba-oracle) database.

## Demo

![demo](media/demo.gif)

## Usage

### Enviroment

Create a `.env` file in the root of the repository using the `.env.example` template.

To run this service, the [Polymarket NBA Oracle](https://github.com/etchedheadplate/polymarket-nba-oracle) and [Polymarket NBA Report](https://github.com/etchedheadplate/polymarket-nba-report) services must be deployed first.

To obtain `TG_BOT_TOKEN` use BotFather (see [Telegram Bot Documentation](https://core.telegram.org/bots/tutorial#obtain-your-bot-token)).

### Running

The system is built around a RabbitMQ-based task processing model. A consumer subscribes to task queues, executes incoming tasks, and publishes results back to response queues.

Start Telegram bot with RabbitMQ consumer:

```bash
python -m main
```
