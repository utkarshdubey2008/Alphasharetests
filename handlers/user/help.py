from pyrogram import Client, filters
from pyrogram.types import Message
from utils import ButtonManager

button_manager = ButtonManager()

@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = (
        "**🤖 Bot Help Center v1.4**\n\n"
        "📌 **Basic Commands:**\n"
        "• /start - Start the bot.\n"
        "• /help - Show this menu.\n"
        "• /about - Bot details.\n"
        "• /short [url] - Shorten a link.\n\n"
        "🔧 **Admin Commands:**\n"
        "• /upload - Upload a file (reply to a file).\n"
        "• /batch - Group multiple files (reply to multiple).\n"
        "• /auto_del - Set auto-delete timer.\n"
        "• /stats - View bot stats.\n"
        "• /broadcast - Send messages to all users.\n\n"
        "🗑 **Auto-Delete System:**\n"
        "• Files auto-delete after a set time.\n"
        "• Use /auto_del to modify the timer.\n\n"
        "📦 **Batch System:**\n"
        "• Use /batch to create file batches.\n"
        "• Share multiple files with one link.\n"
        "• Forward multiple files and reply with /batch.\n\n"
        "💡 **Tips:**\n"
        "• Use buttons below for quick access.\n"
        "• Shorten links with /short [link].\n"
        "• Auto-delete keeps files organized.\n\n"
        "❓ Need help? Contact support!"
    )
    await message.reply_text(help_text, reply_markup=button_manager.help_button())
