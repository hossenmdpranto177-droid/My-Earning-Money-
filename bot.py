import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_data = {}

# Settings & Rules
DAILY_AD_LIMIT = 100          # দিনে ১০০টি এড দেখবে
AD_REWARD_PER_AD = 0.20        # প্রতি এডে ০.২০ টাকা
REFERRAL_REWARD = 5            # প্রতি ইনভাইটে ৫ টাকা
MIN_WITHDRAWAL = 100           # সর্বনিম্ন উইথড্র ১০০ টাকা
AHMED_WHATSAPP = "8801928749153" # আলামিন ভাইয়ের নাম্বার

# ⚠️ এখানে আপনার নিজের টেলিগ্রাম আইডির নম্বর বসাবেন
ADMIN_CHAT_ID = 7014001047  

def get_user(user_id, referrer_id=None):
    if user_id not in user_data:
        user_data[user_id] = {
            'balance': 0.0,
            'ads_today': 0,
            'referrals': 0,
            'awaiting_withdraw_num': False,
            'withdraw_method': None,
            'referred_by': referrer_id if (referrer_id and referrer_id != user_id) else None,
            'referral_credited': False
        }
    return user_data[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    args = context.args
    referrer_id = int(args[0]) if args and args[0].isdigit() else None
    get_user(user_id, referrer_id)
    
    keyboard = [
        [InlineKeyboardButton("📺 এড দেখে আয় করুন (৪০৳/দিন)", callback_data="watch_ad")],
        [InlineKeyboardButton("📸 কাজের প্রুফ/স্ক্রিনশট পাঠান (বাধ্যতামূলক)", callback_data="send_proof")],
        [InlineKeyboardButton("👥 ইনভাইট করুন (৫৳/রেফার)", callback_data="invite")],
        [InlineKeyboardButton("💰 ব্যালেন্স ও উইথড্র (বিকাশ/নগদ)", callback_data="wallet")],
        [InlineKeyboardButton("💬 আহমেদ ভাইয়ের সাথে যোগাযোগ (WhatsApp)", url=f"https://wa.me/{AHMED_WHATSAPP}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 **জি, আসসালামু আলাইকুম!**\n\n"
        f"🏆 **মেগা পুরষ্কার অফার ও র্যাঙ্কিং প্রতিযোগিতা!** 🏆\n"
        f"যারা এডে ক্লিক করে বেশি বেশি অ্যাপ ইন্সটল করবেন অথবা সাইন আপ করবেন, তাদের মধ্য থেকে র্যাঙ্ক অনুযায়ী পুরষ্কার দেওয়া হবে:\n\n"
        f"🥇 **১ম স্থান:** ৳৫০০ পুরষ্কার\n"
        f"🥈 **২য় স্থান:** ৳ ৩০০ পুরষ্কার\n"
        f"🥉 **৩য় স্থান:** ৳২০০ পুরষ্কার\n"
        f"🎖️ **৪র্থ থেকে ২০তম স্থান:** পাবেন ৳৫০ করে!\n\n"
        f"💡 *তাই এডে ক্লিক করে বেশি করে অ্যাপ ইন্সটল করুন এবং ওয়েবসাইটে সাইন আপ করে স্ক্রিনশট জমা দিন। কারণ আপনাদের এই এডের মাধ্যমে ইনকাম করেই আপনাদেরকে পেমেন্ট করা হবে!*\n\n"
        f"----------------------------------------\n"
        f"📢 **জরুরি নিয়মাবলী:**\n"
        f"১. প্রতিদিন অন্তত **৫টি অ্যাপ ইনস্টল** ও **ওয়েবসাইটে সাইন-আপ** করতে হবে।\n"
        f"২. কাজ শেষে **'📸 কাজের প্রুফ/স্ক্রিনশট পাঠান'** অপশনে প্রমাণ জমা দেওয়া বাধ্যতামূলক।\n"
        f"⚠️️ *রেফার বোনাস পেতে যাকে ইনভাইট করবেন তাকে অবশ্যই এডে ক্লিক করে অ্যাপ ইনস্টল অথবা ওয়েবসাইটে সাইন-আপ সম্পন্ন করতে হবে।*\n\n"
        f"🔹 **এড দেখে আয়:** প্রতিদিন ১০০টি এড দেখে ৪০ টাকা আয়।\n"
        f"🔹 **রেফার:** প্রতি ইনভাইটে ৫ টাকা (শর্ত প্রযোজ্য)।"
    )
    
    if update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user(user_id)
    bot_username = context.bot.username

    if query.data == "watch_ad":
        if data['ads_today'] >= DAILY_AD_LIMIT:
            text = f"⚠️ আপনার আজকের ১০০টি বিজ্ঞাপনের কোটা (৪০৳ আয়) শেষ হয়ে গেছে! আগামীকাল আবার চেষ্টা করুন।"
        else:
            data['ads_today'] += 1
            data['balance'] += AD_REWARD_PER_AD
            
            if data['referred_by'] and not data['referral_credited']:
                ref_id = data['referred_by']
                if ref_id in user_data:
                    user_data[ref_id]['balance'] += REFERRAL_REWARD
                    user_data[ref_id]['referrals'] += 1
                    try:
                        await context.bot.send_message(
                            chat_id=ref_id,
                            text=f"🎉 **রেফার বোনাস সফল!**\nআপনার রেফারকৃত ইউজার এডে ক্লিক করে অ্যাপ ইনস্টল/সাইন-আপ কাজ শুরু করেছেন। আপনার ব্যালেন্সে **{REFERRAL_REWARD} টাকা** যুক্ত করা হয়েছে।"
                        )
                    except Exception:
                        pass
                data['referral_credited'] = True
            
            # 👇 আপনার এড লিঙ্কটি 'https://www.profitableratecpmnetwork.com/zw40wi03u?key=cc5a67fe3140a46961472d6c12ce49b9' এর জায়গায় বসান
            text = (
                f"🎉 **বিজ্ঞাপন দেখা সম্পন্ন হয়েছে!**\n\n"
                f"👉 [এখানে ক্লিক করে অ্যাপ ইন্সটল ও একাউন্ট তৈরি করুন](https://www.profitableratecpmnetwork.com/zw40wi03u?key=cc5a67fe3140a46961472d6c12ce49b9)\n\n"
                f"🔥 **প্রতিযোগিতা চলছে!** বেশি বেশি অ্যাপ ইনস্টল ও সাইন-আপ করে প্রুফ জমা দিয়ে জিতে নিন ৫০০ টাকা পর্যন্ত বাম্পার পুরষ্কার!\n\n"
                f"⚠️ **জরুরি নিয়ম:** এডে ক্লিক করার পর অ্যাপ ইনস্টল বা সাইন-আপ করে তার প্রুফ হিসেবে স্ক্রিনশট তুলে 'প্রুফ পাঠান' অপশনে পাঠিয়ে দিন।\n\n"
                f"💰 ব্যালেন্সে যোগ হয়েছে: **{AD_REWARD_PER_AD} টাকা**\n"
                f"📊 আজ মোট এড দেখেছেন: **{data['ads_today']}/{DAILY_AD_LIMIT}**"
            )
        
        keyboard = [[InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "send_proof":
        text = (
            f"📸 **কাজের প্রমাণ/স্ক্রিনশট জমা দিন:**\n\n"
            f"আপনি এডে ক্লিক করে অ্যাপ ইনস্টল বা ওয়েবসাইটে একাউন্ট তৈরি (সাইন-আপ) করার পর তার একটি পরিষ্কার **স্ক্রিনশট/ছবি** সরাসরি এই বটের চ্যাটে পাঠাবে।"
        )
        keyboard = [[InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "invite":
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        text = (
            f"👥 **রেফার করে আয় করুন!**\n\n"
            f"আপনার বন্ধুকে ইনভাইট করুন। প্রতি সফল রেফারলে পাবেন **৫ টাকা**।\n\n"
            f"⚠️ **বাধ্যতামূলক নিয়ম:** আপনি যাকে ইনভাইট করবেন তাকে অবশ্যই এডে ক্লিক করে **অ্যাপ ইনস্টল অথবা সাইন-আপ করতে হবে**, তানাহলে রেফার বোনাস কাউন্ট হবে না।\n\n"
            f"🔗 **আপনার লিংক:**\n`{ref_link}`\n\n"
            f"📊 সফল রেফার করেছেন: **{data['referrals']} জন**"
        )
        keyboard = [[InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "wallet":
        text = (
            f"💼 **আপনার ওয়ালেট:**\n\n"
            f"💰 বর্তমান ব্যালেন্স: **{data['balance']:.2f} টাকা**\n"
            f"⚠️ সর্বনিম্ন উইথড্র: **{MIN_WITHDRAWAL} টাকা**\n\n"
            f"উইথড্র করতে নিচে আপনার কাঙ্ক্ষিত মাধ্যম বেছে নিন:"
        )
        keyboard = [
            [InlineKeyboardButton("বিকাশ (Bkash)", callback_data="withdraw_bkash"), InlineKeyboardButton("নগদ (Nagad)", callback_data="withdraw_nagad")],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data in ["withdraw_bkash", "withdraw_nagad"]:
        method = "বিকাশ" if query.data == "withdraw_bkash" else "নগদ"
        if data['balance'] < MIN_WITHDRAWAL:
            text = f"⚠️ আপনার পর্যাপ্ত ব্যালেন্স নেই! উইথড্র করতে সর্বনিম্ন **{MIN_WITHDRAWAL} টাকা** লাগবে।"
            keyboard = [[InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]]
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            data['awaiting_withdraw_num'] = True
            data['withdraw_method'] = method
            await query.message.edit_text(f"📱 দয়া করে আপনার **{method} নম্বরটি** মেসেজে লিখে পাঠান:")

    elif query.data == "main_menu":
        await start(update, context)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_file = update.message.photo[-1].file_id
    
    caption = (
        f"📩 **নতুন কাজের স্ক্রিনশট জমা পড়েছে!**\n\n"
        f"👤 নাম: {user.full_name}\n"
        f"🆔 ইউজার আইডি: `{user.id}`\n"
        f"🌐 ইউজারনেম: @{user.username if user.username else 'নাই'}"
    )
    
    if ADMIN_CHAT_ID != 123456789:
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_file, caption=caption, parse_mode="Markdown")
    
    await update.message.reply_text("✅ **আপনার কাজের স্ক্রিনশটটি সফলভাবে জমা হয়েছে!** এডমিন ভেরিফাই করে পেমেন্ট অ্যাপ্রুভ করবেন।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = get_user(user_id)
    
    if data.get('awaiting_withdraw_num'):
        num = update.message.text
        method = data['withdraw_method']
        amount = data['balance']
        
        data['balance'] = 0.0
        data['awaiting_withdraw_num'] = False
        
        admin_msg = (
            f"💰 **নতুন উইথড্র রিকোয়েস্ট!**\n\n"
            f"👤 ইউজার ID: `{user_id}`\n"
            f"📱 মেথড: {method}\n"
            f"🔢 নম্বর: `{num}`\n"
            f"💵 পরিমাণ: {amount} টাকা"
        )
        if ADMIN_CHAT_ID != 123456789:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode="Markdown")
            
        await update.message.reply_text(
            f"✅ **উইথড্র রিকোয়েস্ট সফল হয়েছে!**\n\n"
            f"মেথড: {method}\n"
            f"নম্বর: `{num}`\n"
            f"পরিমাণ: {amount} টাকা\n\n"
            f"২৪ ঘণ্টার মধ্যে আহমেদ ভাই আপনার জমা দেওয়া প্রুফ ভেরিফাই করে পেমেন্ট সম্পন্ন করবেন।"
        )

if __name__ == "__main__":
    TOKEN = "8797976574:AAFW9do7KvNYKPv-U5Rc2PlHwAFJsPU6M-o"
    
    # PythonAnywhere প্রক্সির জন্য সঠিক HTTPXRequest কনফিগারেশন
    req = HTTPXRequest(proxy_url="http://proxy.server:3128")
    
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .request(req)
        .get_updates_request(req)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running...")
    app.run_polling()



