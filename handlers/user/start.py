from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils import ButtonManager
import config
import asyncio
from ..utils.message_delete import schedule_message_deletion

db = Database()
button_manager = ButtonManager()

@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await db.add_user(message.from_user.id, message.from_user.username)
    
    if len(message.command) > 1:
        command = message.command[1]
        
        if not await button_manager.check_force_sub(client, message.from_user.id):
            await message.reply_text(
                "**⚠️ You must join our channel to use this bot!**\n\n"
                "Please join Our Forcesub Channel and try again.",
                reply_markup=button_manager.force_sub_button(),
                protect_content=config.PRIVACY_MODE
            )
            return

        if command.startswith("batch_"):
            batch_uuid = command.replace("batch_", "")
            batch_data = await db.get_batch(batch_uuid)
            
            if not batch_data:
                await message.reply_text(
                    "❌ Batch not found or has been deleted!", 
                    protect_content=config.PRIVACY_MODE
                )
                return
            
            status_msg = await message.reply_text(
                f"🔄 **Processing Batch Download**\n\n"
                f"📦 Total Files: {len(batch_data['files'])}\n"
                f"⏳ Please wait...",
                protect_content=config.PRIVACY_MODE
            )
            
            success_count = 0
            failed_count = 0
            sent_msgs = []
            
            for file_uuid in batch_data["files"]:
                file_data = await db.get_file(file_uuid)
                if file_data and "message_id" in file_data:
                    try:
                        msg = await client.copy_message(
                            chat_id=message.chat.id,
                            from_chat_id=config.DB_CHANNEL_ID,
                            message_id=file_data["message_id"],
                            protect_content=config.PRIVACY_MODE
                        )
                        sent_msgs.append(msg.id)
                        success_count += 1
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Batch file send error: {str(e)}")
                        continue
            
            if success_count > 0:
                await db.increment_batch_downloads(batch_uuid)
            
            status_text = (
                f"✅ **Batch Download Complete**\n\n"
                f"📥 Successfully sent: {success_count} files\n"
                f"❌ Failed: {failed_count} files"
            )
            await status_msg.edit_text(status_text)
            
        else:
            file_uuid = command
            file_data = await db.get_file(file_uuid)
            
            if not file_data:
                await message.reply_text(
                    "❌ File not found or has been deleted!", 
                    protect_content=config.PRIVACY_MODE
                )
                return
            
            try:
                msg = await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=config.DB_CHANNEL_ID,
                    message_id=file_data["message_id"],
                    protect_content=config.PRIVACY_MODE
                )
                await db.increment_downloads(file_uuid)
                await db.update_file_message_id(file_uuid, msg.id, message.chat.id)
                
                if file_data.get("auto_delete"):
                    delete_time = file_data.get("auto_delete_time")
                    if delete_time:
                        info_msg = await msg.reply_text(
                            f"⏳ **File Auto-Delete Information**\n\n"
                            f"This file will be automatically deleted in {delete_time} minutes\n"
                            f"• Delete Time: {delete_time} minutes\n"
                            f"• Time Left: {delete_time} minutes\n"
                            f"💡 **Save this file to your saved messages before it's deleted!**",
                            protect_content=config.PRIVACY_MODE
                        )
                        
                        asyncio.create_task(schedule_message_deletion(
                            client, file_uuid, message.chat.id, [msg.id, info_msg.id], delete_time
                        ))
                    
            except Exception as e:
                await message.reply_text(
                    f"❌ Error: {str(e)}", 
                    protect_content=config.PRIVACY_MODE
                )
                
    else:
        # Only send start message if no command arguments (pure /start)
        await message.reply_text(
            config.Messages.START_TEXT.format(
                bot_name=config.BOT_NAME,
                user_mention=message.from_user.mention
            ),
            reply_markup=button_manager.start_button(),
            protect_content=config.PRIVACY_MODE
        )
