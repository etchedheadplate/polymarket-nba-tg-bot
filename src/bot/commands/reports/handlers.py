from collections.abc import Sequence

import aiofiles
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaPhoto, Message, ReplyKeyboardRemove

from src.bot.commands.keyboards import get_team_side_keyboard, get_teams_keyboard
from src.bot.commands.reports.keyboards import get_reports_keyboard
from src.bot.commands.reports.states import ReportForm
from src.bot.commands.reports.text import ReportName, ReportText
from src.bot.commands.text import Buttons
from src.bot.domain import NBATeam
from src.queue import RabbitMQConnection
from src.tasks import Registry, ReportWorker

router = Router()

LABEL_TO_REPORT = {v: k for k, v in ReportText.BUTTON_LABELS.items()}


@router.message(Command("reports"))
async def reports_command_handler(message: Message, state: FSMContext):
    await state.set_state(ReportForm.report_name)
    await message.answer("Select report:", reply_markup=get_reports_keyboard())


@router.message(ReportForm.report_name)
async def handle_report_name(message: Message, state: FSMContext):
    if message.text == Buttons.CANCEL:
        await state.clear()
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
        return

    report_name = LABEL_TO_REPORT.get(message.text)  # pyright: ignore[reportArgumentType]
    if report_name is None:
        await message.answer("Please select a valid report.")
        return

    await state.update_data(report_name=report_name)
    await state.set_state(ReportForm.team)
    await message.answer("Select team:", reply_markup=get_teams_keyboard())


@router.message(ReportForm.team)
async def handle_team(message: Message, state: FSMContext):
    if message.text == Buttons.CANCEL:
        await state.clear()
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
        return
    if message.text == Buttons.BACK:
        await state.set_state(ReportForm.report_name)
        await message.answer("Select report:", reply_markup=get_reports_keyboard())
        return

    try:
        team = NBATeam[message.text]  # pyright: ignore[reportArgumentType]
    except KeyError:
        await message.answer("Please select a valid team.")
        return

    await state.update_data(team=team.value)
    await state.set_state(ReportForm.team_side)
    await message.answer("Select team side:", reply_markup=get_team_side_keyboard())


@router.message(ReportForm.team_side)
async def handle_team_side(message: Message, state: FSMContext):
    if message.text == Buttons.CANCEL:
        await state.clear()
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
        return
    if message.text == Buttons.BACK:
        await state.set_state(ReportForm.team)
        await message.answer("Select team:", reply_markup=get_teams_keyboard())
        return

    if message.text != Buttons.ANY_SIDE:
        await state.update_data(team_side=message.text)
    await state.set_state(ReportForm.team_vs)
    await message.answer("Select vs team:", reply_markup=get_teams_keyboard(optional=True))


@router.message(ReportForm.team_vs)
async def handle_team_vs(message: Message, state: FSMContext, connection: RabbitMQConnection, registry: Registry):
    if message.text == Buttons.CANCEL:
        await state.clear()
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())
        return
    if message.text == Buttons.BACK:
        await state.set_state(ReportForm.team_side)
        await message.answer("Select team side:", reply_markup=get_team_side_keyboard())
        return

    data = await state.get_data()
    await state.clear()

    query: dict[str, str] = {"team": data["team"]}
    if "team_side" in data:
        query["side"] = data["team_side"]
    if message.text != Buttons.ALL_TEAMS:
        try:
            query["team_vs"] = NBATeam[message.text].value  # pyright: ignore[reportArgumentType]
        except KeyError:
            await message.answer("Please select a valid team.")
            return

    report_name = ReportName(data["report_name"])
    worker = ReportWorker(connection=connection, registry=registry)
    payload = await worker.run(name=report_name, query=query)

    await message.answer("Generating report...", reply_markup=ReplyKeyboardRemove())

    async with aiofiles.open(payload["summary"]) as f:
        summary_text = await f.read()

    media = [FSInputFile(path) for path in payload["visuals"]]
    media_group: Sequence[InputMediaPhoto] = [InputMediaPhoto(media=photo) for photo in media]
    media_group[0] = InputMediaPhoto(media=media[0], caption=summary_text)

    await message.answer_media_group(media=media_group)  # pyright: ignore[reportArgumentType]
