from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, Voice, PhotoSize
import asyncio

# Replace with the token from BotFather
TOKEN = '8112767062:AAFN7Rod9qYYbtuFSlCu1tc1_k23JVes4G8'

# Admin ID
ADMIN_ID = 7439508908

# Dictionary to store paired users and all users
paired_users = {}
all_users = set()  # To store all users who used /start
broadcast_group = {}  # To store users with their anonymous index
poll_data = {}  # To store poll question and votes {group_id: {"question": str, "yes": int, "no": int, "voters": set}}
waiting_users = []  # To store users waiting to be paired

# Menu keyboard setup with emojis (Admin-specific)
admin_menu_keyboard = ReplyKeyboardMarkup([
    ['💬 Anonymous Chat', '📤 Anonymous Groups', '📤 Broadcast'],
    ['🆘 Help']
], resize_keyboard=True)

# Menu keyboard setup with emojis (Regular users)
user_menu_keyboard = ReplyKeyboardMarkup([
    ['💬 Anonymous Chat', '📤 Anonymous Groups'],
    ['🆘 Help']
], resize_keyboard=True)

# Chat-specific keyboard
chat_keyboard = ReplyKeyboardMarkup([
    ['🚪 End Chat', '📡 Send Status']
], resize_keyboard=True)

# Broadcast group keyboard
broadcast_keyboard = ReplyKeyboardMarkup([
    ['🚪 Leave', '📊 View Members']
], resize_keyboard=True)

# Poll voting keyboard
poll_keyboard = ReplyKeyboardMarkup([
    ['💟 Yes', '💔 No', '/viewpoll'],
    ['/resetpoll']
], resize_keyboard=True)

async def start(update, context):
    user_id = update.effective_user.id
    all_users.add(user_id)  # Add user to all_users set
    if user_id not in paired_users:
        await update.message.reply_text(
            "👋 ကြိုဆိုပါတယ်! တခြားသူတစ်ဦးနဲ့ စကားပြောဖို့ (💬 Anonymous Chat) သို့မဟုတ် Anonymous Groups မှာ မက်ဆေ့ချ်ပို့ဖို့ အောက်က button တွေကို သုံးပါ။ 😊",
            reply_markup=admin_menu_keyboard if user_id == ADMIN_ID else user_menu_keyboard
        )
        paired_users[user_id] = None
    else:
        await update.message.reply_text(
            "🙌 သင်သည် ကြိုတင်စတင်ပြီးသား ဖြစ်ပါတယ်။ အောက်က button တွေကို သုံးပါ။",
            reply_markup=admin_menu_keyboard if user_id == ADMIN_ID else user_menu_keyboard
        )

async def join(update, context):
    user_id = update.effective_user.id
    if user_id in paired_users and paired_users[user_id] is not None:
        await update.message.reply_text(
            "❌ သင်သည် ချိတ်ဆက်ပြီးသားဖြစ်ပါတယ်။ 🚪 End Chat နှိပ်ပြီး နောက်တစ်ယောက်ရှာနိုင်ပါတယ်။",
            reply_markup=chat_keyboard
        )
        return

    # If user is already in waiting list, remove them to avoid duplicates
    if user_id in waiting_users:
        waiting_users.remove(user_id)

    # Add user to waiting list
    waiting_users.append(user_id)
    paired_users[user_id] = None

    # Check if there is another user waiting to pair
    if len(waiting_users) >= 2:
        user1 = waiting_users.pop(0)  # First waiting user
        user2 = waiting_users.pop(0)  # Second waiting user

        paired_users[user1] = user2
        paired_users[user2] = user1

        await context.bot.send_message(
            chat_id=user1,
            text="🎉 Friend {} နဲ့ ချိတ်ဆက်ပြီးပါတယ်! 💬 စာပို့ပြီး စကားစမြည်ပြောနိုင်ပါတယ်။ 🌟".format(user2),
            reply_markup=chat_keyboard
        )
        await context.bot.send_message(
            chat_id=user2,
            text="🎉 Friend {} နဲ့ ချိတ်ဆက်ပြီးပါတယ်! 💬 စာပို့ပြီး စကားစမြည်ပြောနိုင်ပါတယ်။ 🌟".format(user1),
            reply_markup=chat_keyboard
        )
    else:
        await update.message.reply_text(
            "⏳ တခြားသူတစ်ဦးကို စောင့်နေပါတယ်... (တစ်ဖက်လူကလည်း 💬 Anonymous Chat နှိပ်ရပါမယ်။)",
            reply_markup=admin_menu_keyboard if user_id == ADMIN_ID else user_menu_keyboard
        )

async def end(update, context):
    user_id = update.effective_user.id
    if user_id in paired_users and paired_users[user_id] is not None:
        partner_id = paired_users[user_id]
        paired_users[user_id] = None
        paired_users[partner_id] = None
        # Remove users from waiting list if they are there
        if user_id in waiting_users:
            waiting_users.remove(user_id)
        if partner_id in waiting_users:
            waiting_users.remove(partner_id)
        await context.bot.send_message(
            chat_id=user_id,
            text="👋 Chat ကို အဆုံးသတ်လိုက်ပါပြီ။ 💬 Anonymous Chat နဲ့ နောက်တစ်ယောက်ရှာပါ။ 😊",
            reply_markup=admin_menu_keyboard if user_id == ADMIN_ID else user_menu_keyboard
        )
        await context.bot.send_message(
            chat_id=partner_id,
            text="👋 Friend က chat ကို အဆုံးသတ်လိုက်ပါပြီ။ 💬 Anonymous Chat နဲ့ နောက်တစ်ယောက်ရှာပါ။ 😊",
            reply_markup=admin_menu_keyboard if partner_id == ADMIN_ID else user_menu_keyboard
        )
    else:
        await update.message.reply_text("❌ သင်သည် မည်သူနှင့်မျှ ချိတ်ဆက်မထားပါ။ 💬 Anonymous Chat နဲ့ စတင်ပါ။", reply_markup=admin_menu_keyboard if user_id == ADMIN_ID else user_menu_keyboard)

async def help(update, context):
    user_id = update.effective_user.id
    help_text = (
        "📖 **Help Menu**\n\n"
        "💬 Anonymous Chat - တခြားသူတစ်ဦးနဲ့ ချိတ်ဆက်ပါ (နှစ်ဦးလုံး နှိပ်ထားမှ ချိတ်ဆက်မှာဖြစ်ပါတယ်)\n\n"
        "🚪 End Chat - လက်ရှိ chat ကို အဆုံးသတ်ပါ\n\n"
        "📡 Send Status - သင့်လက်ရှိ Chat အခြေအနေကို စစ်ကြည့်ပါ\n\n"
        "📤 Anonymous Groups - အားလုံးထံသို့ မက်ဆေ့ချ်ပို့ပါ (Anonymous Group ထဲရောက်မယ်)\n\n"
        "📊 View Members - Anonymous Group ထဲက အဖွဲ့ဝင်များကို ကြည့်ပါ\n\n"
    )
    if user_id == ADMIN_ID:
        help_text += (
            "📤 Broadcast - အကုန်လုံးထံသို့ မက်ဆေ့ချ်၊ ပုံ၊ လင့်ပို့ပါ\n\n"
            "📝 Create Poll - Anonymous Group ထဲမှာ Poll ဖန်တီးပါ\n\n"
            "/viewpoll - Poll ရလဒ်ကို ကြည့်ပါ\n\n"
            "/resetpoll - Poll ကို ပြန်စပါ\n\n"
        )
    help_text += (
        "🚪 Leave - Anonymous Group ကနေ ထွက်ပါ\n\n"
        "အကယ်၍ ပြဿနာရှိရင် Bot ကို /start ပြန်စတင်ကြည့်ပါ။"
    )
    await update.message.reply_text(help_text, reply_markup=admin_menu_keyboard if user_id == ADMIN_ID else user_menu_keyboard)

async def handle_message(update, context):
    user_id = update.effective_user.id
    message_text = update.message.text

    # Handle keyboard button presses
    if message_text == "💬 Anonymous Chat":
        await join(update, context)
        return
    elif message_text == "🚪 End Chat":
        await end(update, context)
        return
    elif message_text == "🆘 Help":
        await help(update, context)
        return
    elif message_text == "📡 Send Status":
        status = "သင်သည် မည်သူနှင့်မျှ ချိတ်ဆက်မထားပါ" if paired_users.get(user_id) is None else f"သင်သည် Friend {paired_users[user_id]} နှင့် ချိတ်ဆက်ထားပါတယ်"
        await update.message.reply_text(
            f"📡 **Your Status**\nStatus: {status}",
            reply_markup=chat_keyboard if paired_users.get(user_id) is not None else (admin_menu_keyboard if user_id == ADMIN_ID else user_menu_keyboard)
        )
        return
    elif message_text == "📤 Anonymous Groups":
        if user_id not in broadcast_group:
            broadcast_group[user_id] = len(broadcast_group) + 1  # Assign anonymous index
            await update.message.reply_text(
                "📤 သင်သည် Anonymous Group ထဲရောက်ပါတယ်။ အခုချက်ချင်းမက်ဆေ့ချ်ရိုက်ထည့်ပြီး ပို့လိုက်ပါ။",
                reply_markup=broadcast_keyboard
            )
        else:
            await update.message.reply_text(
                "📤 သင်သည် ကြိုတင်ရောက်နေပြီ။ မက်ဆေ့ချ်ရိုက်ထည့်ပြီး ပို့ပါ။",
                reply_markup=broadcast_keyboard
            )
        return
    elif message_text == "📊 View Members" and user_id in broadcast_group:
        if broadcast_group:
            members = [f"Anonymous {index}" for user, index in broadcast_group.items()]
            members_list = "\n".join(members)
            await update.message.reply_text(
                f"📊 **Group Members**\n{members_list}",
                reply_markup=broadcast_keyboard
            )
        else:
            await update.message.reply_text(
                "📊 **Group Members**\nအဖွဲ့ဝင်မရှိပါ။",
                reply_markup=broadcast_keyboard
            )
        return
    elif message_text == "📝 Create Poll" and user_id == ADMIN_ID and user_id in broadcast_group:
        if "question" in poll_data:
            await update.message.reply_text(
                "📝 လက်ရှိ Poll တစ်ခုရှိနေပါတယ်။ /resetpoll နဲ့ ရှင်းလိုက်ပြီး အသစ်ဖန်တီးပါ။",
                reply_markup=broadcast_keyboard
            )
        else:
            context.user_data["creating_poll"] = True
            await update.message.reply_text(
                "📝 Poll အတွက် မေးခွန်းတစ်ခုရိုက်ထည့်ပါ (Yes/No ပုံစံဖြစ်ရမယ်)။",
                reply_markup=broadcast_keyboard
            )
        return
    elif message_text == "📤 Broadcast" and user_id == ADMIN_ID:
        context.user_data["broadcasting"] = True
        await update.message.reply_text(
            "📤 Broadcast အတွက် မက်ဆေ့ချ်၊ ပုံ၊ သို့မဟုတ် လင့်တစ်ခုရိုက်ထည့်ပြီး ပို့ပါ။",
            reply_markup=admin_menu_keyboard
        )
        return
    elif message_text == "/viewpoll" and user_id in broadcast_group:
        if "question" in poll_data:
            question = poll_data["question"]
            yes_votes = poll_data["yes"]
            no_votes = poll_data["no"]
            await update.message.reply_text(
                f"📊 **Poll Results**\nQuestion: {question}\nYes: {yes_votes}\nNo: {no_votes}",
                reply_markup=poll_keyboard
            )
        else:
            await update.message.reply_text(
                "📝 လက်ရှိမှာ Poll မရှိပါ။",
                reply_markup=broadcast_keyboard
            )
        return
    elif message_text == "/resetpoll" and user_id in broadcast_group:
        poll_data.clear()
        for target_user in broadcast_group.keys():
            try:
                await context.bot.send_message(
                    chat_id=target_user,
                    text="📝 Poll ကို ရှင်းလိုက်ပါပြီ။ အသစ်ဖန်တီးနိုင်ပါတယ်။",
                    reply_markup=broadcast_keyboard
                )
            except Exception as e:
                pass
        return
    elif message_text == "💟 Yes" and user_id in broadcast_group and "question" in poll_data:
        if user_id not in poll_data["voters"]:
            poll_data["yes"] += 1
            poll_data["voters"].add(user_id)
            await update.message.reply_text(
                "✅ သင့်မဲကို မှတ်တမ်းတင်လိုက်ပါတယ်။ /viewpoll နဲ့ ရလဒ်ကြည့်ပါ။",
                reply_markup=poll_keyboard
            )
        else:
            await update.message.reply_text(
                "❌ သင်သည် မဲပေးပြီးဖြစ်ပါတယ်။ /viewpoll နဲ့ ရလဒ်ကြည့်ပါ။",
                reply_markup=poll_keyboard
            )
        return
    elif message_text == "💔 No" and user_id in broadcast_group and "question" in poll_data:
        if user_id not in poll_data["voters"]:
            poll_data["no"] += 1
            poll_data["voters"].add(user_id)
            await update.message.reply_text(
                "✅ သင့်မဲကို မှတ်တမ်းတင်လိုက်ပါတယ်။ /viewpoll နဲ့ ရလဒ်ကြည့်ပါ။",
                reply_markup=poll_keyboard
            )
        else:
            await update.message.reply_text(
                "❌ သင်သည် မဲပေးပြီးဖြစ်ပါတယ်။ /viewpoll နဲ့ ရလဒ်ကြည့်ပါ။",
                reply_markup=poll_keyboard
            )
        return
    elif message_text == "🚪 Leave" and user_id in broadcast_group:
        del broadcast_group[user_id]
        await update.message.reply_text(
            "🚪 သင်သည် Anonymous Group မှ ထွက်လိုက်ပါတယ်။",
            reply_markup=admin_menu_keyboard if user_id == ADMIN_ID else user_menu_keyboard
        )
        if not broadcast_group:  # If group is empty, reset poll
            poll_data.clear()
        return

    # Handle poll creation
    if context.user_data.get("creating_poll", False) and user_id == ADMIN_ID and user_id in broadcast_group:
        if update.message.text:
            poll_question = update.message.text
            poll_data["question"] = poll_question
            poll_data["yes"] = 0
            poll_data["no"] = 0
            poll_data["voters"] = set()
            context.user_data["creating_poll"] = False
            for target_user in broadcast_group.keys():
                try:
                    await context.bot.send_message(
                        chat_id=target_user,
                        text=f"📝 **New Poll**\nQuestion: {poll_question}\n💟 Yes / 💔 No နှိပ်ပြီး မဲပေးပါ။",
                        reply_markup=poll_keyboard
                    )
                except Exception as e:
                    pass
        return

    # Handle broadcast
    if context.user_data.get("broadcasting", False) and user_id == ADMIN_ID:
        if update.message.text:
            broadcast_message = update.message.text
            for target_user in all_users:
                try:
                    await context.bot.send_message(
                        chat_id=target_user,
                        text=f"📤 Team ဘက်မှ ကြော်ငြာချက်: {broadcast_message}"
                    )
                except Exception as e:
                    pass
            context.user_data["broadcasting"] = False
            await update.message.reply_text("📤 Broadcast ပို့လိုက်ပါတယ်။", reply_markup=admin_menu_keyboard)
        elif update.message.photo:
            photo = update.message.photo[-1]
            for target_user in all_users:
                try:
                    await context.bot.send_photo(
                        chat_id=target_user,
                        photo=photo.file_id,
                        caption="📤 Team ဘက်မှ ကြော်ငြာချက်: Photo"
                    )
                except Exception as e:
                    pass
            context.user_data["broadcasting"] = False
            await update.message.reply_text("📤 Broadcast Photo ပို့လိုက်ပါတယ်။", reply_markup=admin_menu_keyboard)
        return

    # Handle broadcast message in Anonymous Groups
    if user_id in broadcast_group and update.message.text:
        broadcast_message = update.message.text
        user_index = broadcast_group[user_id]
        for target_user in broadcast_group.keys():
            if target_user != user_id:  # Avoid sending to self
                try:
                    await context.bot.send_message(
                        chat_id=target_user,
                        text=f"Anonymous {user_index}: {broadcast_message}",
                        reply_markup=broadcast_keyboard
                    )
                except Exception as e:
                    pass
        return

    # Handle messaging between paired users
    if user_id in paired_users and paired_users[user_id] is not None:
        partner_id = paired_users[user_id]
        if partner_id in paired_users and paired_users[partner_id] == user_id:  # Ensure bidirectional pairing
            if update.message.text:
                message_text = update.message.text
                try:
                    await context.bot.send_message(
                        chat_id=partner_id,
                        text=message_text  # Send only to partner, no reply to self
                    )
                except Exception as e:
                    await update.message.reply_text("Error sending message: Try again.", reply_markup=chat_keyboard)
            elif update.message.voice:
                voice = update.message.voice
                try:
                    await context.bot.send_voice(
                        chat_id=partner_id,
                        voice=voice.file_id,
                        reply_markup=chat_keyboard
                    )
                except Exception as e:
                    await update.message.reply_text("Error sending voice: Try again.", reply_markup=chat_keyboard)
            elif update.message.photo:
                photo = update.message.photo[-1]
                try:
                    await context.bot.send_photo(
                        chat_id=partner_id,
                        photo=photo.file_id,
                        reply_markup=chat_keyboard
                    )
                except Exception as e:
                    await update.message.reply_text("Error sending photo: Try again.", reply_markup=chat_keyboard)
        else:
            await update.message.reply_text(
                "❌ ချိတ်ဆက်မှု ပြတ်တောက်သွားပါပြီ။ 🚪 End Chat နှိပ်ပြီး ပြန်စပါ။",
                reply_markup=chat_keyboard
            )

def main():
    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Startup message to console
    print("Bot စတင်နေပါသည်...")

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("end", end))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(MessageHandler(
        filters.Regex("^(💬 Anonymous Chat|🚪 End Chat|🆘 Help|📡 Send Status|📤 Anonymous Groups|📊 View Members|📤 Broadcast|📝 Create Poll|💟 Yes|💔 No|/viewpoll|/resetpoll|🚪 Leave)$"),
        handle_message
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(💬 Anonymous Chat|🚪 End Chat|🆘 Help|📡 Send Status|📤 Anonymous Groups|📊 View Members|📤 Broadcast|📝 Create Poll|💟 Yes|💔 No|/viewpoll|/resetpoll|🚪 Leave)$"),
        handle_message
    ))
    application.add_handler(MessageHandler(filters.VOICE | filters.PHOTO, handle_message))

    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
