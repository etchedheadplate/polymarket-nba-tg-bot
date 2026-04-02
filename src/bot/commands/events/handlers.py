from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.commands.events.keyboards import get_events_keyboard
from src.bot.commands.events.states import EventsForm
from src.bot.commands.events.text import EventName, EventText
from src.bot.commands.keyboards import get_return_keyboard, get_team_side_keyboard, get_teams_keyboard
from src.bot.commands.text import Buttons
from src.bot.domain import NBATeam, NBATeamSide
from src.queue import RabbitMQConnection
from src.tasks import EventsWorker, Registry

router = Router()

LABEL_TO_EVENT = {v: k for k, v in EventText.BUTTON_LABELS.items()}


@router.message(Command("events"))
async def events_command_handler(message: Message, state: FSMContext):
    await state.set_state(EventsForm.event_name)
    await message.answer("Select events period:", reply_markup=get_events_keyboard())


@router.message(EventsForm.event_name)
async def handle_event_name(message: Message, state: FSMContext, connection: RabbitMQConnection, registry: Registry):
    if message.text == Buttons.CANCEL:
        await state.clear()
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
        return

    event_name = LABEL_TO_EVENT.get(message.text)  # pyright: ignore[reportArgumentType]
    if event_name is None:
        await message.answer("Please select a valid event period.", reply_markup=get_return_keyboard())
        return

    await state.update_data(event_name=event_name)
    if event_name != EventName.FUTURE:
        await state.set_state(EventsForm.start_date)
        await message.answer("Enter period start in YYYY-MM-DD:", reply_markup=get_return_keyboard())
    else:
        data = await state.get_data()
        await state.clear()

        event_period = EventName(data["event_name"])
        worker = EventsWorker(connection=connection, registry=registry)
        payload = await worker.run(period=event_period, query=data)

        if not payload:
            await message.answer("No games found for selected period.", reply_markup=ReplyKeyboardRemove())
            return

        text_response: list[str] = []
        for id, game in payload.items():
            game_line = f"{id} | {game["game_date"]} | {game["game_status"]} | {game["guest_team"]} {game["guest_score"]}:{game["host_score"]} {game["host_team"]}"
            text_response.append(game_line)

        formatted_text = f"```\n{'\n'.join(text_response)}```"
        await message.answer(formatted_text, parse_mode="MarkdownV2")


@router.message(EventsForm.start_date)
async def handle_start_date(message: Message, state: FSMContext):
    try:
        if message.text == Buttons.CANCEL:
            await state.clear()
            await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
            return
        if message.text == Buttons.BACK:
            await state.set_state(EventsForm.event_name)
            await message.answer("Enter period start in YYYY-MM-DD", reply_markup=get_return_keyboard())
            return

        selected_date_dt = datetime.strptime(message.text, "%Y-%m-%d").date()  # pyright: ignore[reportArgumentType]
        selected_date_str = selected_date_dt.strftime("%Y-%m-%d")
        await state.update_data(start_date=selected_date_str)

        await state.set_state(EventsForm.end_date)
        await message.answer("Enter period end in YYYY-MM-DD:", reply_markup=get_return_keyboard())
    except ValueError:
        await message.answer("Please enter a valid period in YYYY-MM-DD", reply_markup=get_return_keyboard())
        return


@router.message(EventsForm.end_date)
async def handle_end_date(message: Message, state: FSMContext):
    try:
        if message.text == Buttons.CANCEL:
            await state.clear()
            await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
            return
        if message.text == Buttons.BACK:
            await state.set_state(EventsForm.start_date)
            await message.answer("Enter period start in YYYY-MM-DD:", reply_markup=get_return_keyboard())
            return

        selected_date_dt = datetime.strptime(message.text, "%Y-%m-%d").date()  # pyright: ignore[reportArgumentType]
        selected_date_str = selected_date_dt.strftime("%Y-%m-%d")
        await state.update_data(end_date=selected_date_str)

        await state.set_state(EventsForm.team)
        await message.answer("Select team:", reply_markup=get_teams_keyboard())
    except ValueError:
        await message.answer("Please enter a valid period in YYYY-MM-DD", reply_markup=get_return_keyboard())
        return


@router.message(EventsForm.team)
async def handle_team(message: Message, state: FSMContext):
    if message.text == Buttons.CANCEL:
        await state.clear()
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
        return
    if message.text == Buttons.BACK:
        await state.set_state(EventsForm.end_date)
        await message.answer("Enter period end in YYYY-MM-DD:", reply_markup=get_return_keyboard())
        return

    try:
        team = NBATeam[message.text]  # pyright: ignore[reportArgumentType]
    except KeyError:
        await message.answer("Please select a valid team.", reply_markup=get_return_keyboard())
        return

    await state.update_data(team=team.value)
    await state.set_state(EventsForm.team_side)
    await message.answer("Select team side:", reply_markup=get_team_side_keyboard())


@router.message(EventsForm.team_side)
async def handle_team_side(message: Message, state: FSMContext):
    if message.text == Buttons.CANCEL:
        await state.clear()
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
        return
    if message.text == Buttons.BACK:
        await state.set_state(EventsForm.team)
        await message.answer("Select team:", reply_markup=get_teams_keyboard())
        return

    if message.text != Buttons.ANY_SIDE:
        try:
            team_side = NBATeamSide[message.text.upper()] if message.text else None
        except KeyError:
            await message.answer("Please select a valid side.", reply_markup=get_return_keyboard())
            return
        await state.update_data(team_side=team_side)
    await state.set_state(EventsForm.team_vs)
    await message.answer("Select vs team:", reply_markup=get_teams_keyboard(optional=True))


@router.message(EventsForm.team_vs)
async def handle_team_vs(message: Message, state: FSMContext, connection: RabbitMQConnection, registry: Registry):
    if message.text == Buttons.CANCEL:
        await state.clear()
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
        return
    if message.text == Buttons.BACK:
        await state.set_state(EventsForm.team_side)
        await message.answer("Select team side:", reply_markup=get_team_side_keyboard())
        return

    try:
        team_vs = NBATeam[message.text]  # pyright: ignore[reportArgumentType]
    except KeyError:
        await message.answer("Please select a valid team.", reply_markup=get_return_keyboard())
        return

    await state.update_data(team_vs=team_vs.value)
    data = await state.get_data()
    await state.clear()

    event_period = EventName(data["event_name"])
    worker = EventsWorker(connection=connection, registry=registry)
    dummy_query = {
        "event_name": "past",
        "start_date": "2025-06-17",
        "end_date": "2025-12-19",
        "team": "Grizzlies",
        "team_side": "guest",
        "team_vs": "Cavaliers",
    }
    payload = await worker.run(period=event_period, query=dummy_query)

    if not payload:
        await message.answer("No games found for selected period.", reply_markup=ReplyKeyboardRemove())
        return

    text_response: list[str] = []
    for id, game in payload.items():
        game_line = f"{id} | {game['game_date']} | {game['game_status']} | {game['guest_team']} {game['guest_score']}:{game['host_score']} {game['host_team']}"
        text_response.append(game_line)

    formatted_text = f"```\n{chr(10).join(text_response)}```"
    await message.answer(formatted_text, parse_mode="MarkdownV2")
