import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatType, ChatMemberStatus
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, SUPPORT_CHAT, DEVELOPER, START_PHOTO
from database import (
    add_user, add_group, remove_group, get_group_settings, set_silent_mode,
    set_custom_warning, is_authorized, add_authorized_user, remove_authorized_user,
    get_authorized_users, get_total_users, get_total_groups, get_all_groups,
    get_all_users
)

# --------------------- BOT INIT ---------------------
app = Client(
    "edit_guard_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Store original start message caption and keyboard for back button
START_CAPTION = f"""**👋 Welcome!**  

I am **Edit Guard Bot**, here to protect your groups from message editing misuse.

🔹 **Features:**    
✅ Auto-delete edited messages from unauthorized users    
✅ Grant/revoke edit permission with `/approve`    
✅ Silent mode – disable warnings    
✅ Custom warning messages    
✅ Admin controls & user status check    
✅ Analytics for bot owner    

📌 **Get Started:**    
- Add me to your group with admin rights.    
- Use `/help` to see all commands.    

Enjoy safe group management! 😊  
"""

# --------------------- START COMMAND ---------------------
@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user = message.from_user
    new_user = add_user(user.id, user.first_name, user.last_name, user.username)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆘 Help", callback_data="help")],
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER),
         InlineKeyboardButton("💬 Support Chat", url=SUPPORT_CHAT)]
    ])

    await message.reply_photo(
        photo=START_PHOTO,
        caption=START_CAPTION,
        reply_markup=keyboard
    )

    if new_user:
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        text = f"📢 New User Started Bot\n👤 Name: {mention}\n🆔 ID: `{user.id}`\n📊 Total Users: {get_total_users()}"
        await client.send_message(OWNER_ID, text)

# --------------------- CALLBACK HANDLER ---------------------
@app.on_callback_query()
async def handle_callback(client: Client, callback_query: CallbackQuery):
    if callback_query.data == "help":
        help_text = f"""**🤖 Bot Commands List**  

**👤 User Commands:**  
/start - Start bot    
/help - Show help    
/mystatus - Check your edit permission status  

**👮 Admin Commands (Group Admins only):**  
/approve or /auth - Allow a user to edit messages (reply or user ID)    
/unapprove or /unauth - Revoke edit permission    
/authusers - List authorized users    
/setwarn - Set a custom warning message    
/silent on/off - Toggle silent mode    
/settings - View group settings  

**👑 Owner Commands:**  
/stats - Bot stats    
/groups - List all groups the bot is in  
/broadcast - Send message to all users (owner only)  

**Need help?** Join our support chat: [Click here]({SUPPORT_CHAT})    
Developer: [Click here]({DEVELOPER})"""

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
        ])

        await callback_query.message.edit_caption(
            caption=help_text,
            reply_markup=back_button
        )
        await callback_query.answer()

    elif callback_query.data == "back":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🆘 Help", callback_data="help")],
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{client.me.username}?startgroup=true")],
            [InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER),
             InlineKeyboardButton("💬 Support Chat", url=SUPPORT_CHAT)]
        ])

        await callback_query.message.edit_caption(
            caption=START_CAPTION,
            reply_markup=keyboard
        )
        await callback_query.answer()

# --------------------- /help COMMAND ---------------------
@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = f"""**🤖 Bot Commands List**  

**👤 User Commands:**  
/start - Start bot    
/help - Show help    
/mystatus - Check your edit permission status  

**👮 Admin Commands (Group Admins only):**  
/approve or /auth - Allow a user to edit messages (reply or user ID)    
/unapprove or /unauth - Revoke edit permission    
/authusers - List authorized users    
/setwarn - Set a custom warning message    
/silent on/off - Toggle silent mode    
/settings - View group settings  

**👑 Owner Commands:**  
/stats - Bot stats    
/groups - List all groups the bot is in  
/broadcast - Send message to all users (owner only)  

**Need help?** Join our support chat: [Click here]({SUPPORT_CHAT})    
Developer: [Click here]({DEVELOPER})"""
    await message.reply(help_text, disable_web_page_preview=True)

# --------------------- /mystatus ---------------------
@app.on_message(filters.command("mystatus") & filters.group)
async def mystatus_command(client: Client, message: Message):
    user_id = message.from_user.id
    group_id = message.chat.id
    authorized = is_authorized(group_id, user_id)
    status = "Yes" if authorized else "No"
    text = f"👤 Your Status\n🔓 Authorized: {status}"
    await message.reply(text)

# --------------------- /approve or /auth ---------------------
@app.on_message(filters.command(["approve", "auth"]) & filters.group)
async def approve_command(client: Client, message: Message):
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply("❌ Only group admins can use this command.")
        return

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        add_authorized_user(message.chat.id, target_user.id, message.from_user.id)
        mention = f"[{target_user.first_name}](tg://user?id={target_user.id})"
        await message.reply(f"✅ {mention} is now authorized to edit messages.")
        return

    args = message.text.split()
    if len(args) == 2:
        try:
            target_id = int(args[1])
            try:
                target_user = await client.get_users(target_id)
            except:
                await message.reply("❌ User not found.")
                return
            add_authorized_user(message.chat.id, target_id, message.from_user.id)
            mention = f"[{target_user.first_name}](tg://user?id={target_id})"
            await message.reply(f"✅ {mention} is now authorized to edit messages.")
        except ValueError:
            await message.reply("❌ Invalid user ID.")
        return

    await message.reply("❌ Usage:\nReply to a message with /approve\nor /approve USER_ID")

# --------------------- /unapprove or /unauth ---------------------
@app.on_message(filters.command(["unapprove", "unauth"]) & filters.group)
async def unapprove_command(client: Client, message: Message):
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply("❌ Only group admins can use this command.")
        return

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        remove_authorized_user(message.chat.id, target_user.id)
        mention = f"[{target_user.first_name}](tg://user?id={target_user.id})"
        await message.reply(f"❌ {mention} is no longer authorized to edit messages.")
        return

    args = message.text.split()
    if len(args) == 2:
        try:
            target_id = int(args[1])
            remove_authorized_user(message.chat.id, target_id)
            await message.reply(f"❌ User `{target_id}` is no longer authorized.")
        except ValueError:
            await message.reply("❌ Invalid user ID.")
        return

    await message.reply("❌ Usage:\nReply to a message with /unapprove\nor /unapprove USER_ID")

# --------------------- /authusers ---------------------
@app.on_message(filters.command("authusers") & filters.group)
async def authusers_command(client: Client, message: Message):
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply("❌ Only group admins can use this command.")
        return

    user_ids = get_authorized_users(message.chat.id)
    if not user_ids:
        await message.reply("📋 No authorized users in this group.")
        return

    text = "📋 Authorized Users:\n\n"
    for user_id in user_ids:
        try:
            user = await client.get_users(user_id)
            mention = f"[{user.first_name}](tg://user?id={user_id})"
            text += f"• {mention}\n"
        except Exception:
            text += f"• User {user_id} (not found)\n"
    await message.reply(text)

# --------------------- /setwarn ---------------------
@app.on_message(filters.command("setwarn") & filters.group)
async def setwarn_command(client: Client, message: Message):
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply("❌ Only group admins can use this command.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ Usage: /setwarn Your custom warning message")
        return

    custom_warning = args[1]
    set_custom_warning(message.chat.id, custom_warning)
    await message.reply(f"✅ Custom warning message set:\n\n{custom_warning}")

# --------------------- /silent on/off ---------------------
@app.on_message(filters.command("silent") & filters.group)
async def silent_command(client: Client, message: Message):
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply("❌ Only group admins can use this command.")
        return

    args = message.text.split()
    if len(args) != 2 or args[1] not in ["on", "off"]:
        await message.reply("❌ Usage: /silent on  or  /silent off")
        return

    silent = args[1] == "on"
    set_silent_mode(message.chat.id, silent)
    status = "ON" if silent else "OFF"
    await message.reply(f"🔇 Silent mode is now {status}.")

# --------------------- /settings ---------------------
@app.on_message(filters.command("settings") & filters.group)
async def settings_command(client: Client, message: Message):
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply("❌ Only group admins can use this command.")
        return

    settings = get_group_settings(message.chat.id)
    silent_mode = "ON" if settings["silent_mode"] else "OFF"
    custom_warning = "Yes" if settings["custom_warning"] else "No"
    auth_count = len(get_authorized_users(message.chat.id))

    text = f"""⚙️ Group Settings  

🔇 Silent Mode: {silent_mode}  
✏️ Custom Warning: {custom_warning}  
👥 Authorized Users: {auth_count}"""
    await message.reply(text)

# --------------------- /stats (owner only) ---------------------
@app.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ This command is only for the bot owner.")
        return

    total_users = get_total_users()
    total_groups = get_total_groups()
    text = f"📊 Bot Stats\n\n👥 Total Users: {total_users}\n🧑‍🤝‍🧑 Total Groups: {total_groups}"
    await message.reply(text)

# --------------------- /groups (owner only) ---------------------
@app.on_message(filters.command("groups") & filters.private)
async def groups_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ This command is only for the bot owner.")
        return

    groups = get_all_groups()
    if not groups:
        await message.reply("📋 Bot is not in any groups.")
        return

    text = "📋 Groups List:\n\n"
    for idx, (group_id, title, username) in enumerate(groups, 1):
        if username:
            link = f"https://t.me/{username}"
        else:
            try:
                chat = await client.get_chat(group_id)
                if chat.permissions and chat.permissions.can_invite_users:
                    invite_link = await client.create_chat_invite_link(group_id, member_limit=1)
                    link = invite_link.invite_link
                else:
                    link = "Link not available"
            except Exception:
                link = "Link not available"

        text += f"{idx}. {title}\n   {link}\n\n"
    await message.reply(text)

# --------------------- BROADCAST (owner only) ---------------------
@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("❌ This command is only for the bot owner.")
        return

    # Determine broadcast content
    broadcast_text = None
    broadcast_media = None
    broadcast_caption = None

    # Case 1: Reply to a message
    if message.reply_to_message:
        broadcast_media = message.reply_to_message
        if broadcast_media.text:
            broadcast_text = broadcast_media.text
        elif broadcast_media.caption:
            broadcast_caption = broadcast_media.caption
        # For media without caption, we'll add header as caption later
    else:
        # Case 2: Text after command
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            broadcast_text = args[1]
        else:
            await message.reply("❌ Usage: /broadcast <message> or reply to a message.")
            return

    # Prepare the message with announcement header
    header = "📢 **Announcement by EditGuard Bot**\n\n"
    if broadcast_text:
        # Text message
        final_content = header + broadcast_text
    elif broadcast_media:
        # Media message
        if broadcast_media.photo:
            media_type = "photo"
            file_id = broadcast_media.photo.file_id
            final_caption = header + (broadcast_caption if broadcast_caption else "")
        elif broadcast_media.video:
            media_type = "video"
            file_id = broadcast_media.video.file_id
            final_caption = header + (broadcast_caption if broadcast_caption else "")
        elif broadcast_media.document:
            media_type = "document"
            file_id = broadcast_media.document.file_id
            final_caption = header + (broadcast_caption if broadcast_caption else "")
        else:
            await message.reply("❌ Unsupported media type.")
            return
    else:
        await message.reply("❌ No valid content to broadcast.")
        return

    # Get all users
    users = get_all_users()
    if not users:
        await message.reply("📋 No users in database.")
        return

    status_msg = await message.reply(f"📢 Broadcasting to {len(users)} users...")
    success = 0
    failed = 0

    for user_id in users:
        try:
            if broadcast_text:
                await client.send_message(user_id, final_content)
            elif broadcast_media:
                if media_type == "photo":
                    await client.send_photo(user_id, file_id, caption=final_caption)
                elif media_type == "video":
                    await client.send_video(user_id, file_id, caption=final_caption)
                elif media_type == "document":
                    await client.send_document(user_id, file_id, caption=final_caption)
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # avoid flood wait

    await status_msg.edit_text(f"📢 Broadcast completed.\n✅ Sent: {success}\n❌ Failed: {failed}")

# --------------------- ANTI-EDIT HANDLER ---------------------
@app.on_edited_message()
async def handle_edit(client: Client, message: Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return

    user = message.from_user
    if not user:
        return

    try:
        member = await message.chat.get_member(user.id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
    except Exception:
        pass

    group_id = message.chat.id
    settings = get_group_settings(group_id)

    if is_authorized(group_id, user.id):
        return

    try:
        await message.delete()
    except Exception:
        pass

    if not settings["silent_mode"]:
        if settings["custom_warning"]:
            warning_text = settings["custom_warning"]
        else:
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            warning_text = f'❌ {mention}\nEdit message allowed nahi hai!'

        warning_msg = await message.reply(warning_text)
        await asyncio.sleep(7)
        try:
            await warning_msg.delete()
        except Exception:
            pass

# --------------------- GROUP JOIN/LEAVE HANDLERS ---------------------
@app.on_chat_member_updated()
async def chat_member_update(client: Client, update):
    if update.new_chat_member and update.new_chat_member.user.id == client.me.id:
        chat = update.chat
        add_group(chat.id, chat.title, chat.username, str(chat.type))
        text = f"➕ Bot added to group: {chat.title} (ID: {chat.id})"
        await client.send_message(OWNER_ID, text)

    elif update.old_chat_member and update.old_chat_member.user.id == client.me.id:
        chat_id = update.chat.id
        remove_group(chat_id)
        text = f"➖ Bot removed from group: {update.chat.title} (ID: {chat_id})"
        await client.send_message(OWNER_ID, text)

# --------------------- MAIN ---------------------
if __name__ == "__main__":
    print("Bot started...")
    app.run()
