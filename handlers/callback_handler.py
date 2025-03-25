from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database import Database
from utils import ButtonManager, is_admin, humanbytes
import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()
button_manager = ButtonManager()

@Client.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    try:
        # Home Button
        if callback.data == "home":
            await button_manager.show_start(client, callback)
        
        # Help Button
        elif callback.data == "help":
            await button_manager.show_help(client, callback)
        
        # About Button
        elif callback.data == "about":
            await button_manager.show_about(client, callback)
        
        # Download File Button
        elif callback.data.startswith("download_"):
            # Check force subscription
            if not await button_manager.check_force_sub(client, callback.from_user.id):
                await callback.answer(
                    "Please join our channel to download files!",
                    show_alert=True
                )
                return
                
            file_uuid = callback.data.split("_")[1]
            file_data = await db.get_file(file_uuid)
            
            if not file_data:
                await callback.answer("File not found!", show_alert=True)
                return
                
            try:
                status_msg = await callback.message.reply_text(
                    "🔄 **Processing Download**\n\n⏳ Please wait..."
                )
                
                await client.copy_message(
                    chat_id=callback.message.chat.id,
                    from_chat_id=config.DB_CHANNEL_ID,
                    message_id=file_data["message_id"]
                )
                await db.increment_downloads(file_uuid)
                
                await status_msg.delete()
            except Exception as e:
                logger.error(f"Download error: {str(e)}")
                await callback.answer(f"Error: {str(e)}", show_alert=True)
        
        # Share File Button
        elif callback.data.startswith("share_"):
            file_uuid = callback.data.split("_")[1]
            share_link = f"https://t.me/{config.BOT_USERNAME}?start={file_uuid}"
            await callback.answer(
                f"Share Link: {share_link}",
                show_alert=True
            )
        
        # Download Batch Button
        elif callback.data.startswith("dlbatch_"):
            # Check force subscription
            if not await button_manager.check_force_sub(client, callback.from_user.id):
                await callback.answer(
                    "Please join our channel to download files!",
                    show_alert=True
                )
                return
                
            batch_uuid = callback.data.split("_")[1]
            batch_data = await db.get_batch(batch_uuid)
            
            if not batch_data:
                await callback.answer("Batch not found or expired!", show_alert=True)
                return
            
            status_msg = await callback.message.reply_text(
                "🔄 **Processing Batch Download**\n\n⏳ Please wait..."
            )
            
            success_count = 0
            failed_count = 0
            
            for file_uuid in batch_data["files"]:
                file_data = await db.get_file(file_uuid)
                if file_data:
                    try:
                        await client.copy_message(
                            chat_id=callback.message.chat.id,
                            from_chat_id=config.DB_CHANNEL_ID,
                            message_id=file_data["message_id"]
                        )
                        success_count += 1
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Batch download error: {str(e)}")
                        continue
            
            await db.increment_batch_downloads(batch_uuid)
            
            status_text = (
                f"✅ **Batch Download Complete**\n\n"
                f"📥 Successfully sent: {success_count} files\n"
                f"❌ Failed: {failed_count} files"
            )
            await status_msg.edit_text(status_text)
        
        # Share Batch Button
        elif callback.data.startswith("share_batch_"):
            batch_uuid = callback.data.split("_")[2]
            share_link = f"https://t.me/{config.BOT_USERNAME}?start=batch_{batch_uuid}"
            await callback.answer(
                f"Share Link: {share_link}",
                show_alert=True
            )
        
        # Answer the callback query
        if not callback.answered:
            await callback.answer()
            
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        if not callback.answered:
            await callback.answer("❌ An error occurred", show_alert=True)
