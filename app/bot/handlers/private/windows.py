from aiogram.utils.markdown import hcode
from aiogram_tonconnect import ATCManager
from aiogram_tonconnect.tonconnect.models import AccountWallet

from app.bot.manager import Manager, SendMode
from app.bot.utils import keyboards
from app.bot.utils.states import UserState
from app.bot.utils.urls import NFTBuyUrl, JettonBuyUrl, TonviewerUrl
from app.db.models import UserDB, ChatDB, TokenDB


class Window:

    @staticmethod
    async def select_language(manager: Manager, send_mode: SendMode = SendMode.EDIT, **_) -> None:
        text = manager.text_message.get("select_language")
        reply_markup = keyboards.select_language()

        await manager.send_message(text, reply_markup=reply_markup, send_mode=send_mode)
        await manager.state.set_state(UserState.SELECT_LANGUAGE)

    @staticmethod
    async def change_language(manager: Manager, send_mode: SendMode = SendMode.EDIT, **_) -> None:
        text = manager.text_message.get("change_language")
        reply_markup = keyboards.select_language()

        await manager.send_message(text, reply_markup=reply_markup, send_mode=send_mode)
        await manager.state.set_state(UserState.CHANGE_LANGUAGE)

    @staticmethod
    async def main_menu(
            manager: Manager,
            send_mode: SendMode = SendMode.EDIT,
            account_wallet: AccountWallet = None,
            **data,
    ) -> None:
        wallet_address = manager.user_db.wallet_address

        if account_wallet:
            await manager.send_loader_message()
            await UserDB.update(
                manager.sessionmaker,
                primary_key=manager.user_db.id,
                wallet_address=account_wallet.address.to_userfriendly(),
            )
            wallet_address = account_wallet.address.to_userfriendly()
            atc_manager: ATCManager = data.get("atc_manager")
            await atc_manager.disconnect_wallet()

        chats = await ChatDB.all(manager.sessionmaker)
        tokens = await TokenDB.all(manager.sessionmaker)

        text = manager.text_message.get("main_menu").format(
            wallet=TonviewerUrl(wallet_address).hlink_short,
            chats="\n".join([f"• {hcode(chat.name)}" for chat in chats]),
            tokens="\n".join(
                [
                    f"• {NFTBuyUrl(token.address, token.name).hlink_name} - {hcode(token.min_amount_str)}"
                    if token.type == TokenDB.Type.NFTCollection else
                    f"• {JettonBuyUrl(token.address, token.name).hlink_name} - {hcode(token.min_amount_str)}"
                    for token in tokens
                ]
            )
        )
        reply_markup = keyboards.main_menu(manager.text_button)

        await manager.send_message(text, reply_markup=reply_markup, send_mode=send_mode)
        await manager.state.set_state(UserState.MAIN_MENU)

    @staticmethod
    async def allow_access(manager: Manager, send_mode: SendMode = SendMode.EDIT) -> None:
        chats = await ChatDB.all(manager.sessionmaker)

        text = manager.text_message.get("allow_access")
        reply_markup = keyboards.allow_access(manager.text_button, chats)

        await manager.send_message(text, reply_markup=reply_markup, send_mode=send_mode)
        await manager.state.set_state(UserState.ALLOW_ACCESS)

    @staticmethod
    async def deny_access(manager: Manager, send_mode: SendMode = SendMode.EDIT) -> None:
        tokens = await TokenDB.all(manager.sessionmaker)

        text = manager.text_message.get("deny_access")
        reply_markup = keyboards.deny_access(manager.text_button, tokens)

        await manager.send_message(text, reply_markup=reply_markup, send_mode=send_mode)
        await manager.state.set_state(UserState.DENY_ACCESS)
