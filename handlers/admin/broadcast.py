from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils import is_admin
import asyncio
import logging

logger = logging.getLogger(__name__)
db = Database()

@Client.on_message(filters.command("broadcast") & filters.reply)
async def broadcast_command(client: Client, message: Message):
    if not is_admin(message):
        await message.reply_text("⚠️ You are not authorized to broadcast!")
        return

    replied_msg = message.reply_to_message
    if not replied_msg:
        await message.reply_text("❌ Please reply to a message to broadcast!")
        return
    
    status_msg = await message.reply_text("🔄 Broadcasting message...")
    users = await db.get_all_users()
    
    if not users:
        await status_msg.edit_text("❌ No users found in database!")
        return
        
    success = 0
    failed = 0
    
    total_users = len(users)
    progress_interval = max(total_users // 5, 1)  # Update progress every 20% or for each user if less than 5 users
    
    for index, user in enumerate(users, 1):
        try:
            if replied_msg.text:
                await client.send_message(
                    chat_id=user["user_id"],
                    text=replied_msg.text
                )
            elif replied_msg.media:
                await client.copy_message(
                    chat_id=user["user_id"],
                    from_chat_id=replied_msg.chat.id,
                    message_id=replied_msg.message_id
                )
            success += 1
            
            # Update progress periodically
            if index % progress_interval == 0:
                progress = (index / total_users) * 100
                await status_msg.edit_text(
                    f"🔄 Broadcasting...\n"
                    f"Progress: {progress:.1f}%\n"
                    f"✓ Success: {success}\n"
                    f"× Failed: {failed}\n"
                    f"📊 Total: {index}/{total_users}"
                )
        except Exception as e:
            failed += 1
            logger.error(f"Failed to send broadcast to user {user.get('user_id')}: {str(e)}")
        
        # Add a small delay to avoid flooding
        await asyncio.sleep(0.05)
    
    # Final status update
    broadcast_text = (
        "✅ **Broadcast Completed**\n\n"
        f"✓ Success: {success}\n"
        f"× Failed: {failed}\n"
        f"📊 Total: {total_users}"
    )
    await status_msg.edit_text(broadcast_text)
    
    # Log the broadcast completion
    logger.info(f"Broadcast completed - Success: {success}, Failed: {failed}, Total: {total_users}")
