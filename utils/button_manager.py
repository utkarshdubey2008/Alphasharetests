from typing import List, Union
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import config
import logging

logger = logging.getLogger(__name__)

class ButtonManager:
    def __init__(self):
        self.force_sub_channels = []
        self.force_sub_links = []
        
        if hasattr(config, 'FORCE_SUB_CHANNEL1') and config.FORCE_SUB_CHANNEL1 != 0:
            self.force_sub_channels.append(str(config.FORCE_SUB_CHANNEL1))
            if config.FORCE_SUB_LINK1:
                self.force_sub_links.append(config.FORCE_SUB_LINK1)
                
        if hasattr(config, 'FORCE_SUB_CHANNEL2') and config.FORCE_SUB_CHANNEL2 != 0:
            self.force_sub_channels.append(str(config.FORCE_SUB_CHANNEL2))
            if config.FORCE_SUB_LINK2:
                self.force_sub_links.append(config.FORCE_SUB_LINK2)
                
        if hasattr(config, 'FORCE_SUB_CHANNEL3') and config.FORCE_SUB_CHANNEL3 != 0:
            self.force_sub_channels.append(str(config.FORCE_SUB_CHANNEL3))
            if config.FORCE_SUB_LINK3:
                self.force_sub_links.append(config.FORCE_SUB_LINK3)
                
        if hasattr(config, 'FORCE_SUB_CHANNEL4') and config.FORCE_SUB_CHANNEL4 != 0:
            self.force_sub_channels.append(str(config.FORCE_SUB_CHANNEL4))
            if config.FORCE_SUB_LINK4:
                self.force_sub_links.append(config.FORCE_SUB_LINK4)
        
        self.db_channel = config.DB_CHANNEL_ID

    async def check_force_sub(self, client, user_id: int) -> bool:
        if not self.force_sub_channels:
            return True
            
        try:
            all_joined = True
            for channel_id in self.force_sub_channels:
                try:
                    member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
                    if member.status in ["left", "kicked", "banned"]:
                        all_joined = False
                        break
                except Exception as e:
                    logger.error(f"Force sub check error for channel {channel_id}: {str(e)}")
                    all_joined = False
                    break
            return all_joined
        except Exception as e:
            logger.error(f"Force sub check error: {str(e)}")
            return False

    def force_sub_button(self) -> InlineKeyboardMarkup:
        buttons = []
        for i, link in enumerate(self.force_sub_links):
            if link and link.strip():
                buttons.append([
                    InlineKeyboardButton(
                        f"Join Channel {i + 1} 🔔",
                        url=link.strip()
                    )
                ])
        if not buttons:
            buttons.append([
                InlineKeyboardButton(
                    "Join Main Channel 🔔",
                    url=config.CHANNEL_LINK
                )
            ])
        buttons.append([
            InlineKeyboardButton(
                "🔄 Try Again",
                callback_data="check_sub"
            )
        ])
        return InlineKeyboardMarkup(buttons)

    async def show_start(self, client, callback_query: CallbackQuery):
        try:
            await callback_query.message.edit_text(
                config.Messages.START_TEXT.format(
                    bot_name=config.BOT_NAME,
                    user_mention=callback_query.from_user.mention
                ),
                reply_markup=self.start_button()
            )
        except Exception as e:
            logger.error(f"Show start error: {str(e)}")

    async def show_help(self, client, callback_query: CallbackQuery):
        try:
            await callback_query.message.edit_text(
                config.Messages.HELP_TEXT,
                reply_markup=self.help_button()
            )
        except Exception as e:
            logger.error(f"Show help error: {str(e)}")

    async def show_about(self, client, callback_query: CallbackQuery):
        try:
            await callback_query.message.edit_text(
                config.Messages.ABOUT_TEXT.format(
                    bot_name=config.BOT_NAME,
                    version=config.BOT_VERSION
                ),
                reply_markup=self.about_button()
            )
        except Exception as e:
            logger.error(f"Show about error: {str(e)}")

    def start_button(self) -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton("Help 📚", callback_data="help"),
                InlineKeyboardButton("About ℹ️", callback_data="about")
            ],
            [
                InlineKeyboardButton("Channel 📢", url=config.CHANNEL_LINK),
                InlineKeyboardButton("Developer 👨‍💻", url=config.DEVELOPER_LINK)
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    def help_button(self) -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton("Home 🏠", callback_data="home"),
                InlineKeyboardButton("About ℹ️", callback_data="about")
            ],
            [
                InlineKeyboardButton("Channel 📢", url=config.CHANNEL_LINK),
                InlineKeyboardButton("Support 🛟", url=config.SUPPORT_LINK)
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    def about_button(self) -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton("Home 🏠", callback_data="home"),
                InlineKeyboardButton("Help 📚", callback_data="help")
            ],
            [
                InlineKeyboardButton("Channel 📢", url=config.CHANNEL_LINK),
                InlineKeyboardButton("Support 🛟", url=config.SUPPORT_LINK)
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    def file_button(self, file_uuid: str) -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton("Download 📥", callback_data=f"download_{file_uuid}"),
                InlineKeyboardButton("Share Link 🔗", callback_data=f"share_{file_uuid}")
            ],
            [
                InlineKeyboardButton("Channel 📢", url=config.CHANNEL_LINK),
                InlineKeyboardButton("Support 🛟", url=config.SUPPORT_LINK)
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    def batch_button(self, batch_uuid: str) -> InlineKeyboardMarkup:
        buttons = [
            [
                InlineKeyboardButton("Download All 📥", callback_data=f"dlbatch_{batch_uuid}"),
                InlineKeyboardButton("Share Link 🔗", callback_data=f"share_batch_{batch_uuid}")
            ],
            [
                InlineKeyboardButton("Channel 📢", url=config.CHANNEL_LINK),
                InlineKeyboardButton("Support 🛟", url=config.SUPPORT_LINK)
            ]
        ]
        return InlineKeyboardMarkup(buttons)
