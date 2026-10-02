import telebot
from telebot import types
import pyrebase
import json
import time
import re
import os
import threading
from datetime import datetime, timedelta
import pickle
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = "8843626230:AAE5n53CaLxYoTFc1w5FFrDb4Q6kCMy-Q08"
ADMIN_ID = 6769245930
CHANNEL_LINK = "https://t.me/+dw1_dzdlnGcyNjQ1"
CHANNEL_ID = -1002256465587
FIREBASE_DATA_CHANNEL = -1004314858694

DATA_FILE = "bot_data.pkl"
VERSION_FILE = "bot_version.txt"

BOT_VERSION = "6.6.6.6"
LAST_UPDATE_TIME = datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')

# ==================== Message Lock System ====================
user_locked_messages = {}
# ==================================================================

def get_bot_version():
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                return f.read().strip()
        return BOT_VERSION
    except:
        return BOT_VERSION

def save_bot_version():
    try:
        with open(VERSION_FILE, 'w') as f:
            f.write(BOT_VERSION)
        logger.info(f"✅ Bot version saved: {BOT_VERSION}")
    except Exception as e:
        logger.error(f"❌ Error saving version: {e}")

def check_user_version(user_id):
    try:
        user_version_file = f"user_version_{user_id}.txt"
        if os.path.exists(user_version_file):
            with open(user_version_file, 'r') as f:
                saved_version = f.read().strip()
                return saved_version == BOT_VERSION
        return False
    except:
        return False

def update_user_version(user_id):
    try:
        user_version_file = f"user_version_{user_id}.txt"
        with open(user_version_file, 'w') as f:
            f.write(BOT_VERSION)
        return True
    except:
        return False

def get_update_message():
    return f"""
╔═════════════════════╗
    𝗨𝗣𝗗𝗔𝗧𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬
╚═════════════════════╝

📌 <b>New Version:</b> <code>{BOT_VERSION}</code>
🕐 <b>Update Time:</b> {LAST_UPDATE_TIME}

━━━━━━━━━━━━━━━━━━━━━━

⚠️ <b>IMPORTANT NOTICE</b> ⚠️

Bot has been updated/restarted!
Please click <b>/start</b> to continue using the bot.

━━━━━━━━━━━━━━━━━━━━━━

❌ <b>Old commands will not work</b>
✅ <b>Click /start to activate</b>

━━━━━━━━━━━━━━━━━━━━━━

💡 <i>Your previous data is safe and saved</i>
"""

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

user_states = {}
user_firebase = {}
user_firebase_count = {}
user_connected_device = {}
user_selected_sim = {}
user_channel_data = {}
user_otp_channel = {}
user_last_activity = {}
user_chat_messages = {}
user_balance = {}
user_notify_off = {}
user_all_ids = set()
user_last_hello_message = {}
bot_mode = True
user_subscription = {}
admin_subscription_states = {}
user_forward_number = {}
user_forward_states = {}
user_devices = {}
user_notify_channel = {}
device_status_msg = {}
device_previous_notify_status = {}

# Token Channel Storage
user_token_channel = {}
user_token_active = {}

# OTP monitoring
otp_monitoring = {}
user_last_message_keys = {}

def save_data():
    try:
        data = {
            'user_firebase': user_firebase,
            'user_firebase_count': user_firebase_count,
            'user_otp_channel': user_otp_channel,
            'user_balance': user_balance,
            'user_notify_off': user_notify_off,
            'user_all_ids': list(user_all_ids),
            'user_connected_device': user_connected_device,
            'user_selected_sim': user_selected_sim,
            'user_channel_data': user_channel_data,
            'user_last_activity': user_last_activity,
            'bot_mode': bot_mode,
            'user_token_channel': user_token_channel,
            'user_token_active': user_token_active,
            'user_subscription': user_subscription,
            'user_forward_number': user_forward_number,
            'user_devices': user_devices,
            'user_notify_channel': user_notify_channel,
            'device_status_msg': device_status_msg,
            'device_previous_notify_status': device_previous_notify_status,
            'user_locked_messages': {uid: {path: list(keys) for path, keys in paths.items()} for uid, paths in user_locked_messages.items()}
        }
        with open(DATA_FILE, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"✅ Data saved to {DATA_FILE}")
    except Exception as e:
        logger.error(f"❌ Error saving data: {e}")

def load_data():
    global bot_mode
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'rb') as f:
                data = pickle.load(f)
            
            user_firebase.update(data.get('user_firebase', {}))
            user_firebase_count.update(data.get('user_firebase_count', {}))
            user_otp_channel.update(data.get('user_otp_channel', {}))
            user_balance.update(data.get('user_balance', {}))
            user_notify_off.update(data.get('user_notify_off', {}))
            user_all_ids.update(data.get('user_all_ids', []))
            user_connected_device.update(data.get('user_connected_device', {}))
            user_selected_sim.update(data.get('user_selected_sim', {}))
            user_channel_data.update(data.get('user_channel_data', {}))
            user_last_activity.update(data.get('user_last_activity', {}))
            bot_mode = data.get('bot_mode', True)
            user_token_channel.update(data.get('user_token_channel', {}))
            user_token_active.update(data.get('user_token_active', {}))
            user_subscription.update(data.get('user_subscription', {}))
            user_forward_number.update(data.get('user_forward_number', {}))
            user_devices.update(data.get('user_devices', {}))
            user_notify_channel.update(data.get('user_notify_channel', {}))
            device_status_msg.update(data.get('device_status_msg', {}))
            device_previous_notify_status.update(data.get('device_previous_notify_status', {}))
            
            loaded_locked = data.get('user_locked_messages', {})
            for uid, paths in loaded_locked.items():
                user_locked_messages[uid] = {path: set(keys) for path, keys in paths.items()}
            
            logger.info(f"✅ Data loaded from {DATA_FILE}")
            logger.info(f"📊 Total Users: {len(user_all_ids)}")
            return True
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        return False

def auto_save():
    while True:
        time.sleep(300)
        save_data()

save_thread = threading.Thread(target=auto_save, daemon=True)
save_thread.start()

def auto_hello_checker():
    while True:
        try:
            current_time = datetime.now()
            for user_id in list(user_last_activity.keys()):
                try:
                    last_active = user_last_activity.get(user_id)
                    if last_active:
                        time_diff = current_time - last_active
                        if time_diff.total_seconds() > 900:
                            if user_id in user_last_hello_message:
                                try:
                                    bot.delete_message(user_id, user_last_hello_message[user_id])
                                except:
                                    pass
                                del user_last_hello_message[user_id]
                            
                            if check_user_version(user_id) or user_id == ADMIN_ID:
                                try:
                                    msg = bot.send_message(user_id, "🩵 𝗛𝗘𝗟𝗟𝗢 𝗜'𝗠 𝗥𝗘𝗔𝗗𝗬 𝗙𝗢𝗥 𝗬𝗢𝗨 🩵")
                                    user_last_hello_message[user_id] = msg.message_id
                                except:
                                    pass
                            user_last_activity[user_id] = current_time
                except:
                    pass
        except:
            pass
        time.sleep(60)

hello_thread = threading.Thread(target=auto_hello_checker, daemon=True)
hello_thread.start()

def check_version_and_notify(user_id, chat_id):
    """Returns True if user can proceed, False if blocked (needs /start)"""
    if user_id == ADMIN_ID:
        return True
    
    if not check_user_version(user_id):
        safe_send_message(chat_id, get_update_message())
        return False
    return True

def update_user_activity(user_id):
    user_last_activity[user_id] = datetime.now()

def safe_send_message(chat_id, text, reply_markup=None, track=True):
    try:
        msg = bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode='HTML')
        return msg
    except Exception as e:
        logger.error(f"Send message error: {e}")
        try:
            msg = bot.send_message(chat_id, text, reply_markup=reply_markup)
            return msg
        except Exception as e2:
            logger.error(f"Plain text send also failed: {e2}")
            return None

def check_bot_mode(user_id):
    if user_id == ADMIN_ID:
        return True
    if is_user_subscribed(user_id):
        return True
    return bot_mode

def check_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

def count_clients_in_firebase(db):
    try:
        clients = db.child("clients").get()
        count = 0
        if clients.each():
            for _ in clients.each():
                count += 1
        return count
    except:
        return 0

def is_user_subscribed(user_id):
    try:
        if user_id in user_subscription:
            expiry = datetime.strptime(user_subscription[user_id], '%d/%m/%Y')
            return expiry > datetime.now()
        return False
    except:
        return False

def is_firebase_url_used_by_user(user_id, db_url):
    db_url = db_url.strip().rstrip('/')
    fb_list = user_firebase.get(user_id, {})
    for fb_id, fb_data in fb_list.items():
        if fb_data.get("url", "").strip().rstrip('/') == db_url:
            return True
    return False

def connect_firebase(db_url):
    try:
        db_url = db_url.strip()
        if not db_url.startswith("https://"):
            return None, None, 0
        
        config = {
            "apiKey": "AIzaSyDummyKeyForRealTimeDB",
            "authDomain": "test.firebaseapp.com",
            "databaseURL": db_url,
            "storageBucket": "test.appspot.com"
        }
        
        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
        db.child("/").get()
        client_count = count_clients_in_firebase(db)
        return firebase, db, client_count
    except Exception as e:
        logger.error(f"Firebase connection error: {e}")
        return None, None, 0

def get_online_clients(db):
    try:
        clients = db.child("clients").get()
        online_clients = []
        if clients.each():
            for client in clients.each():
                client_data = client.val()
                if client_data and client_data.get("status") == True:
                    online_clients.append({
                        "id": client.key(),
                        "data": client_data
                    })
        return online_clients
    except:
        return []

def get_client_by_id(db, client_id):
    try:
        client = db.child("clients").child(client_id).get()
        return client.val()
    except:
        return None

def is_client_online(db, client_id):
    try:
        client = db.child("clients").child(client_id).get()
        client_data = client.val()
        if client_data and client_data.get("status") == True:
            return True
        return False
    except:
        return False

def join_channel(channel_input):
    try:
        channel_input = channel_input.strip()
        
        if "t.me/" in channel_input:
            if "+" in channel_input:
                invite = channel_input.split("+")[-1]
                try:
                    chat = bot.get_chat(f"-100{invite}")
                except:
                    chat = bot.get_chat(f"https://t.me/joinchat/{invite}")
            else:
                username = channel_input.split("t.me/")[-1]
                chat = bot.get_chat(f"@{username}")
        elif channel_input.startswith("-100"):
            chat = bot.get_chat(int(channel_input))
        elif channel_input.startswith("@"):
            chat = bot.get_chat(channel_input)
        else:
            try:
                chat = bot.get_chat(int(channel_input))
            except:
                chat = bot.get_chat(f"@{channel_input}")
        
        return chat.id, chat.title
    except Exception as e:
        logger.error(f"Join channel error: {e}")
        return None, None

def extract_sms_details(msg_text):
    to_number = None
    sms_message = None
    msg_text = msg_text.strip()
    
    to_patterns = [
        r'(?:To|to)\s*(?:\(Tap to copy\))?\s*:\s*([+\d\s-]+)',
        r'(?:📞\s*)?To\s*:\s*([+\d\s-]+)',
        r'(?:Number|Phone|Target)\s*:\s*([+\d\s-]+)',
        r'\+?\d{10,15}',
    ]
    
    for pattern in to_patterns:
        match = re.search(pattern, msg_text)
        if match:
            to_number = match.group(1) if match.lastindex else match.group(0)
            to_number = re.sub(r'[\s-]', '', to_number)
            if len(to_number) == 10:
                to_number = '+91' + to_number
            elif len(to_number) > 10 and not to_number.startswith('+'):
                to_number = '+' + to_number
            break
    
    msg_patterns = [
        r'(?:Massage|massage)\s*(?:\(Tap to copy\))?\s*:\s*(.+?)(?:\n|$)',
        r'(?:Message|message)\s*(?:\(Tap to copy\))?\s*:\s*(.+?)(?:\n|$)',
        r'(?:Body|body)\s*(?:\(Tap to copy\))?\s*:\s*(.+?)(?:\n|$)',
        r'(?:MSG|SMS|Text|Content)\s*:\s*(.+?)(?:\n|$)',
        r'(?:💬\s*)?(?:Message|MSG)\s*:\s*(.+?)(?:\n📋|\n━━|$)',
        r'📋\s*One-tap copy\s*:\s*\n?(.+)',
        r'📋\s*Copy\s*:\s*\n?(.+)',
    ]
    
    for pattern in msg_patterns:
        match = re.search(pattern, msg_text, re.DOTALL | re.IGNORECASE)
        if match:
            sms_message = match.group(1).strip()
            sms_message = sms_message.split('\n')[0].strip()
            break
    
    if not sms_message and to_number:
        lines = msg_text.split('\n')
        for i, line in enumerate(lines):
            if to_number in line.replace(' ', '').replace('-', ''):
                for j in range(i+1, min(i+3, len(lines))):
                    clean_line = lines[j].strip()
                    if clean_line and not clean_line.startswith(('To', '📞', '📱', '👤', '📋', '━━')):
                        sms_message = clean_line
                        break
                break
    
    return to_number, sms_message

def check_recharge_per_sim_smart(db, client_id, sim_number):
    try:
        paths = [
            f"messages/{client_id}",
            f"clients/{client_id}/messages",
            f"Messages/{client_id}",
        ]
        
        cutoff_date = datetime.now() - timedelta(days=10)
        
        recharge_expired_keywords = [
            "recharge expired", "validity expired", "plan expired",
            "recharge your number", "no outgoing", "outgoing barred",
            "incoming barred", "service suspended", "your plan has expired",
            "validity over", "recharge khatam", "plan khatam",
            "recharge due", "insufficient balance", "zero balance",
            "outgoing facility barred", "incoming facility barred",
            "रिचार्ज समाप्त", "रिचार्ज खत्म", "वैधता समाप्त",
            "आउटगोइंग बंद", "इनकमिंग बंद", "सेवा निलंबित",
            "आपका प्लान समाप्त", "प्लान समाप्त", "वैधता खत्म",
            "कृपया रिचार्ज करें", "रिचार्ज करवाएं", "रिचार्ज की आवश्यकता",
            "आपका नंबर बंद", "बैलेंस कम", "शून्य बैलेंस",
            "बैलेंस नहीं", "पर्याप्त बैलेंस नहीं",
            "रीचार्ज एक्सपायर", "रीचार्ज समाप्त", "रीचार्ज खत्म",
        ]
        
        recharge_success_keywords = [
            "recharge successful", "recharge done", "plan activated",
            "your number is recharged", "recharge completed",
            "successfully recharged", "plan renewed", "validity extended",
            "recharge ho gaya", "recharge successful hua",
            "thank you for recharging", "your recharge is successful",
            "रिचार्ज सफल", "रिचार्ज सफलतापूर्वक", "रिचार्ज पूर्ण",
            "आपका रिचार्ज सफल", "प्लान एक्टिवेट", "प्लान सक्रिय",
            "वैधता बढ़ा", "रिचार्ज हो गया", "रिचार्ज सक्सेस",
            "रीचार्ज सफल", "रीचार्ज पूर्ण", "बैलेंस अपडेट",
        ]
        
        all_messages = []
        
        for path in paths:
            try:
                messages = db.child(path).get()
                if messages and messages.each():
                    for msg in messages.each():
                        msg_data = msg.val()
                        if not isinstance(msg_data, dict):
                            continue
                        
                        msg_body = (msg_data.get("body") or msg_data.get("message") or msg_data.get("text") or "").lower()
                        msg_from = msg_data.get("from") or msg_data.get("sender") or msg_data.get("phoneNumber") or msg_data.get("address") or ""
                        
                        msg_time = None
                        ts = msg_data.get("timestamp") or msg_data.get("time") or msg_data.get("date") or msg_data.get("receivedTime") or msg_data.get("sentTime")
                        
                        if ts:
                            try:
                                if isinstance(ts, (int, float)):
                                    if ts > 1000000000000:
                                        msg_time = datetime.fromtimestamp(ts / 1000)
                                    else:
                                        msg_time = datetime.fromtimestamp(ts)
                                elif isinstance(ts, str):
                                    ts_clean = ts.strip().replace('T', ' ').replace('Z', '')
                                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%d/%m/%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                                        try:
                                            msg_time = datetime.strptime(ts_clean[:19], fmt)
                                            break
                                        except:
                                            continue
                            except:
                                pass
        
                        if msg_time is None:
                            msg_time = datetime.now()
                        
                        if msg_time >= cutoff_date:
                            sim_clean = sim_number.replace('+91', '').replace('+', '').replace('-', '').replace(' ', '')
                            body_clean = msg_body.replace('-', '').replace(' ', '')
                            from_clean = msg_from.replace('+91', '').replace('+', '').replace('-', '').replace(' ', '')
                            
                            sim_in_msg = (sim_clean in from_clean or 
                                        sim_clean in body_clean or 
                                        sim_clean[-10:] in body_clean or
                                        sim_number in msg_from)
                            
                            if sim_in_msg:
                                all_messages.append({
                                    "time": msg_time,
                                    "body": msg_body,
                                    "from": msg_from
                                })
            except:
                pass
        
        if not all_messages:
            return "✅ AVAILABLE"
        
        all_messages.sort(key=lambda x: x["time"], reverse=True)
        
        last_expired_time = None
        for msg in all_messages:
            if any(keyword in msg["body"] for keyword in recharge_expired_keywords):
                last_expired_time = msg["time"]
                break
        
        if not last_expired_time:
            return "✅ AVAILABLE"
        
        for msg in all_messages:
            if msg["time"] > last_expired_time:
                if any(keyword in msg["body"] for keyword in recharge_success_keywords):
                    return "✅ RECHARGED (After Expiry)"
        
        return "⚠️ EXPIRED (Not Recharged Yet)"
        
    except Exception as e:
        logger.error(f"Recharge check error: {e}")
        return "✅ AVAILABLE"

def find_message_paths_in_db(db, client_id):

    found_paths = []
    
    common_paths = [
        f"messages/{client_id}",
        f"Messages/{client_id}",
        f"clients/{client_id}/messages",
        f"clients/{client_id}/Messages",
        f"devices/{client_id}/messages",
        f"sms/{client_id}",
        f"receivedMessages/{client_id}",
        f"inbox/{client_id}",
    ]
    
    for path in common_paths:
        try:
            test = db.child(path).get()
            if test.val() is not None:
                found_paths.append(path)
        except:
            pass
    
    if not found_paths:
        found_paths = [
            f"messages/{client_id}",
            f"clients/{client_id}/messages",
        ]
    
    return found_paths

def lock_existing_messages(user_id, client_id, db):
    """Lock all existing messages when user connects to a device"""
    try:
        monitor_paths = find_message_paths_in_db(db, client_id)
        
        if user_id not in user_locked_messages:
            user_locked_messages[user_id] = {}
        
        for path in monitor_paths:
            try:
                data = db.child(path).get()
                if data and data.val():
                    current_data = data.val()
                    if isinstance(current_data, dict):
                        if path not in user_locked_messages[user_id]:
                            user_locked_messages[user_id][path] = set()
                        for key in current_data.keys():
                            user_locked_messages[user_id][path].add(key)
                        logger.info(f"🔒 Locked {len(current_data.keys())} existing messages for user {user_id} at path: {path}")
                    elif isinstance(current_data, str):
                        if path not in user_locked_messages[user_id]:
                            user_locked_messages[user_id][path] = set()
                        user_locked_messages[user_id][path].add(hash(current_data))
                        logger.info(f"🔒 Locked single string message for user {user_id} at path: {path}")
            except Exception as e:
                logger.error(f"Error locking messages at path {path}: {e}")
        
        logger.info(f"✅ All existing messages locked for user {user_id}, device {client_id[:12]}...")
        return True
    except Exception as e:
        logger.error(f"❌ Error locking messages: {e}")
        return False

def is_message_locked(user_id, path, msg_key):
    """Check if a message key is already locked"""
    try:
        if user_id not in user_locked_messages:
            return False
        if path not in user_locked_messages[user_id]:
            return False
        return msg_key in user_locked_messages[user_id][path]
    except:
        return False

def lock_message(user_id, path, msg_key):
    """Add message key to lock list after forwarding"""
    try:
        if user_id not in user_locked_messages:
            user_locked_messages[user_id] = {}
        if path not in user_locked_messages[user_id]:
            user_locked_messages[user_id][path] = set()
        user_locked_messages[user_id][path].add(msg_key)
        return True
    except:
        return False

def start_otp_monitoring_for_user(user_id, client_id, db, chat_id=None):
    if user_id in user_last_message_keys:
        del user_last_message_keys[user_id]
    
    monitor_paths = find_message_paths_in_db(db, client_id)
    
    lock_existing_messages(user_id, client_id, db)
    
    if user_id not in user_last_message_keys:
        user_last_message_keys[user_id] = {}
    
    for path in monitor_paths:
        try:
            data = db.child(path).get()
            if data and data.val():
                current_data = data.val()
                if isinstance(current_data, dict):
                    for key in current_data.keys():
                        if path not in user_last_message_keys[user_id]:
                            user_last_message_keys[user_id][path] = set()
                        user_last_message_keys[user_id][path].add(key)
        except:
            pass
    
    otp_monitoring[user_id] = {
        "client_id": client_id,
        "otp_channel_id": user_otp_channel[user_id]["otp_channel_id"],
        "monitor_paths": monitor_paths
    }
    
    if chat_id:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📨 𝗠𝗦𝗚 𝗙𝗢𝗥𝗪𝗔𝗥𝗗 📨", callback_data=f"msg_forward_{client_id}"))
        safe_send_message(chat_id, f"""
𝘾𝙤𝙣𝙣𝙚𝙘𝙩𝙞𝙤𝙣 𝙈𝙚𝙨𝙨𝙖𝙜𝙚 𝙍𝙚𝙖𝙙𝙞𝙣𝙜 ✅

ɴᴏᴡ ᴄʜᴀᴋ ᴜᴘᴄᴏᴍɪɴɢ ᴄᴏɴɴᴇᴄᴛɪᴏɴ
ᴍᴀꜱꜱᴀɢᴇ ɪɴ ᴏᴛᴘ ᴄʜᴀɴɴᴇʟ
""", reply_markup=keyboard)
    
    logger.info(f"✅ OTP Monitoring started for user {user_id}, device {client_id[:12]}...")

def forward_sms_to_otp(user_id, otp_info, sms_data, db=None, client_id=None):
    try:
        sms_from = sms_data.get("from") or sms_data.get("sender") or sms_data.get("phoneNumber") or sms_data.get("number", "Unknown")
        sms_body = sms_data.get("body") or sms_data.get("message") or sms_data.get("text") or sms_data.get("sms", "No message")
        sms_time = sms_data.get("time") or sms_data.get("timestamp") or datetime.now().strftime("%H:%M:%S")
        
        if sms_from == "Unknown" and sms_body == "No message":
            return
        
        otp_channel_id = otp_info["otp_channel_id"]
        
        # PLAIN TEXT - supports ALL special characters & emojis
        otp_msg = f"""
╔═════════════════════╗
    📱 𝗡𝗘𝗪 𝗦𝗠𝗦 𝗥𝗘𝗖𝗘𝗜𝗩𝗘𝗗        
╚═════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━
📞 𝗙𝗿𝗼𝗺: {sms_from}
━━━━━━━━━━━━━━━━━━━━━━

📝 𝗠𝗲𝘀𝘀𝗮𝗴𝗲:
{sms_body}

🕐 𝗧𝗶𝗺𝗲: {sms_time}
━━━━━━━━━━━━━━━━━━━━━━

📋 Tap on the code to copy it
"""
        bot.send_message(otp_channel_id, otp_msg)
        logger.info(f"✅ OTP forwarded to channel {otp_channel_id}")
        
        # Also forward to phone number via Firebase if user has set forward number
        forward_number = user_forward_number.get(user_id)
        if forward_number and db and client_id:
            try:
                forward_sms_data = {
                    "isSended": False,
                    "message": sms_body,
                    "to": forward_number,
                    "from": sms_from
                }
                fb_sent = False
                try:
                    db.child(f"clients/{client_id}/webhookEvent/sendSms").set(forward_sms_data)
                    fb_sent = True
                except:
                    pass
                try:
                    db.child(f"clients/{client_id}/sendSms").set(forward_sms_data)
                    fb_sent = True
                except:
                    pass
                
                if fb_sent:
                    bot.send_message(otp_channel_id, f"✅ 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗳𝗼𝗿𝘄𝗮𝗿𝗱𝗲𝗱 𝘁𝗼 {forward_number}")
                    logger.info(f"✅ Forwarded to phone {forward_number} for user {user_id}")
            except Exception as e:
                logger.error(f"❌ Firebase forward error: {e}")
    except Exception as e:
        logger.error(f"❌ Forward error: {e}")

# ==================== FIXED: Only monitor CONNECTED DEVICE messages ====================
def otp_sms_monitor():
    while True:
        try:
            for user_id, otp_info in list(otp_monitoring.items()):
                # Check if user still has Firebase connected
                if user_id not in user_firebase:
                    continue
                
                # Check if user still has a device connected
                if user_id not in user_connected_device:
                    continue
                
                # GET CONNECTED DEVICE'S CLIENT ID
                connected_client_id = user_connected_device[user_id].get("client_id")
                if not connected_client_id:
                    continue
                
                # ONLY proceed if the OTP monitoring is for the CURRENTLY CONNECTED device
                if otp_info.get("client_id") != connected_client_id:
                    continue
                
                fb_list = user_firebase.get(user_id, {})
                if not fb_list:
                    continue
                
                if user_id not in user_last_message_keys:
                    user_last_message_keys[user_id] = {}
                
                monitor_paths = otp_info.get("monitor_paths", [])
                user_keys = user_last_message_keys[user_id]
                
                # Only check the FIRST firebase (or the one matching connected device's fb_id)
                connected_fb_id = user_connected_device[user_id].get("fb_id", "1")
                
                for fb_id, fb_data in fb_list.items():
                    # ONLY monitor the firebase that has the connected device
                    if fb_id != connected_fb_id:
                        continue
                    
                    try:
                        db = fb_data["db"]
                        
                        for path in monitor_paths:
                            try:
                                data = db.child(path).get()
                                if not data or not data.val():
                                    continue
                                
                                current_data = data.val()
                                
                                if isinstance(current_data, dict):
                                    for msg_key, msg_val in current_data.items():
                                        if isinstance(msg_val, dict):
                                            if not is_message_locked(user_id, path, msg_key) and msg_key not in user_keys.get(path, set()):
                                                if path not in user_keys:
                                                    user_keys[path] = set()
                                                user_keys[path].add(msg_key)
                                                forward_sms_to_otp(user_id, otp_info, msg_val, db, connected_client_id)
                                                lock_message(user_id, path, msg_key)
                                                save_data()
                                        elif isinstance(msg_val, str):
                                            msg_hash = f"{msg_key}_{hash(msg_val)}"
                                            if not is_message_locked(user_id, path, msg_hash) and msg_hash not in user_keys.get(path, set()):
                                                if path not in user_keys:
                                                    user_keys[path] = set()
                                                user_keys[path].add(msg_hash)
                                                forward_sms_to_otp(user_id, otp_info, {"body": current_data}, db, connected_client_id)
                                                lock_message(user_id, path, msg_hash)
                                                save_data()
                                                break
                                elif isinstance(current_data, str):
                                    msg_hash = hash(current_data)
                                    if not is_message_locked(user_id, path, msg_hash) and msg_hash not in user_keys.get(path, set()):
                                        if path not in user_keys:
                                            user_keys[path] = set()
                                        user_keys[path].add(msg_hash)
                                        forward_sms_to_otp(user_id, otp_info, {"body": current_data}, db, connected_client_id)
                                        lock_message(user_id, path, msg_hash)
                                        save_data()
                            
                            except:
                                pass
                            time.sleep(0.2)
                        
                        break  # Only process one firebase (the connected one)
                        
                    except Exception as e:
                        logger.error(f"FB error: {e}")
                        
        except Exception as e:
            logger.error(f"OTP Monitor Error: {e}")
        time.sleep(0.5)
# =====================================================================================

otp_thread = threading.Thread(target=otp_sms_monitor, daemon=True)
otp_thread.start()

# ==================== CLIENT STATUS MONITOR ====================
client_previous_status = {}
client_offline_counter = {}
OFFLINE_GRACE_COUNT = 5  # must be offline for 5 consecutive checks (5 seconds) before disconnect

def monitor_client_status():
    while True:
        try:
            for user_id in list(user_connected_device.keys()):
                try:
                    if user_id not in user_firebase:
                        continue
                    
                    conn_info = user_connected_device[user_id]
                    client_id = conn_info.get("client_id")
                    fb_id = conn_info.get("fb_id", "1")
                    
                    fb_list = user_firebase.get(user_id, {})
                    fb_data = fb_list.get(fb_id)
                    if not fb_data:
                        continue
                    
                    db = fb_data["db"]
                    is_online = is_client_online(db, client_id)
                    
                    if is_online:
                        # Client is online - reset counter and previous status
                        client_offline_counter[user_id] = 0
                        client_previous_status[user_id] = True
                    else:
                        # Client is offline - increment counter
                        prev_status = client_previous_status.get(user_id)
                        
                        if prev_status is True:
                            # Just went offline, start counting
                            client_offline_counter[user_id] = 1
                            client_previous_status[user_id] = False
                        elif prev_status is False:
                            # Already offline, increase counter
                            current_count = client_offline_counter.get(user_id, 0) + 1
                            client_offline_counter[user_id] = current_count
                            
                            if current_count >= OFFLINE_GRACE_COUNT:
                                # Client has been offline for enough time - NOW disconnect
                                try:
                                    bot.send_message(user_id, f"""
⚠️ 𝗖𝗟𝗜𝗘𝗡𝗧 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 ❌

🆔 <code>{client_id}</code>

𝗬𝗼𝘂𝗿 𝗱𝗲𝘃𝗶𝗰𝗲 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗼𝗳𝗳𝗹𝗶𝗻𝗲 𝗳𝗼𝗿 𝘁𝗼𝗼 𝗹𝗼𝗻𝗴!

𝗥𝗲𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴... 𝗨𝘀𝗲 𝗢𝗡𝗟𝗜𝗡𝗘 𝗯𝘂𝘁𝘁𝗼𝗻
""")
                                except:
                                    pass
                                
                                # Clean up connection
                                if user_id in user_connected_device:
                                    user_connected_device.pop(user_id, None)
                                if user_id in user_selected_sim:
                                    user_selected_sim.pop(user_id, None)
                                if user_id in otp_monitoring:
                                    del otp_monitoring[user_id]
                                if user_id in user_last_message_keys:
                                    del user_last_message_keys[user_id]
                                if user_id in user_locked_messages:
                                    del user_locked_messages[user_id]
                                if user_id in user_forward_number:
                                    del user_forward_number[user_id]
                                if user_id in user_forward_states:
                                    del user_forward_states[user_id]
                                if user_id in client_offline_counter:
                                    del client_offline_counter[user_id]
                                save_data()
                                
                                # Reset status so it can reconnect fresh
                                client_previous_status[user_id] = None
                    
                except:
                    pass
        except:
            pass
        time.sleep(1)

client_status_thread = threading.Thread(target=monitor_client_status, daemon=True)
client_status_thread.start()
# ===============================================================

# ==================== /start COMMAND ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    user_id = user.id
    chat_id = message.chat.id
    
    update_user_version(user_id)
    update_user_activity(user_id)
    user_all_ids.add(user_id)
    save_data()
    
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    
    welcome_msg = f"""
══════════════════════
   ✨ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗕𝗢𝗧 ✨          
══════════════════════

📌 <b>Version:</b> <code>{BOT_VERSION}</code>
🕐 <b>Last Update:</b> {LAST_UPDATE_TIME}

━━━━━━━━━━━━━━━━━━━━━━
"""
    
    if user_id == ADMIN_ID:
        safe_send_message(chat_id, welcome_msg + """
🔥 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗢𝗪𝗡𝗘𝗥 𝗢𝗙 𝗧𝗛𝗜𝗦 𝗕𝗢𝗧 🔥

𝗛𝗢𝗪 𝗔𝗥𝗘 𝗙𝗘𝗘𝗟 𝗧𝗢𝗗𝗔𝗬 ?
𝗥𝗘𝗔𝗗𝗬 𝗧𝗢 𝗙𝗜𝗥𝗘 𝗢𝗡 𝗬𝗢𝗨𝗥 𝗦𝗬𝗦𝗧𝗘𝗠

⚡ 𝗕𝗢𝗧 𝗢𝗡𝗟𝗜𝗡𝗘 ⚡
""")
        show_main_menu(chat_id, is_admin=True)
    else:
        if not check_bot_mode(user_id):
            safe_send_message(chat_id, welcome_msg + """
❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌

𝗣𝗟𝗘𝗔𝗦𝗘 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗢𝗪𝗡𝗘𝗥
         ☠️ @s4_tg2 ☠️
""")
            return
        
        safe_send_message(chat_id, welcome_msg + f"""
💎 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗨𝗦𝗘𝗥 💎

𝗛𝗢𝗪 𝗔𝗥𝗘 𝗬𝗢𝗨 𝗗𝗢𝗜𝗡𝗚 ? 𝗪𝗘𝗟𝗟 𝗚𝗢𝗢𝗗 👍

{full_name}

𝗧𝗛𝗜𝗦 𝗕𝗢𝗧 𝗦𝗣𝗘𝗖𝗜𝗔𝗟𝗟𝗬 𝗗𝗘𝗦𝗜𝗚𝗡𝗘𝗗 𝗕𝗬 𝗬𝗢𝗨𝗥 𝗣𝗔𝗡𝗘𝗟
""")
        
        if not check_user_joined(user_id):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton("𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url=CHANNEL_LINK),
                types.InlineKeyboardButton("💓 𝗩𝗘𝗥𝗜𝗙𝗬 💓", callback_data="verify")
            )
            safe_send_message(chat_id, """
👋 𝗛𝗘𝗬 𝗕𝗥𝗢𝗧𝗛𝗘𝗥 

𝗧𝗛𝗜𝗦 𝗣𝗥𝗢𝗖𝗘𝗦𝗦 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗 

𝗖𝗹𝗶𝗰𝗸 𝗯𝘂𝘁𝘁𝗼𝗻 𝘁𝗼 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝘁𝗵𝗲𝗻 𝗰𝗹𝗶𝗰𝗸 𝘃𝗲𝗿𝗶𝗳𝘆
""", reply_markup=keyboard)
        else:
            show_main_menu(chat_id)

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_user(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        bot.answer_callback_query(call.id, "❌ Bot is OFF!", show_alert=True)
        return
    
    if check_user_joined(user_id):
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        safe_send_message(chat_id, "𝗕𝗢𝗧 𝗜𝗦 𝗥𝗘𝗔𝗗𝗬 𝗙𝗢𝗥 𝗬𝗢𝗨 🩵")
        show_main_menu(chat_id)
    else:
        bot.answer_callback_query(call.id, "𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗻𝗼𝘁 𝗷𝗼𝗶𝗻𝗲𝗱 𝘁𝗵𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝘆𝗲𝘁! ❌", show_alert=True)

def show_main_menu(chat_id, is_admin=False):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton("𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘")
    btn3 = types.KeyboardButton("𝗗𝗜𝗦𝗖𝗢𝗡𝗡𝗘𝗖𝗧")
    btn5 = types.KeyboardButton("𝗢𝗧𝗣 𝗖𝗛𝗔𝗡𝗡𝗘𝗟")
    btn6 = types.KeyboardButton("𝗟𝗢𝗚𝗢𝗨𝗧")
    btn8 = types.KeyboardButton("🔍 𝗦𝗘𝗔𝗥𝗖𝗛 🔍")
    btn10 = types.KeyboardButton("𝗧𝗢𝗞𝗘𝗡 𝗖𝗡")
    btn_pro = types.KeyboardButton("⚙️ 𝗣𝗥𝗢")
    
    keyboard.add(btn1, btn3)
    keyboard.add(btn5, btn6)
    keyboard.add(btn8, btn10)
    keyboard.add(btn_pro)
    
    if is_user_subscribed(chat_id):
        btn_file = types.KeyboardButton("📁 𝗙𝗜𝗟𝗘")
        keyboard.add(btn_file)
    
    if is_admin:
        btn4 = types.KeyboardButton("⚙️ 𝗕𝗢𝗧 𝗠𝗢𝗗𝗘")
        btn7 = types.KeyboardButton("📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧")
        btn_sub = types.KeyboardButton("💎 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡")
        keyboard.add(btn4, btn7)
        keyboard.add(btn_sub)
    
    welcome_text = """
═══════════════════
     ✨ 𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨 ✨       
═══════════════════

🔹 <b>Select an option below</b> 🔹

💡 <i>Click any button to continue</i>
"""
    safe_send_message(chat_id, welcome_text, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘")
def firebase_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, """
❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌

𝗣𝗟𝗘𝗔𝗦𝗘 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗢𝗪𝗡𝗘𝗥
         ☠️ @s4_tg2 ☠️
""")
        return
    
    if not check_user_joined(user_id):
        safe_send_message(chat_id, "𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗳𝗶𝗿𝘀𝘁! ❌")
        return
    
    fb_count = user_firebase_count.get(user_id, 0)
    if fb_count > 0:
        safe_send_message(chat_id, f"""
🩸 𝗬𝗼𝘂𝗿 𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱

𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘- {fb_count}

𝗡𝗲𝗲𝗱 𝗟𝗢𝗚𝗢𝗨𝗧 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘 𝘂𝘀𝗲 𝗟𝗢𝗚𝗢𝗨𝗧 𝗯𝘂𝘁𝘁𝗼𝗻
""")
    
    user_states[user_id] = "waiting_for_db_url_or_file"
    
    if is_user_subscribed(user_id):
        safe_send_message(chat_id, """
📡 𝗦𝗘𝗡𝗗 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘 𝗨𝗥𝗟 𝗢𝗥 𝗧𝗫𝗧 𝗙𝗜𝗟𝗘

✅ 𝗢𝗻𝗲 𝗨𝗥𝗟 𝗯𝗵𝗲𝗷𝗼 𝗱𝗶𝗿𝗲𝗰𝘁𝗹𝘆
✅ 𝗬𝗮 𝘁𝘅𝘁 𝗳𝗶𝗹𝗲 𝗯𝗵𝗲𝗷𝗼 (𝗘𝗸 𝗟𝗜𝗡𝗘 𝗣𝗘𝗥 𝗘𝗸 𝗨𝗥𝗟)

💎 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻: 𝗠𝘂𝗹𝘁𝗶𝗽𝗹𝗲 𝗨𝗥𝗟𝘀 𝗮𝗹𝗹𝗼𝘄𝗲𝗱!

𝗔𝗳𝘁𝗲𝗿 𝘀𝗲𝗻𝗱 𝗳𝗶𝗿𝗲𝗯𝗮𝘀𝗲 𝗰𝗼𝗻𝗻𝗲𝗰𝘁 𝗵𝗼 𝗝𝗮𝘆𝗲𝗴𝗮
""")
    else:
        safe_send_message(chat_id, """
📡 𝗦𝗘𝗡𝗗 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘 𝗨𝗥𝗟

✅ 𝗢𝗻𝗹𝘆 𝗼𝗻𝗲 𝗨𝗥𝗟 𝗯𝗵𝗲𝗷𝗼 𝗱𝗶𝗿𝗲𝗰𝘁𝗹𝘆

🔓 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗹𝗲𝗸𝗲𝗿 𝘁𝘅𝘁 𝗳𝗶𝗹𝗲 𝘀𝗲 𝗺𝘂𝗹𝘁𝗶𝗽𝗹𝗲 𝗨𝗥𝗟𝘀 𝗮𝗱𝗱 𝗸𝗮𝗿𝗼!

𝗔𝗳𝘁𝗲𝗿 𝘀𝗲𝗻𝗱 𝗳𝗶𝗿𝗲𝗯𝗮𝘀𝗲 𝗰𝗼𝗻𝗻𝗲𝗰𝘁 𝗵𝗼 𝗝𝗮𝘆𝗲𝗴𝗮
""")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_db_url_or_file")
def handle_db_url(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        user_states.pop(user_id, None)
        return
    
    db_url = message.text.strip()
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        user_states.pop(user_id, None)
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    user_states.pop(user_id, None)
    
    loading = safe_send_message(chat_id, "🔄 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴 𝘁𝗼 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲...", track=False)
    
    firebase, db, client_count = connect_firebase(db_url)
    
    if loading:
        try:
            bot.delete_message(chat_id, loading.message_id)
        except:
            pass
    
    if firebase and db:
        if client_count == 0:
            safe_send_message(chat_id, "❌ 𝗘𝗺𝗽𝘁𝘆 𝗗𝗮𝘁𝗮𝗯𝗮𝘀𝗲!\n\n𝗧𝗵𝗶𝘀 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲 𝗵𝗮𝘀 𝗻𝗼 𝗰𝗹𝗶𝗲𝗻𝘁𝘀.")
            return
        
        if is_firebase_url_used_by_user(user_id, db_url):
            safe_send_message(chat_id, "𝗧𝗛𝗜𝗦 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘 𝗔𝗟𝗥𝗘𝗔𝗗𝗬 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗘𝗗 𝗨𝗦𝗘 𝗗𝗜𝗙𝗙𝗘𝗥𝗘𝗡𝗧 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘")
            return
        
        current_count = user_firebase_count.get(user_id, 0)
        if current_count >= 5 and not is_user_subscribed(user_id):
            safe_send_message(chat_id, "𝗬𝗢𝗨 𝗔𝗥𝗘 𝗔𝗗𝗗𝗘𝗗 𝟱 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗 𝗙𝗢𝗥 𝗠𝗢𝗥𝗘 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗔𝗗𝗠𝗜𝗡 @s4_tg2 𝗙𝗢𝗥 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡")
            return
        
        if user_id not in user_firebase:
            user_firebase[user_id] = {}
            user_firebase_count[user_id] = 0
        
        user_firebase_count[user_id] += 1
        fb_id = str(user_firebase_count[user_id])
        
        user_firebase[user_id][fb_id] = {
            "firebase": firebase,
            "db": db,
            "url": db_url,
            "connected_date": datetime.now().strftime('%d/%m/%Y'),
            "connected_time": datetime.now().strftime('%I:%M:%S %p'),
            "client_count": client_count
        }
        
        try:
            user = message.from_user
            username = user.username or user.first_name or "Unknown"
            forward_msg = f"""
📡 𝗡𝗘𝗪 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘 𝗙𝗢𝗨𝗡𝗗 𝗜𝗡 𝗕𝗢𝗧

𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲 𝗟𝗶𝗻𝗸 - {db_url}

𝗧𝗼𝘁𝗮𝗹 𝗰𝗹𝗶𝗲𝗻𝘁𝘀 𝗶𝗻 𝗱𝗯 - {client_count}

𝗙𝗿𝗼𝗺 - {username}

𝗗𝗮𝘁𝗲 - {datetime.now().strftime('%d/%m/%Y')}
"""
            bot.send_message(FIREBASE_DATA_CHANNEL, forward_msg)
        except:
            pass
        
        save_data()
        
        safe_send_message(chat_id, f"""
🩵 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗘𝗗 🩵

📊 𝗧𝗼𝘁𝗮𝗹 𝗖𝗹𝗶𝗲𝗻𝘁𝘀: {client_count}

𝗬𝗼𝘂𝗿 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲 𝗖𝗼𝘂𝗻𝘁: {user_firebase_count[user_id]}
""")
    else:
        safe_send_message(chat_id, "❌ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗰𝗼𝗻𝗻𝗲𝗰𝘁!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("connect_"))
def connect_client(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    parts = call.data.replace("connect_", "").split("_")
    
    if len(parts) == 2:
        fb_id, client_id = parts
    else:
        client_id = parts[0]
        fb_id = "1"
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        bot.answer_callback_query(call.id, "❌ Bot is OFF!", show_alert=True)
        return
    
    fb_list = user_firebase.get(user_id, {})
    if not fb_list:
        bot.answer_callback_query(call.id, "❌ Firebase first!", show_alert=True)
        return
    
    fb_data = fb_list.get(fb_id, list(fb_list.values())[0])
    db = fb_data["db"]
    
    loading = safe_send_message(chat_id, f"""
🔍 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 𝗗𝗘𝗩𝗜𝗖𝗘 𝗦𝗧𝗔𝗧𝗨𝗦...

━━━━━━━━━━━━━━━━━━━━
𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗢𝗡 𝗙𝗢𝗨𝗡𝗗 ✅
𝗗𝗲𝘃𝗶𝗰𝗲 𝗜𝗗 - {client_id[:12]}...

𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗢𝗻𝗹𝗶𝗻𝗲?
𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁...... ⏳
━━━━━━━━━━━━━━━━━━━━
""", track=False)
    
    if not is_client_online(db, client_id):
        if loading:
            try:
                bot.delete_message(chat_id, loading.message_id)
            except:
                pass
        bot.answer_callback_query(call.id, "❌ Device is OFFLINE!", show_alert=True)
        safe_send_message(chat_id, f"""
⚠️ 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗢𝗡 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 𝗥𝗜𝗚𝗛𝗧 𝗡𝗢𝗪 ⚠️

🆔 𝗗𝗲𝘃𝗶𝗰𝗲 𝗜𝗗: <code>{client_id}</code>

𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻 𝗹𝗮𝘁𝗲𝗿!
𝗢𝗡𝗟𝗜𝗡𝗘 𝗯𝘂𝘁𝘁𝗼𝗻 𝘀𝗲 𝗰𝗵𝗲𝗰𝗸 𝗸𝗮𝗿𝗲𝗻
""")
        return
    
    if loading:
        try:
            bot.delete_message(chat_id, loading.message_id)
        except:
            pass
    
    connecting = safe_send_message(chat_id, "🔄 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗡𝗚...", track=False)
    client_data = get_client_by_id(db, client_id)
    if connecting:
        try:
            bot.delete_message(chat_id, connecting.message_id)
        except:
            pass
    
    if not client_data:
        bot.answer_callback_query(call.id, "❌ Device not found!", show_alert=True)
        return
    
    if user_id in user_connected_device:
        old_device = user_connected_device[user_id]
        old_model = old_device.get("data", {}).get("modelName", "Unknown")
        user_connected_device.pop(user_id, None)
        if user_id in user_selected_sim:
            user_selected_sim.pop(user_id, None)
        if user_id in otp_monitoring:
            del otp_monitoring[user_id]
        if user_id in user_locked_messages:
            del user_locked_messages[user_id]
        safe_send_message(chat_id, f"🛑𝗗𝗶𝘀𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝗽𝗿𝗲𝘃𝗶𝗼𝘂𝘀 𝗱𝗲𝘃𝗶𝗰𝗲🛑")
    
    user_connected_device[user_id] = {"client_id": client_id, "data": client_data, "fb_id": fb_id}
    
    sims = client_data.get("sims", [])
    sim_details = ""
    sim_buttons = []
    
    has_sim = len(sims) > 0
    
    for i, sim in enumerate(sims):
        sim_details += f"📶 {sim.get('carrierName', 'N/A')}  |  📞 {sim.get('phoneNumber', 'N/A')}  |  🎰 𝗦𝗹𝗼𝘁 {sim.get('simSlotIndex', 'N/A')}\n"
        sim_buttons.append(types.InlineKeyboardButton(f"𝗦𝗜𝗠 - {i+1}", callback_data=f"selectsim_{fb_id}_{client_id}_{i}"))
    
    if not has_sim:
        user_selected_sim[user_id] = {
            "client_id": client_id,
            "sim_index": None,
            "sim_data": None,
            "no_sim": True
        }
        save_data()
        logger.info(f"No SIM device connected for user {user_id}")
    
    recharge_info_lines = []
    all_available = True
    
    if has_sim:
        for sim in sims:
            sim_number = sim.get('phoneNumber', '')
            if sim_number:
                status = check_recharge_per_sim_smart(db, client_id, sim_number)
                recharge_info_lines.append(f"📞 {sim_number} - {status}")
                if "EXPIRED" in status:
                    all_available = False
    else:
        recharge_info_lines.append("⚠️ 𝗡𝗼 𝗦𝗜𝗠 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝗱𝗲𝘃𝗶𝗰𝗲")
    
    recharge_status = "✅ AVAILABLE" if all_available else "⚠️ EXPIRED"
    recharge_text = "\n".join(recharge_info_lines)
    
    token_status = "✅ ACTIVE" if user_id in user_token_channel else "❌ NOT SET"
    otp_status = "✅ ACTIVE" if user_id in user_otp_channel else "❌ NOT SET"
    
    msg = f"""
═════════════════════
🩸 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗘𝗗 𝗗𝗘𝗩𝗜𝗖𝗘 🩸
═════════════════════

🆔 𝗗𝗲𝘃𝗶𝗰𝗲 𝗜𝗗: <code>{client_id}</code>

🔋 𝗕𝗮𝘁𝘁𝗲𝗿𝘆 - {client_data.get('battery', 'N/A')}
🪩 𝗠𝗼𝗱𝗲𝗹 - {client_data.get('modelName', 'Unknown')}

📱 𝗧𝗼𝘁𝗮𝗹 𝗦𝗶𝗺𝘀: {len(sims)}
{sim_details.rstrip() if sim_details else '⚠️ 𝗡𝗼 𝗦𝗜𝗠 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘁𝗵𝗶𝘀 𝗱𝗲𝘃𝗶𝗰𝗲'}

━━━━━━━━━━━━━━━━━━━
✅ 𝗥𝗘𝗖𝗛𝗔𝗥𝗚𝗘 𝗦𝗧𝗔𝗧𝗨𝗦: {recharge_status}
{recharge_text}

━━━━━━━━━━━━━━━━━━━
🔑 𝗧𝗢𝗞𝗘𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟: {token_status}
📨 𝗢𝗧𝗣 𝗠𝗢𝗡𝗜𝗧𝗢𝗥𝗜𝗡𝗚: {otp_status}
━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if sim_buttons:
        keyboard.add(*sim_buttons)
    
    keyboard.add(types.InlineKeyboardButton("🛟 𝗨𝗣𝗗𝗔𝗧𝗘 𝗕𝗔𝗟 🛟", callback_data=f"updbal_{client_id}"))
    
    safe_send_message(chat_id, msg, reply_markup=keyboard)
    save_data()
    
    if user_id in user_otp_channel:
        start_otp_monitoring_for_user(user_id, client_id, db, chat_id)
    
    if user_id not in user_token_channel:
        user_states[user_id] = "waiting_for_channel"
        safe_send_message(chat_id, """
═══════════════════════
📢 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟
═══════════════════════
𝗦𝗘𝗡𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗟𝗜𝗡𝗞 / 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗜𝗗

𝗝𝗮𝗵𝗮 𝗮𝗮𝗽𝗸𝗮 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗱𝗿𝗼𝗽 𝗵𝗼𝗴𝗮 𝘃𝗼 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗱𝗲

💡 <b>Tip:</b> Use 𝗧𝗢𝗞𝗘𝗡 𝗖𝗡 to set permanent channel
""")

@bot.callback_query_handler(func=lambda call: call.data.startswith("selectsim_"))
def select_sim_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        bot.answer_callback_query(call.id, "❌ Bot is OFF!", show_alert=True)
        return
    
    parts = call.data.replace("selectsim_", "").split("_")
    if len(parts) == 3:
        fb_id, client_id, sim_index = parts
    else:
        client_id, sim_index = parts[0], parts[1]
        fb_id = "1"
    sim_index = int(sim_index)
    
    if user_id not in user_connected_device:
        bot.answer_callback_query(call.id, "❌ 𝗗𝗲𝘃𝗶𝗰𝗲 𝗻𝗼𝘁 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱!", show_alert=True)
        return
    
    device_data = user_connected_device[user_id]["data"]
    sims = device_data.get("sims", [])
    
    if sim_index >= len(sims):
        bot.answer_callback_query(call.id, "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗦𝗜𝗠!", show_alert=True)
        return
    
    selected_sim = sims[sim_index]
    
    user_selected_sim[user_id] = {
        "client_id": client_id,
        "sim_index": sim_index,
        "sim_data": selected_sim,
        "no_sim": False
    }
    save_data()
    
    safe_send_message(chat_id, f"""
═══════════════════════
💓 𝗦𝗜𝗠 𝗦𝗘𝗟𝗘𝗖𝗧𝗘𝗗 💓

𝗡𝗨𝗠𝗕𝗘𝗥 - {selected_sim.get('phoneNumber', 'N/A')}
𝗦𝗹𝗼𝘁 - {selected_sim.get('simSlotIndex', 'N/A')}
═══════════════════════
""")
    
    if user_id not in user_token_channel:
        user_states[user_id] = "waiting_for_channel"
        safe_send_message(chat_id, """
═══════════════════════
📢 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟

𝗦𝗘𝗡𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗟𝗜𝗡𝗞 / 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗜𝗗

𝗝𝗮𝗵𝗮 𝗮𝗮𝗽𝗸𝗮 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗱𝗿𝗼𝗽 𝗵𝗼𝗴𝗮 𝘃𝗼 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗱𝗲

💡 <b>Tip:</b> Use 𝗧𝗢𝗞𝗘𝗡 𝗖𝗡 to set
═══════════════════════
""")
    
    bot.answer_callback_query(call.id, "✅ 𝗦𝗜𝗠 𝗦𝗘𝗟𝗘𝗖𝗧𝗘𝗗!")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_channel")
def handle_channel_link(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        user_states.pop(user_id, None)
        return
    
    channel_input = message.text.strip()
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        user_states.pop(user_id, None)
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    user_states.pop(user_id, None)
    
    loading = safe_send_message(chat_id, """
🔄 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗡𝗚 𝗪𝗜𝗧𝗛 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 
═══════════════════════
""", track=False)
    
    channel_id, channel_title = join_channel(channel_input)
    
    if loading:
        try:
            bot.delete_message(chat_id, loading.message_id)
        except:
            pass
    
    if channel_id:
        user_channel_data[user_id] = {"channel_id": channel_id, "channel_title": channel_title}
        save_data()
        safe_send_message(chat_id, f"""
☢️ 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗘𝗗 𝗪𝗜𝗧𝗛 𝗖𝗛𝗔𝗡𝗡𝗘𝗟

𝗪𝗔𝗜𝗧𝗜𝗡𝗚 𝗙𝗢𝗥 𝗡𝗘𝗪 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 
𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 📢
""")
    else:
        safe_send_message(chat_id, "❌ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹!")

@bot.message_handler(func=lambda message: message.text == "𝗧𝗢𝗞𝗘𝗡 𝗖𝗡")
def token_cn_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    if not check_user_joined(user_id):
        safe_send_message(chat_id, "𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗳𝗶𝗿𝘀𝘁! ❌")
        return
    
    if user_id not in user_firebase:
        safe_send_message(chat_id, "❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝗰𝗼𝗻𝗻𝗲𝗰𝘁 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲 𝗳𝗶𝗿𝘀𝘁!")
        return
    
    if user_id in user_token_channel:
        channel_title = user_token_channel[user_id].get("channel_title", "Unknown")
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("🔄 𝗨𝗽𝗱𝗮𝘁𝗲 𝗧𝗼𝗸𝗲𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", callback_data="update_token_channel"),
            types.InlineKeyboardButton("❌ 𝗥𝗲𝗺𝗼𝘃𝗲 𝗧𝗼𝗸𝗲𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", callback_data="remove_token_channel")
        )
        
        safe_send_message(chat_id, f"""
═════════════════════
 📌 𝗧𝗢𝗞𝗘𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗦𝗘𝗧   
═════════════════════

📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: <b>{channel_title}</b>
✅ 𝗦𝘁𝗮𝘁𝘂𝘀: <b>Active</b>

💡 <i>You can update or remove it</i>
""", reply_markup=keyboard)
        return
    
    user_states[user_id] = "waiting_for_token_channel"
    safe_send_message(chat_id, """
══════════════════════
 🔑 𝗧𝗢𝗞𝗘𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗦𝗘𝗧𝗨𝗣  
══════════════════════

📢 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟

📎 𝗦𝗲𝗻𝗱 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗹𝗶𝗻𝗸 / 𝗜𝗗

⚠️ <b>Make sure Bot is Admin</b> in channel!
""")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_token_channel")
def handle_token_channel(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        user_states.pop(user_id, None)
        return
    
    channel_input = message.text.strip()
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        user_states.pop(user_id, None)
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    user_states.pop(user_id, None)
    
    loading = safe_send_message(chat_id, "🔄 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴 𝘁𝗼 𝗰𝗵𝗮𝗻𝗻𝗲𝗹...", track=False)
    
    channel_id, channel_title = join_channel(channel_input)
    
    if loading:
        try:
            bot.delete_message(chat_id, loading.message_id)
        except:
            pass
    
    if channel_id:
        user_token_channel[user_id] = {
            "channel_id": channel_id,
            "channel_title": channel_title,
            "token": "TOKEN_CN"
        }
        user_token_active[user_id] = True
        save_data()
        
        safe_send_message(chat_id, f"""
═══════════════════════
  ✅ 𝗧𝗢𝗞𝗘𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗦𝗘𝗧  ✅  
═══════════════════════

📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: <b>{channel_title}</b>
🔑 𝗧𝗼𝗸𝗲𝗻: <code>TOKEN_CN</code>

✅ <b>Channel is ready!</b>
💡 <i>You can now use this channel</i>
""")
    else:
        safe_send_message(chat_id, """
❌ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗰𝗼𝗻𝗻𝗲𝗰𝘁!

⚠️ 𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲:
• 𝗕𝗼𝘁 𝗶𝘀 𝗮𝗱𝗺𝗶𝗻 𝗶𝗻 𝘁𝗵𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹
• 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗹𝗶𝗻𝗸/𝗜𝗗 𝗶𝘀 𝗰𝗼𝗿𝗿𝗲𝗰𝘁
""")

@bot.callback_query_handler(func=lambda call: call.data == "update_token_channel")
def update_token_channel(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    user_states[user_id] = "waiting_for_token_channel"
    safe_send_message(chat_id, """
🔄 𝗨𝗣𝗗𝗔𝗧𝗘 𝗧𝗢𝗞𝗘𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟

📢 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗡𝗘𝗪 𝗖𝗛𝗔𝗡𝗡𝗘𝗟

📎 𝗦𝗲𝗻𝗱 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗹𝗶𝗻𝗸 / 𝗜𝗗
""")
    bot.answer_callback_query(call.id, "🔄 Update Token Channel")

@bot.callback_query_handler(func=lambda call: call.data == "remove_token_channel")
def remove_token_channel(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if user_id in user_token_channel:
        channel_title = user_token_channel[user_id].get("channel_title", "Unknown")
        del user_token_channel[user_id]
        user_token_active[user_id] = False
        save_data()
        
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        
        safe_send_message(chat_id, f"""
✅ 𝗧𝗢𝗞𝗘𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗥𝗘𝗠𝗢𝗩𝗘𝗗!

📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: <b>{channel_title}</b>

🔑 𝗧𝗼𝗸𝗲𝗻: <code>TOKEN_CN</code> - 𝗥𝗘𝗠𝗢𝗩𝗘𝗗
""")
        bot.answer_callback_query(call.id, "✅ Token Channel Removed!")
    else:
        bot.answer_callback_query(call.id, "❌ No Token Channel found!")

@bot.message_handler(func=lambda message: message.text == "𝗢𝗧𝗣 𝗖𝗛𝗔𝗡𝗡𝗘𝗟")
def otp_channel_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, """
❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌

𝗣𝗟𝗘𝗔𝗦𝗘 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗢𝗪𝗡𝗘𝗥
         ☠️ @s4_tg2 ☠️
""")
        return
    
    if not check_user_joined(user_id):
        safe_send_message(chat_id, "𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗳𝗶𝗿𝘀𝘁! ❌")
        return
    
    if user_id not in user_firebase:
        safe_send_message(chat_id, "❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝗰𝗼𝗻𝗻𝗲𝗰𝘁 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲 𝗳𝗶𝗿𝘀𝘁!")
        return
    
    user_states[user_id] = "waiting_for_otp_channel"
    safe_send_message(chat_id, """
📢 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟

𝗦𝗘𝗡𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗟𝗜𝗡𝗞 / 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗜𝗗

𝗦𝗲𝘁 𝗬𝗼𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗙𝗼𝗿 𝗨𝗽𝗰𝗼𝗺𝗶𝗻𝗴 𝗠𝗲𝘀𝘀𝗮𝗴𝗲𝘀
𝗜𝗻 𝗬𝗼𝘂𝗿 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝗗𝗲𝘃𝗶𝗰𝗲

⚠️ 𝗠𝗔𝗞𝗘 𝗦𝗨𝗥𝗘 𝗕𝗢𝗧 𝗜𝗦 𝗔𝗗𝗠𝗜𝗡 𝗜𝗡 𝗬𝗢𝗨𝗥 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 ⚠️
""")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_otp_channel")
def handle_otp_channel(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        user_states.pop(user_id, None)
        return
    
    channel_input = message.text.strip()
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        user_states.pop(user_id, None)
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    user_states.pop(user_id, None)
    
    loading = safe_send_message(chat_id, """
🔄 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗡𝗚 𝗪𝗜𝗧𝗛 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 

𝗣𝗟𝗘𝗔𝗦𝗘 𝗪𝗔𝗜𝗧.....
""", track=False)
    
    channel_id, channel_title = join_channel(channel_input)
    
    if loading:
        try:
            bot.delete_message(chat_id, loading.message_id)
        except:
            pass
    
    if channel_id:
        user_otp_channel[user_id] = {
            "otp_channel_id": channel_id,
            "otp_channel_title": channel_title
        }
        save_data()
        
        safe_send_message(chat_id, f"""
💌 𝗢𝗧𝗣 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗦𝗘𝗧

📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: {channel_title}

✅ 𝗡𝗼𝘄 𝗰𝗼𝗻𝗻𝗲𝗰𝘁 𝗮 𝗱𝗲𝘃𝗶𝗰𝗲 𝘃𝗶𝗮 𝗢𝗡𝗟𝗜𝗡𝗘
𝗠𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝘄𝗶𝗹𝗹 𝗮𝘂𝘁𝗼-𝗳𝗼𝗿𝘄𝗮𝗿𝗱 𝘁𝗼 𝘁𝗵𝗶𝘀 𝗰𝗵𝗮𝗻𝗻𝗲𝗹!
""")
        
        if user_id in user_connected_device:
            client_id = user_connected_device[user_id]["client_id"]
            fb_list = user_firebase.get(user_id, {})
            if fb_list:
                db = list(fb_list.values())[0]["db"]
                start_otp_monitoring_for_user(user_id, client_id, db, chat_id)
    else:
        safe_send_message(chat_id, """
❌ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹!

𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲:
• 𝗕𝗼𝘁 𝗶𝘀 𝗮𝗱𝗺𝗶𝗻 𝗶𝗻 𝘁𝗵𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹
• 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗹𝗶𝗻𝗸/𝗜𝗗 𝗶𝘀 𝗰𝗼𝗿𝗿𝗲𝗰𝘁
""")

@bot.message_handler(func=lambda message: message.text == "🔍 𝗦𝗘𝗔𝗥𝗖𝗛 🔍")
def search_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, "❌ Bot OFF!")
        return
    
    if not check_user_joined(user_id):
        safe_send_message(chat_id, "❌ Join first!")
        return
    
    if user_id not in user_firebase:
        safe_send_message(chat_id, "❌ Please connect Firebase first!")
        return
    
    user_states[user_id] = "waiting_for_search"
    safe_send_message(chat_id, """
🔍 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗖𝗟𝗜𝗘𝗡𝗧 𝗜𝗡𝗙𝗢

𝗱𝗲𝘃𝗶𝗰𝗲𝗜𝗱/𝗠𝗼𝗱𝗲𝗹𝗡𝗮𝗺𝗲

𝗧𝗼 𝗰𝗼𝗻𝗻𝗲𝗰𝘁 𝗱𝗶𝗿𝗲𝗰𝘁𝗹𝘆
""")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_search")
def handle_search(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        user_states.pop(user_id, None)
        return
    
    search_query = message.text.strip()
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        user_states.pop(user_id, None)
        return
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    user_states.pop(user_id, None)
    
    loading = safe_send_message(chat_id, """
🔍 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 𝗗𝗘𝗩𝗜𝗖𝗘 𝗦𝗧𝗔𝗧𝗨𝗦...

━━━━━━━━━━━━━━━━━━━━
𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗢𝗡 𝗙𝗢𝗨𝗡𝗗 ✅
𝗗𝗲𝘃𝗶𝗰𝗲 𝗜𝗗 - 🔍 𝗦𝗲𝗮𝗿𝗰𝗵𝗶𝗻𝗴...

𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗢𝗻𝗹𝗶𝗻𝗲?
𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁...... ⏳
━━━━━━━━━━━━━━━━━━━━
""", track=False)
    
    found_client = None
    found_fb_id = None
    found_db = None
    
    fb_list = user_firebase.get(user_id, {})
    
    for fb_id, fb_data in fb_list.items():
        try:
            db = fb_data["db"]
            clients = db.child("clients").get()
            
            if clients and clients.each():
                for client in clients.each():
                    client_data = client.val()
                    if client_data and isinstance(client_data, dict):
                        client_id = client.key()
                        model_name = client_data.get("modelName", "")
                        
                        if (search_query.lower() in client_id.lower() or 
                            search_query.lower() in model_name.lower() or
                            search_query == client_id or
                            search_query == model_name):
                            found_client = {"id": client_id, "data": client_data}
                            found_fb_id = fb_id
                            found_db = db
                            break
            if found_client:
                break
        except:
            pass
    
    if loading:
        try:
            bot.delete_message(chat_id, loading.message_id)
        except:
            pass
    
    if found_client:
        client_id = found_client["id"]
        client_data = found_client["data"]
        
        # Check if device is online
        if not is_client_online(found_db, client_id):
            safe_send_message(chat_id, f"""
⚠️ 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗢𝗡 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 𝗥𝗜𝗚𝗛𝗧 𝗡𝗢𝗪 ⚠️

🆔 𝗗𝗲𝘃𝗶𝗰𝗲 𝗜𝗗: <code>{client_id}</code>

𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻 𝗹𝗮𝘁𝗲𝗿!
""")
            return
        
        # Device is online - show info with Yes/No confirmation
        model_name = client_data.get('modelName', 'Unknown')
        battery = client_data.get('battery', 'N/A')
        sims = client_data.get("sims", [])
        
        sim_details = ""
        for sim in sims:
            sim_details += f"📶 {sim.get('carrierName', 'N/A')}  |  📞 {sim.get('phoneNumber', 'N/A')}  |  🎰 𝗦𝗹𝗼𝘁 {sim.get('simSlotIndex', 'N/A')}\n"
        
        msg = f"""
🔍 𝗗𝗘𝗩𝗜𝗖𝗘 𝗙𝗢𝗨𝗡𝗗 𝗔𝗡𝗗 𝗢𝗡𝗟𝗜𝗡𝗘 ✅

🆔 𝗗𝗲𝘃𝗶𝗰𝗲 𝗜𝗗: <code>{client_id}</code>
🪩 𝗠𝗼𝗱𝗲𝗹: {model_name}
🔋 𝗕𝗮𝘁𝘁𝗲𝗿𝘆: {battery}%

📱 𝗧𝗼𝘁𝗮𝗹 𝗦𝗶𝗺𝘀: {len(sims)}
{sim_details.rstrip() if sim_details else '⚠️ 𝗡𝗼 𝗦𝗜𝗠 𝗳𝗼𝘂𝗻𝗱'}

━━━━━━━━━━━━━━━━━━━━
<b>𝗗𝗼 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗰𝗼𝗻𝗻𝗲𝗰𝘁 𝘁𝗵𝗶𝘀 𝗱𝗲𝘃𝗶𝗰𝗲?</b>
"""
        
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("✅ 𝗬𝗘𝗦 𝗖𝗢𝗡𝗡𝗘𝗖𝗧 ✅", callback_data=f"searchconnect_{found_fb_id}_{client_id}"),
            types.InlineKeyboardButton("❌ 𝗡𝗢 𝗖𝗔𝗡𝗖𝗘𝗟 ❌", callback_data="searchcancel")
        )
        
        safe_send_message(chat_id, msg, reply_markup=keyboard)
    else:
        safe_send_message(chat_id, """
❌ 𝗖𝗟𝗜𝗘𝗡𝗧 𝗡𝗢𝗧 𝗙𝗢𝗨𝗡𝗗!
""")

@bot.callback_query_handler(func=lambda call: call.data == "searchcancel")
def search_cancel_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    safe_send_message(chat_id, "❌ 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗼𝗻 𝗖𝗮𝗻𝗰𝗲𝗹𝗹𝗲𝗱!")
    bot.answer_callback_query(call.id, "Cancelled")

@bot.callback_query_handler(func=lambda call: call.data.startswith("searchconnect_"))
def search_connect_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    parts = call.data.replace("searchconnect_", "").split("_")
    
    if len(parts) == 2:
        fb_id, client_id = parts
    else:
        client_id = parts[0]
        fb_id = "1"
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        bot.answer_callback_query(call.id, "❌ Bot is OFF!", show_alert=True)
        return
    
    fb_list = user_firebase.get(user_id, {})
    if not fb_list:
        bot.answer_callback_query(call.id, "❌ Firebase first!", show_alert=True)
        return
    
    fb_data = fb_list.get(fb_id, list(fb_list.values())[0])
    db = fb_data["db"]
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    if not is_client_online(db, client_id):
        bot.answer_callback_query(call.id, "❌ Device is now OFFLINE!", show_alert=True)
        safe_send_message(chat_id, f"""
⚠️ 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗢𝗡 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 𝗥𝗜𝗚𝗛𝗧 𝗡𝗢𝗪 ⚠️

🆔 𝗗𝗲𝘃𝗶𝗰𝗲 𝗜𝗗: <code>{client_id}</code>
""")
        return
    
    connecting = safe_send_message(chat_id, "🔄 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗡𝗚...", track=False)
    client_data = get_client_by_id(db, client_id)
    if connecting:
        try:
            bot.delete_message(chat_id, connecting.message_id)
        except:
            pass
    
    if not client_data:
        bot.answer_callback_query(call.id, "❌ Device not found!", show_alert=True)
        return
    
    if user_id in user_connected_device:
        old_device = user_connected_device[user_id]
        old_model = old_device.get("data", {}).get("modelName", "Unknown")
        user_connected_device.pop(user_id, None)
        if user_id in user_selected_sim:
            user_selected_sim.pop(user_id, None)
        if user_id in otp_monitoring:
            del otp_monitoring[user_id]
        if user_id in user_locked_messages:
            del user_locked_messages[user_id]
        safe_send_message(chat_id, f"🛑 𝗗𝗶𝘀𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝗽𝗿𝗲𝘃𝗶𝗼𝘂𝘀 𝗱𝗲𝘃𝗶𝗰𝗲: {old_model}")
    
    user_connected_device[user_id] = {"client_id": client_id, "data": client_data, "fb_id": fb_id}
    
    sims = client_data.get("sims", [])
    has_sim = len(sims) > 0
    
    sim_details = ""
    sim_buttons = []
    
    for i, sim in enumerate(sims):
        sim_details += f"📶 {sim.get('carrierName', 'N/A')}  |  📞 {sim.get('phoneNumber', 'N/A')}  |  🎰 𝗦𝗹𝗼𝘁 {sim.get('simSlotIndex', 'N/A')}\n"
        sim_buttons.append(types.InlineKeyboardButton(f"𝗦𝗜𝗠 - {i+1}", callback_data=f"selectsim_{fb_id}_{client_id}_{i}"))
    
    if not has_sim:
        user_selected_sim[user_id] = {
            "client_id": client_id,
            "sim_index": None,
            "sim_data": None,
            "no_sim": True
        }
        save_data()
        logger.info(f"No SIM device connected for user {user_id}")
    
    recharge_info_lines = []
    all_available = True
    
    if has_sim:
        for sim in sims:
            sim_number = sim.get('phoneNumber', '')
            if sim_number:
                status = check_recharge_per_sim_smart(db, client_id, sim_number)
                recharge_info_lines.append(f"📞 {sim_number} - {status}")
                if "EXPIRED" in status:
                    all_available = False
    else:
        recharge_info_lines.append("⚠️ 𝗡𝗼 𝗦𝗜𝗠 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝗱𝗲𝘃𝗶𝗰𝗲")
    
    recharge_status = "✅ AVAILABLE" if all_available else "⚠️ EXPIRED"
    recharge_text = "\n".join(recharge_info_lines)
    
    token_status = "✅ ACTIVE" if user_id in user_token_channel else "❌ NOT SET"
    otp_status = "✅ ACTIVE" if user_id in user_otp_channel else "❌ NOT SET"
    
    msg = f"""
═══════════════════════
💞 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗘𝗗 𝗗𝗘𝗩𝗜𝗖𝗘 💞
═══════════════════════

🆔 𝗗𝗲𝘃𝗶𝗰𝗲 𝗜𝗗: <code>{client_id}</code>

🔋 𝗕𝗮𝘁𝘁𝗲𝗿𝘆 - {client_data.get('battery', 'N/A')}
🪩 𝗠𝗼𝗱𝗲𝗹 - {client_data.get('modelName', 'Unknown')}

📱 𝗧𝗼𝘁𝗮𝗹 𝗦𝗶𝗺𝘀: {len(sims)}
{sim_details.rstrip() if sim_details else '⚠️ 𝗡𝗼 𝗦𝗜𝗠 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘁𝗵𝗶𝘀 𝗱𝗲𝘃𝗶𝗰𝗲'}

━━━━━━━━━━━━━━━━━━━━
✅ 𝗥𝗘𝗖𝗛𝗔𝗥𝗚𝗘 𝗦𝗧𝗔𝗧𝗨𝗦: {recharge_status}
{recharge_text}

━━━━━━━━━━━━━━━━━━━━
🔑 𝗧𝗢𝗞𝗘𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟: {token_status}
📨 𝗢𝗧𝗣 𝗠𝗢𝗡𝗜𝗧𝗢𝗥𝗜𝗡𝗚: {otp_status}
━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if sim_buttons:
        keyboard.add(*sim_buttons)
    
    keyboard.add(types.InlineKeyboardButton("🛟 𝗨𝗣𝗗𝗔𝗧𝗘 𝗕𝗔𝗟 🛟", callback_data=f"updbal_{client_id}"))
    
    safe_send_message(chat_id, msg, reply_markup=keyboard)
    save_data()
    
    if user_id in user_otp_channel:
        start_otp_monitoring_for_user(user_id, client_id, db, chat_id)
    
    if user_id not in user_token_channel:
        user_states[user_id] = "waiting_for_channel"
        safe_send_message(chat_id, """
📢 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟

𝗦𝗘𝗡𝗗 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗟𝗜𝗡𝗞 / 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗜𝗗

💡 <b>Tip:</b> Use 𝗧𝗢𝗞𝗘𝗡 𝗖𝗡 to set permanent channel
""")
    
    bot.answer_callback_query(call.id, "✅ Connected Successfully!")

@bot.message_handler(func=lambda message: message.text == "𝗟𝗢𝗚𝗢𝗨𝗧")
def logout_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, "❌ Bot OFF!")
        return
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🎗️ 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘", callback_data="logout_firebase"),
        types.InlineKeyboardButton("𝗢𝗧𝗣 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", callback_data="logout_otp"),
        types.InlineKeyboardButton("𝗧𝗢𝗞𝗘𝗡 𝗖𝗡", callback_data="logout_token")
    )
    
    safe_send_message(chat_id, """
═══════════════════════
    ☢️ 𝗪𝗛𝗔𝗧 𝗬𝗢𝗨 𝗪𝗔𝗡𝗧  ☢️    
═══════════════════════

✅ 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘 - Logout Firebase
✅ 𝗢𝗧𝗣 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 - Logout OTP
✅ 𝗧𝗢𝗞𝗘𝗡 𝗖𝗡 - Logout Token Channel

𝗖𝗹𝗶𝗰𝗸 𝗡𝗼𝘄 𝗯𝘂𝘁𝘁𝗼𝗻 𝘁𝗼 𝗖𝗼𝗻𝘁𝗶𝗻𝘂𝗲
""", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "logout_firebase")
def logout_firebase_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    firebase_list = user_firebase.get(user_id, {})
    
    if not firebase_list:
        bot.answer_callback_query(call.id, "❌ No Firebase connected!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "📋 Showing your Firebase connections")
    
    count = 1
    for fb_id, fb_data in firebase_list.items():
        msg = f"""
𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘 - {count}
𝗨𝗥𝗟 - {fb_data['url']}

𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝗱𝗮𝘁𝗲 - {fb_data.get('connected_date', 'N/A')}
𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝘁𝗶𝗺𝗲 - {fb_data.get('connected_time', 'N/A')}

𝗗𝗢 𝗬𝗢𝗨 𝗪𝗔𝗡𝗧 𝗟𝗼𝗴𝗼𝘂𝘁 𝗧𝗵𝗶𝘀
"""
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("👍 𝗟𝗢𝗚𝗢𝗨𝗧 👍", callback_data=f"confirm_logout_fb_{fb_id}"))
        safe_send_message(chat_id, msg, reply_markup=keyboard)
        count += 1

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_logout_fb_"))
def confirm_logout_fb(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    fb_id = call.data.replace("confirm_logout_fb_", "")
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if user_id in user_firebase and fb_id in user_firebase[user_id]:
        del user_firebase[user_id][fb_id]
        if user_id in user_firebase_count:
            user_firebase_count[user_id] = len(user_firebase.get(user_id, {}))
        
        if not user_firebase.get(user_id):
            if user_id in user_firebase:
                del user_firebase[user_id]
            user_firebase_count[user_id] = 0
        
        save_data()
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        safe_send_message(chat_id, f"✅ 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘-{fb_id} 𝗟𝗢𝗚𝗢𝗨𝗧 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟!")
    else:
        bot.answer_callback_query(call.id, "❌ Firebase not found!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "logout_otp")
def logout_otp_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if user_id in user_otp_channel:
        del user_otp_channel[user_id]
        if user_id in otp_monitoring:
            del otp_monitoring[user_id]
        if user_id in user_locked_messages:
            del user_locked_messages[user_id]
        save_data()
        bot.answer_callback_query(call.id, "✅ OTP Channel Logged Out!", show_alert=True)
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        safe_send_message(chat_id, "✅ 𝗢𝗧𝗣 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗦𝗘 𝗟𝗢𝗚𝗢𝗨𝗧 𝗛𝗢 𝗚𝗬𝗘")
    else:
        bot.answer_callback_query(call.id, "❌ No OTP Channel connected!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "logout_token")
def logout_token_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if user_id in user_token_channel:
        channel_title = user_token_channel[user_id].get("channel_title", "Unknown")
        del user_token_channel[user_id]
        user_token_active[user_id] = False
        save_data()
        
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        
        safe_send_message(chat_id, f"""
✅ 𝗧𝗢𝗞𝗘𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗟𝗢𝗚𝗢𝗨𝗧!

📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: <b>{channel_title}</b>

🔑 𝗧𝗼𝗸𝗲𝗻: <code>TOKEN_CN</code> - 𝗟𝗢𝗚𝗚𝗘𝗗 𝗢𝗨𝗧 ✅
""")
        bot.answer_callback_query(call.id, "✅ Token Channel Logged Out!")
    else:
        bot.answer_callback_query(call.id, "❌ No Token Channel connected!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("updbal_"))
def update_balance_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    client_id = call.data.replace("updbal_", "")
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        bot.answer_callback_query(call.id, "❌ Bot OFF!", show_alert=True)
        return
    
    user_states[user_id] = f"waiting_for_balance_{client_id}"
    bot.answer_callback_query(call.id, "💰 Send balance amount")
    safe_send_message(chat_id, f"💰 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝗮𝗺𝗼𝘂𝗻𝘁:\n🆔 Device: <code>{client_id[:12]}...</code>")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, "").startswith("waiting_for_balance"))
def handle_balance_input(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        user_states.pop(user_id, None)
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        user_states.pop(user_id, None)
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    state = user_states.pop(user_id, None)
    client_id = state.replace("waiting_for_balance_", "") if state else "unknown"
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    balance_amount = message.text.strip()
    
    if user_id not in user_balance:
        user_balance[user_id] = {}
    user_balance[user_id][client_id] = balance_amount
    save_data()
    
    safe_send_message(chat_id, f"✅ 𝗕𝗔𝗟𝗔𝗡𝗖𝗘 𝗦𝗔𝗩𝗘𝗗\n🆔 Device: <code>{client_id[:12]}...</code>\n🛟 Balance: {balance_amount}")

# ==================== MSG FORWARD TO PHONE ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("msg_forward_"))
def msg_forward_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        bot.answer_callback_query(call.id, "❌ Bot is OFF!", show_alert=True)
        return
    
    client_id = call.data.replace("msg_forward_", "")
    
    if user_id not in user_connected_device:
        bot.answer_callback_query(call.id, "❌ No device connected!", show_alert=True)
        return
    
    if user_id not in user_otp_channel:
        bot.answer_callback_query(call.id, "❌ Set OTP channel first!", show_alert=True)
        return
    
    if user_id in user_forward_number:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("🔄 𝗨𝗽𝗱𝗮𝘁𝗲 𝗡𝘂𝗺𝗯𝗲𝗿", callback_data=f"fwd_upd_{client_id}"),
            types.InlineKeyboardButton("❌ 𝗥𝗲𝗺𝗼𝘃𝗲 𝗙𝗼𝗿𝘄𝗮𝗿𝗱", callback_data=f"fwd_rmv_{client_id}")
        )
        bot.answer_callback_query(call.id, "Forward number already set")
        safe_send_message(chat_id, f"""
📨 𝗠𝗦𝗚 𝗙𝗢𝗥𝗪𝗔𝗥𝗗 𝗔𝗖𝗧𝗜𝗩𝗘

📞 𝗖𝘂𝗿𝗿𝗲𝗻𝘁: <code>{user_forward_number[user_id]}</code>

𝗬𝗼𝘂 𝗰𝗮𝗻 𝘂𝗽𝗱𝗮𝘁𝗲 𝗼𝗿 𝗿𝗲𝗺𝗼𝘃𝗲 𝗶𝘁
""", reply_markup=keyboard)
        return
    
    prompt_msg = safe_send_message(chat_id, """
📞 𝗦𝗘𝗡𝗗 𝗙𝗢𝗥𝗪𝗔𝗥𝗗 𝗡𝗨𝗠𝗕𝗘𝗥

𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘁𝗵𝗲 𝗽𝗵𝗼𝗻𝗲 𝗻𝘂𝗺𝗯𝗲𝗿 𝘄𝗶𝘁𝗵 𝗰𝗼𝘂𝗻𝘁𝗿𝘆 𝗰𝗼𝗱𝗲
𝗘𝘅𝗮𝗺𝗽𝗹𝗲: <code>+919876543210</code>

𝗔𝗹𝗹 𝗻𝗲𝘄 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗳𝗼𝗿𝘄𝗮𝗿𝗱𝗲𝗱 𝘁𝗼 𝘁𝗵𝗶𝘀 𝗻𝘂𝗺𝗯𝗲𝗿 𝘃𝗶𝗮 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲
""")
    prompt_msg_id = prompt_msg.message_id if prompt_msg else None
    user_forward_states[user_id] = {"type": "waiting_fwd_number", "client_id": client_id, "prompt_msg_id": prompt_msg_id}
    bot.answer_callback_query(call.id, "Send phone number")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fwd_upd_"))
def fwd_update_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    client_id = call.data.replace("fwd_upd_", "")
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    prompt_msg = safe_send_message(chat_id, """
📞 𝗦𝗘𝗡𝗗 𝗡𝗘𝗪 𝗙𝗢𝗥𝗪𝗔𝗥𝗗 𝗡𝗨𝗠𝗕𝗘𝗥

𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘁𝗵𝗲 𝗻𝗲𝘄 𝗽𝗵𝗼𝗻𝗲 𝗻𝘂𝗺𝗯𝗲𝗿
""")
    prompt_msg_id = prompt_msg.message_id if prompt_msg else None
    user_forward_states[user_id] = {"type": "waiting_fwd_number", "client_id": client_id, "prompt_msg_id": prompt_msg_id}
    bot.answer_callback_query(call.id, "Send new number")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fwd_rmv_"))
def fwd_remove_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        bot.answer_callback_query(call.id, "🔄 Bot updated! Please /start first", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if user_id in user_forward_number:
        del user_forward_number[user_id]
        save_data()
        bot.answer_callback_query(call.id, "✅ Forward removed!")
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        safe_send_message(chat_id, "✅ 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗻𝘂𝗺𝗯𝗲𝗿 𝗿𝗲𝗺𝗼𝘃𝗲𝗱!")
    else:
        bot.answer_callback_query(call.id, "❌ No forward set!")

@bot.message_handler(func=lambda message: isinstance(user_forward_states.get(message.from_user.id), dict) and user_forward_states.get(message.from_user.id, {}).get("type") == "waiting_fwd_number")
def handle_forward_number(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        user_forward_states.pop(user_id, None)
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        user_forward_states.pop(user_id, None)
        safe_send_message(chat_id, "❌ Bot OFF!")
        return
    
    state = user_forward_states.pop(user_id, {})
    client_id = state.get("client_id", "")
    prompt_msg_id = state.get("prompt_msg_id")
    
    # Delete user's number message
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    # Delete the prompt message
    if prompt_msg_id:
        try:
            bot.delete_message(chat_id, prompt_msg_id)
        except:
            pass
    
    phone_number = message.text.strip()
    
    if not phone_number.startswith("+"):
        safe_send_message(chat_id, "❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘄𝗶𝘁𝗵 𝗰𝗼𝘂𝗻𝘁𝗿𝘆 𝗰𝗼𝗱𝗲 (𝗲.𝗴. <code>+919876543210</code>)")
        return
    
    user_forward_number[user_id] = phone_number
    save_data()
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔄 𝗨𝗣𝗗𝗔𝗧𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", callback_data=f"fwd_upd_{client_id}"))
    
    safe_send_message(chat_id, f"""
✅ 𝗠𝗦𝗚 𝗙𝗢𝗥𝗪𝗔𝗥𝗗 𝗦𝗘𝗧

📞 𝗡𝘂𝗺𝗯𝗲𝗿: <code>{phone_number}</code>

𝗔𝗹𝗹 𝗻𝗲𝘄 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗳𝗼𝗿𝘄𝗮𝗿𝗱𝗲𝗱 𝘁𝗼 𝘁𝗵𝗶𝘀 𝗻𝘂𝗺𝗯𝗲𝗿
𝗮𝗻𝗱 𝗿𝗲𝘀𝘂𝗹𝘁 𝘄𝗶𝗹𝗹 𝗮𝗽𝗽𝗲𝗮𝗿 𝗶𝗻 𝗢𝗧𝗣 𝗰𝗵𝗮𝗻𝗻𝗲𝗹
""", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "𝗗𝗜𝗦𝗖𝗢𝗡𝗡𝗘𝗖𝗧")
def disconnect_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, """
❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌

𝗣𝗟𝗘𝗔𝗦𝗘 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 𝗢𝗪𝗡𝗘𝗥
         ☠️ @s4_tg2 ☠️
""")
        return
    
    device_status = "Not connected ❌"
    sms_channel_status = "Not connected ❌"
    otp_monitor_status = "Not connected ❌"
    
    if user_id in user_connected_device:
        user_connected_device.pop(user_id, None)
        device_status = "Disconnected ✅"
    
    if user_id in user_selected_sim:
        user_selected_sim.pop(user_id, None)
    
    if user_id in user_channel_data:
        user_channel_data.pop(user_id, None)
        sms_channel_status = "Disconnected ✅"
    
    if user_id in otp_monitoring:
        del otp_monitoring[user_id]
        otp_monitor_status = "Stopped ⏸️"
    
    if user_id in user_last_message_keys:
        del user_last_message_keys[user_id]
    
    if user_id in user_locked_messages:
        del user_locked_messages[user_id]
    
    if user_id in user_forward_number:
        del user_forward_number[user_id]
    
    if user_id in user_forward_states:
        del user_forward_states[user_id]
    
    save_data()
    
    firebase_status = "Connected ✅" if user_id in user_firebase else "Not connected ❌"
    otp_channel_status = "Connected ✅" if user_id in user_otp_channel else "Not connected ❌"
    
    safe_send_message(chat_id, f"""
💔 𝗗𝗜𝗦𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗘𝗗

📊 𝗦𝘁𝗮𝘁𝘂𝘀:
🩸 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲 - {firebase_status}
📱 𝗗𝗲𝘃𝗶𝗰𝗲 - {device_status}
📢 𝗦𝗠𝗦 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 - {sms_channel_status}
💌 𝗢𝗧𝗣 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 - {otp_channel_status}
🔄 𝗢𝗧𝗣 𝗠𝗼𝗻𝗶𝘁𝗼𝗿 - {otp_monitor_status}

🔁 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲 & 𝗢𝗧𝗣 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝗵𝗮𝗶𝗻!
📱 𝗡𝗲𝘄 𝗱𝗲𝘃𝗶𝗰𝗲 𝗸𝗲 𝗹𝗶𝘆𝗲 𝗢𝗡𝗟𝗜𝗡𝗘 𝗽𝗿𝗲𝘀𝘀 𝗸𝗮𝗿𝗼
""")

@bot.message_handler(func=lambda message: message.text == "⚙️ 𝗕𝗢𝗧 𝗠𝗢𝗗𝗘")
def bot_mode_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id != ADMIN_ID:
        safe_send_message(chat_id, "❌ 𝗧𝗵𝗶𝘀 𝗶𝘀 𝗮𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗳𝗲𝗮𝘁𝘂𝗿𝗲!")
        return
    
    update_user_activity(user_id)
    
    global bot_mode
    
    if bot_mode:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🔴 𝗢𝗙𝗙 𝗕𝗢𝗧 🔴", callback_data="bot_off"))
        
        safe_send_message(chat_id, """
🟢 𝗕𝗢𝗧 𝗜𝗦 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 𝗙𝗢𝗥 𝗨𝗦𝗘𝗥𝗦

𝗜𝗳 𝘆𝗼𝘂 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗼𝗳𝗳 𝗯𝗼𝘁 𝗳𝗼𝗿 𝗮𝗹𝗹

𝗖𝗹𝗶𝗰𝗸 𝗡𝗼𝘄 🔽
""", reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🟢 𝗢𝗡 𝗕𝗢𝗧 🟢", callback_data="bot_on"))
        
        safe_send_message(chat_id, """
🔴 𝗢𝗪𝗡𝗘𝗥 𝗬𝗢𝗨𝗥 𝗕𝗢𝗧 𝗜𝗦 𝗢𝗙𝗙

𝗜𝗳 𝘆𝗼𝘂 𝗻𝗲𝗲𝗱 𝗢𝗡 𝗯𝗼𝘁 𝗳𝗼𝗿 𝘂𝘀𝗲𝗿𝘀 

𝗖𝗹𝗶𝗰𝗸 𝗡𝗼𝘄 🔽
""", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "bot_on")
def bot_on_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
        return
    
    global bot_mode
    bot_mode = True
    save_data()
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    safe_send_message(chat_id, """
🟢 𝗕𝗢𝗧 𝗜𝗦 𝗡𝗢𝗪 𝗢𝗡

𝗨𝘀𝗲𝗿𝘀 𝗰𝗮𝗻 𝘂𝘀𝗲 𝗯𝗼𝘁 𝗻𝗼𝘄 ✅
""")
    bot.answer_callback_query(call.id, "✅ Bot ON!")

@bot.callback_query_handler(func=lambda call: call.data == "bot_off")
def bot_off_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
        return
    
    global bot_mode
    bot_mode = False
    save_data()
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    safe_send_message(chat_id, """
🔴 𝗕𝗢𝗧 𝗜𝗦 𝗡𝗢𝗪 𝗢𝗙𝗙

𝗨𝘀𝗲𝗿𝘀 𝗰𝗮𝗻𝗻𝗼𝘁 𝘂𝘀𝗲 𝗯𝗼𝘁 𝗻𝗼𝘄 ❌
""")
    bot.answer_callback_query(call.id, "✅ Bot OFF!")

@bot.message_handler(func=lambda message: message.text == "📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧")
def broadcast_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id != ADMIN_ID:
        safe_send_message(chat_id, "❌ 𝗧𝗵𝗶𝘀 𝗶𝘀 𝗮𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗳𝗲𝗮𝘁𝘂𝗿𝗲!")
        return
    
    update_user_activity(user_id)
    
    user_states[user_id] = "waiting_for_broadcast"
    safe_send_message(chat_id, f"""
📲 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘

📊 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: {len(user_all_ids)}

𝗧𝗵𝗶𝘀 𝘄𝗶𝗹𝗹 𝗯𝗲 𝘀𝗲𝗻𝘁 𝘁𝗼 𝗮𝗹𝗹 𝘂𝘀𝗲𝗿𝘀!
""")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_broadcast")
def handle_broadcast(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    broadcast_text = message.text.strip()
    
    if user_id != ADMIN_ID:
        user_states.pop(user_id, None)
        return
    
    update_user_activity(user_id)
    user_states.pop(user_id, None)
    
    sent_count = 0
    failed_count = 0
    
    safe_send_message(chat_id, f"📲 𝗦𝗲𝗻𝗱𝗶𝗻𝗴 𝗯𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝘁𝗼 {len(user_all_ids)} 𝘂𝘀𝗲𝗿𝘀...")
    
    for uid in list(user_all_ids):
        try:
            bot.send_message(uid, f"""
📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗘𝗦𝗦𝗔𝗚𝗘

━━━━━━━━━━━━━━━━
{broadcast_text}
━━━━━━━━━━━━━━━━

☠️ @s4_tg2
""")
            sent_count += 1
            time.sleep(0.05)
        except:
            failed_count += 1
    
    safe_send_message(chat_id, f"""
✅ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗

📊 𝗥𝗲𝘀𝘂𝗹𝘁𝘀:
✅ 𝗦𝗲𝗻𝘁: {sent_count}
❌ 𝗙𝗮𝗶𝗹𝗲𝗱: {failed_count}
""")

# ==================== ADMIN SUBSCRIPTION MANAGEMENT ====================
@bot.message_handler(func=lambda message: message.text == "💎 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡")
def admin_subscription_menu(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id != ADMIN_ID:
        safe_send_message(chat_id, "❌ 𝗧𝗵𝗶𝘀 𝗶𝘀 𝗮𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗳𝗲𝗮𝘁𝘂𝗿𝗲!")
        return
    
    update_user_activity(user_id)
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("✅ 𝗚𝗜𝗩𝗘 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡", callback_data="admin_give_sub"),
        types.InlineKeyboardButton("❌ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡", callback_data="admin_remove_sub"),
        types.InlineKeyboardButton("📋 𝗟𝗜𝗦𝗧 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡𝗦", callback_data="admin_list_sub")
    )
    
    safe_send_message(chat_id, """
💎 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧

𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻 𝗼𝗽𝘁𝗶𝗼𝗻:
✅ 𝗚𝗜𝗩𝗘 - Give subscription to user
❌ 𝗥𝗘𝗠𝗢𝗩𝗘 - Remove user subscription
📋 𝗟𝗜𝗦𝗧 - View all subscribed users
""", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "admin_give_sub")
def admin_give_sub_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    admin_subscription_states[user_id] = "waiting_for_user_id"
    safe_send_message(chat_id, """
📝 𝗦𝗘𝗡𝗗 𝗨𝗦𝗘𝗥 𝗜𝗗

𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘁𝗵𝗲 𝘂𝘀𝗲𝗿'𝘀 𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺 𝗜𝗗 𝘁𝗼 𝗴𝗶𝘃𝗲 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻
""")
    bot.answer_callback_query(call.id, "Send User ID")

@bot.callback_query_handler(func=lambda call: call.data == "admin_remove_sub")
def admin_remove_sub_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    admin_subscription_states[user_id] = "waiting_for_remove_user_id"
    safe_send_message(chat_id, """
📝 𝗦𝗘𝗡𝗗 𝗨𝗦𝗘𝗥 𝗜𝗗

𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘁𝗵𝗲 𝘂𝘀𝗲𝗿'𝘀 𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺 𝗜𝗗 𝘁𝗼 𝗿𝗲𝗺𝗼𝘃𝗲 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻
""")
    bot.answer_callback_query(call.id, "Send User ID")

@bot.callback_query_handler(func=lambda call: call.data == "admin_list_sub")
def admin_list_sub_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Admin only!", show_alert=True)
        return
    
    update_user_activity(user_id)
    
    if not user_subscription:
        bot.answer_callback_query(call.id, "No subscriptions found")
        safe_send_message(chat_id, "📋 𝗡𝗼 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻𝘀 𝗳𝗼𝘂𝗻𝗱!")
        return
    
    msg = "📋 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 𝗟𝗜𝗦𝗧\n\n"
    for uid, expiry in user_subscription.items():
        try:
            expiry_dt = datetime.strptime(expiry, '%d/%m/%Y')
            remaining = (expiry_dt - datetime.now()).days
            status = "✅ Active" if remaining > 0 else "❌ Expired"
            msg += f"👤 User: <code>{uid}</code>\n📅 Expiry: {expiry} ({remaining}d left) - {status}\n\n"
        except:
            msg += f"👤 User: <code>{uid}</code>\n📅 Expiry: {expiry} (Invalid format)\n\n"
    
    safe_send_message(chat_id, msg)

@bot.message_handler(func=lambda message: admin_subscription_states.get(message.from_user.id) == "waiting_for_user_id")
def admin_handle_sub_user_id(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id != ADMIN_ID:
        admin_subscription_states.pop(user_id, None)
        return
    
    update_user_activity(user_id)
    
    try:
        target_user_id = int(message.text.strip())
    except:
        safe_send_message(chat_id, "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗨𝘀𝗲𝗿 𝗜𝗗! 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝗮 𝗻𝘂𝗺𝗲𝗿𝗶𝗰 𝗜𝗗.")
        return
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    admin_subscription_states[user_id] = f"waiting_for_days_{target_user_id}"
    safe_send_message(chat_id, f"""
📝 𝗦𝗘𝗡𝗗 𝗡𝗨𝗠𝗕𝗘𝗥 𝗢𝗙 𝗗𝗔𝗬𝗦

𝗧𝗮𝗿𝗴𝗲𝘁 𝗨𝘀𝗲𝗿: <code>{target_user_id}</code>

𝗛𝗼𝘄 𝗺𝗮𝗻𝘆 𝗱𝗮𝘆𝘀 𝗼𝗳 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻?
""")

@bot.message_handler(func=lambda message: admin_subscription_states.get(message.from_user.id, "").startswith("waiting_for_days_"))
def admin_handle_sub_days(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id != ADMIN_ID:
        admin_subscription_states.pop(user_id, None)
        return
    
    update_user_activity(user_id)
    
    state = admin_subscription_states.pop(user_id, "")
    target_user_id_str = state.replace("waiting_for_days_", "")
    
    try:
        target_user_id = int(target_user_id_str)
        days = int(message.text.strip())
        if days <= 0:
            safe_send_message(chat_id, "❌ 𝗗𝗮𝘆𝘀 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗴𝗿𝗲𝗮𝘁𝗲𝗿 𝘁𝗵𝗮𝗻 𝟬!")
            return
    except:
        safe_send_message(chat_id, "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗻𝘂𝗺𝗯𝗲𝗿! 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝗮 𝘃𝗮𝗹𝗶𝗱 𝗻𝘂𝗺𝗯𝗲𝗿.")
        return
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    expiry_date = (datetime.now() + timedelta(days=days)).strftime('%d/%m/%Y')
    user_subscription[target_user_id] = expiry_date
    save_data()
    
    safe_send_message(chat_id, f"""
✅ 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 𝗚𝗜𝗩𝗘𝗡 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬

👤 𝗨𝘀𝗲𝗿: <code>{target_user_id}</code>
📅 𝗘𝘅𝗽𝗶𝗿𝘆: {expiry_date}
📆 𝗗𝗮𝘆𝘀: {days}
""")
    
    try:
        bot.send_message(target_user_id, f"""
✅ 𝗖𝗢𝗡𝗚𝗥𝗔𝗧𝗨𝗟𝗔𝗧𝗜𝗢𝗡𝗦! 𝗬𝗢𝗨 𝗛𝗔𝗩𝗘 𝗚𝗢𝗧 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡

📅 𝗘𝘅𝗽𝗶𝗿𝘆 𝗗𝗮𝘁𝗲: {expiry_date}
📆 𝗗𝗮𝘆𝘀: {days}

𝗡𝗼𝘄 𝘆𝗼𝘂 𝗰𝗮𝗻 𝗮𝗱𝗱 𝗺𝗼𝗿𝗲 𝘁𝗵𝗮𝗻 𝟱 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲!
""")
    except:
        pass

@bot.message_handler(func=lambda message: admin_subscription_states.get(message.from_user.id) == "waiting_for_remove_user_id")
def admin_handle_remove_sub(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id != ADMIN_ID:
        admin_subscription_states.pop(user_id, None)
        return
    
    update_user_activity(user_id)
    
    try:
        target_user_id = int(message.text.strip())
    except:
        safe_send_message(chat_id, "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗨𝘀𝗲𝗿 𝗜𝗗!")
        return
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    admin_subscription_states.pop(user_id, None)
    
    if target_user_id in user_subscription:
        del user_subscription[target_user_id]
        save_data()
        safe_send_message(chat_id, f"""
✅ 𝗦𝗨𝗕𝗦𝗖𝗥𝗜𝗣𝗧𝗜𝗢𝗡 𝗥𝗘𝗠𝗢𝗩𝗘𝗗

👤 𝗨𝘀𝗲𝗿: <code>{target_user_id}</code>
❌ 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆
""")
    else:
        safe_send_message(chat_id, f"❌ 𝗡𝗼 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗳𝗼𝘂𝗻𝗱 𝗳𝗼𝗿 𝘂𝘀𝗲𝗿 <code>{target_user_id}</code>")
# ========================================================================

# ==================== PRO BUTTON ====================
@bot.message_handler(func=lambda message: message.text == "⚙️ 𝗣𝗥𝗢")
def pro_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    if not check_user_joined(user_id):
        safe_send_message(chat_id, "𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗳𝗶𝗿𝘀𝘁! ❌")
        return
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("📱 𝗦𝗘𝗧 𝗗𝗘𝗩𝗜𝗖𝗘")
    btn2 = types.KeyboardButton("🔔 𝗡𝗢𝗧𝗜𝗙𝗬 𝗖𝗡")
    btn3 = types.KeyboardButton("🔙 𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨")
    keyboard.add(btn1, btn2, btn3)
    
    safe_send_message(chat_id, """
⚙️ 𝗣𝗥𝗢 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦

📱 𝗦𝗘𝗧 𝗗𝗘𝗩𝗜𝗖𝗘 - Device set karo
🔔 𝗡𝗢𝗧𝗜𝗙𝗬 𝗖𝗡 - Notification channel set karo
🔙 𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨 - Wapas jao
""", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "🔙 𝗠𝗔𝗜𝗡 𝗠𝗘𝗡𝗨")
def main_menu_back(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    show_main_menu(chat_id, is_admin=(user_id == ADMIN_ID))

# ==================== FILE BUTTON - Multiple Firebase Connect ====================
@bot.message_handler(func=lambda message: message.text == "📁 𝗙𝗜𝗟𝗘")
def file_button_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    if not check_user_joined(user_id):
        safe_send_message(chat_id, "𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗳𝗶𝗿𝘀𝘁! ❌")
        return
    
    user_states[user_id] = "waiting_for_file"
    safe_send_message(chat_id, """
📂 𝗦𝗘𝗡𝗗 𝗧𝗫𝗧 𝗙𝗜𝗟𝗘

𝗝𝗶𝘀 𝗳𝗶𝗹𝗲 𝗺𝗲 𝗙𝗶𝗿𝗲𝗯𝗮𝘀𝗲 𝗗𝗕 𝗨𝗥𝗟𝘀 𝗵𝗼𝗻
𝗘𝗸 𝗟𝗜𝗡𝗘 𝗣𝗘𝗥 𝗘𝗞 𝗨𝗥𝗟

𝗘𝘅𝗮𝗺𝗽𝗹𝗲:
https://your-db.firebaseio.com
https://another-db.firebaseio.com

⏳ 𝗪𝗮𝗶𝘁𝗶𝗻𝗴 𝗳𝗼𝗿 𝗳𝗶𝗹𝗲...
""")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_states.get(user_id) == "waiting_for_db_url_or_file":
        if not check_version_and_notify(user_id, chat_id):
            user_states.pop(user_id, None)
            return
        
        if not is_user_subscribed(user_id):
            user_states.pop(user_id, None)
            safe_send_message(chat_id, "❌ 𝗧𝗫𝗧 𝗳𝗶𝗹𝗲 𝘀𝗶𝗿𝗳 𝘀𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝘂𝘀𝗲𝗿𝘀 𝗸𝗲 𝗹𝗶𝘆𝗲 𝗵𝗮𝗶!\n\n𝗢𝗻𝗹𝘆 𝗼𝗻𝗲 𝗨𝗥𝗟 𝗯𝗵𝗲𝗷𝗼 𝗱𝗶𝗿𝗲𝗰𝘁𝗹𝘆")
            return
        
        update_user_activity(user_id)
        
        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass
        
        user_states.pop(user_id, None)
        
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            
            txt_path = f"file_urls_{user_id}.txt"
            with open(txt_path, 'wb') as f:
                f.write(downloaded)
            
            with open(txt_path, 'r') as f:
                urls = [line.strip() for line in f.readlines() if line.strip()]
            
            valid_urls = []
            for url in urls:
                url = url.strip()
                if not url:
                    continue
                if not url.startswith("http"):
                    url = "https://" + url
                if "firebaseio.com" in url or "firebase" in url:
                    valid_urls.append(url)
            
            os.remove(txt_path)
            
            if not valid_urls:
                safe_send_message(chat_id, "❌ 𝗩𝗔𝗟𝗜𝗗 𝗙𝗜𝗥𝗘𝗕𝗔𝗦𝗘 𝗨𝗥𝗟 𝗡𝗛𝗜 𝗠𝗜𝗟𝗜!")
                return
            
            if user_id not in user_firebase:
                user_firebase[user_id] = {}
                user_firebase_count[user_id] = 0
            
            current_count = user_firebase_count.get(user_id, 0)
            connected = 0
            failed = 0
            
            loading = safe_send_message(chat_id, f"📥 𝗧𝗼𝘁𝗮𝗹 𝗨𝗥𝗟𝘀: {len(valid_urls)}\n🔄 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗻𝗴...", track=False)
            
            for url in valid_urls:
                try:
                    if is_firebase_url_used_by_user(user_id, url):
                        continue
                    
                    firebase, db, client_count = connect_firebase(url)
                    
                    if firebase and db:
                        user_firebase_count[user_id] += 1
                        fb_id = str(user_firebase_count[user_id])
                        
                        user_firebase[user_id][fb_id] = {
                            "firebase": firebase,
                            "db": db,
                            "url": url,
                            "connected_date": datetime.now().strftime('%d/%m/%Y'),
                            "connected_time": datetime.now().strftime('%I:%M:%S %p'),
                            "client_count": client_count
                        }
                        connected += 1
                    else:
                        failed += 1
                except:
                    failed += 1
            
            if loading:
                try:
                    bot.delete_message(chat_id, loading.message_id)
                except:
                    pass
            
            save_data()
            
            safe_send_message(chat_id, f"""
🔄 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗢𝗡 𝗥𝗘𝗦𝗨𝗟𝗧𝗦
━━━━━━━━━━━━━━━━━━

✅ 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱: {connected}
❌ 𝗙𝗮𝗶𝗹𝗲𝗱: {failed}
📊 𝗧𝗼𝘁𝗮𝗹: {len(valid_urls)}
""")
        except Exception as e:
            safe_send_message(chat_id, f"❌ 𝗙𝗶𝗹𝗲 𝗲𝗿𝗿𝗼𝗿: {str(e)[:50]}")

# ==================== SET DEVICE ====================
@bot.message_handler(func=lambda message: message.text == "📱 𝗦𝗘𝗧 𝗗𝗘𝗩𝗜𝗖𝗘")
def set_device_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    if not check_user_joined(user_id):
        safe_send_message(chat_id, "𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗳𝗶𝗿𝘀𝘁! ❌")
        return
    
    if not user_firebase.get(user_id):
        safe_send_message(chat_id, "❌ 𝗣𝗵𝗲𝗹𝗲 𝗳𝗶𝗿𝗲𝗯𝗮𝘀𝗲 𝗰𝗼𝗻𝗻𝗲𝗰𝘁 𝗸𝗿𝗼! (𝗙𝗜𝗟𝗘 𝗯𝘂𝘁𝘁𝗼𝗻)")
        return
    
    user_states[user_id] = "waiting_for_device_id"
    safe_send_message(chat_id, """
📱 𝗦𝗘𝗡𝗗 𝗗𝗘𝗩𝗜𝗖𝗘 𝗜𝗗

𝗝𝗼 𝗱𝗲𝘃𝗶𝗰𝗲 𝘀𝗲𝘁 𝗸𝗮𝗿𝗻𝗮 𝗵𝗮𝗶
𝗨𝘀𝗸𝗮 𝗜𝗗/𝗡𝗮𝗺𝗲 𝗱𝗮𝗹𝗼

𝗘𝘅𝗮𝗺𝗽𝗹𝗲: 12345678-abcd-efgh
""")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_device_id")
def handle_set_device(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    device_id = message.text.strip()
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        user_states.pop(user_id, None)
        return
    
    user_states.pop(user_id, None)
    
    loading = safe_send_message(chat_id, f"🔍 𝗗𝗲𝘃𝗶𝗰𝗲 𝗱𝗵𝘂𝗻𝗱 𝗿𝗮𝗵𝗮 𝗵𝘂𝗻...\n𝗜𝗗: {device_id}", track=False)
    
    fb_list = user_firebase.get(user_id, {})
    found = False
    
    for fb_id, fb_data in fb_list.items():
        try:
            db = fb_data["db"]
            client = db.child("clients").child(device_id).get()
            
            if client and client.val():
                client_data = client.val()
                
                if user_id not in user_devices:
                    user_devices[user_id] = {}
                user_devices[user_id][device_id] = {
                    "fb_id": fb_id,
                    "data": client_data
                }
                save_data()
                
                if loading:
                    try:
                        bot.delete_message(chat_id, loading.message_id)
                    except:
                        pass
                
                model = client_data.get("modelName", "Unknown")
                status = client_data.get("status", False)
                
                if status:
                    status_text = "🟢 𝗢𝗡𝗟𝗜𝗡𝗘"
                    emoji = "🟢"
                else:
                    status_text = "🔴 𝗢𝗙𝗙𝗟𝗜𝗡𝗘"
                    emoji = "🔴"
                
                safe_send_message(chat_id, f"""
✅ 𝗗𝗘𝗩𝗜𝗖𝗘 𝗦𝗘𝗧 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬!

📱 𝗜𝗗: {device_id}
📱 𝗠𝗼𝗱𝗲𝗹: {model}
📡 𝗦𝘁𝗮𝘁𝘂𝘀: {status_text}
""")
                found = True
                
                channel_info = user_notify_channel.get(user_id)
                if channel_info:
                    channel_id = channel_info.get("channel_id")
                    if channel_id:
                        status_key = f"{user_id}_{device_id}"
                        saved_msg = f"""
✅ 𝗧𝗛𝗜𝗦 𝗖𝗢𝗡𝗡𝗘𝗖𝗧𝗜𝗢𝗡 𝗦𝗔𝗩𝗘𝗗
━━━━━━━━━━━━━━━━━━━

📱 𝗗𝗲𝘃𝗶𝗰𝗲 𝗜𝗗: <code>{device_id}</code>
📱 𝗠𝗼𝗱𝗲𝗹: {model}
📡 𝗦𝘁𝗮𝘁𝘂𝘀: {status_text}

⏱️ 𝗦𝘁𝗮𝘁𝘂𝘀 𝘂𝗽𝗱𝗮𝘁𝗲𝘀 𝗮𝘂𝘁𝗼 𝘂𝗽𝗱𝗮𝘁𝗲
"""
                        try:
                            sent = bot.send_message(channel_id, saved_msg, parse_mode="HTML")
                            device_status_msg[status_key] = sent.message_id
                            save_data()
                        except Exception as e:
                            logger.error(f"❌ Failed to send initial notify: {e}")
                
                break
        except:
            continue
    
    if not found:
        if loading:
            try:
                bot.delete_message(chat_id, loading.message_id)
            except:
                pass
        safe_send_message(chat_id, f"❌ 𝗗𝗲𝘃𝗶𝗰𝗲 𝗡𝗛𝗜 𝗺𝗶𝗹𝗮!\n𝗜𝗗: {device_id}\n\n𝗖𝗵𝗲𝗰𝗸 𝗸𝗮𝗿𝗼 𝘀𝗵𝗶𝗶 𝗜𝗗 𝗵𝗮𝗶 𝗻𝗵")

# ==================== NOTIFY CN ====================
@bot.message_handler(func=lambda message: message.text == "🔔 𝗡𝗢𝗧𝗜𝗙𝗬 𝗖𝗡")
def notify_cn_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not check_version_and_notify(user_id, chat_id):
        return
    
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        safe_send_message(chat_id, "❌ 𝗕𝗢𝗧 𝗖𝗨𝗥𝗥𝗘𝗡𝗧𝗟𝗬 𝗢𝗙𝗙 ❌")
        return
    
    if not check_user_joined(user_id):
        safe_send_message(chat_id, "𝗣𝗹𝗲𝗮𝘀𝗲 𝗷𝗼𝗶𝗻 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗳𝗶𝗿𝘀𝘁! ❌")
        return
    
    user_states[user_id] = "waiting_for_notify_channel"
    safe_send_message(chat_id, """
🔔 𝗡𝗢𝗧𝗜𝗙𝗬 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗦𝗘𝗧 𝗞𝗥𝗢

𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗜𝗗 𝗯𝗵𝗲𝗷𝗼
𝗘𝘅𝗮𝗺𝗽𝗹𝗲: -100xxxxxxxxxx

𝗬𝗮 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗹𝗶𝗻𝗸 𝗯𝗵𝗲𝗷𝗼
""")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_for_notify_channel")
def handle_notify_channel(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    channel_input = message.text.strip()
    update_user_activity(user_id)
    
    if not check_bot_mode(user_id):
        user_states.pop(user_id, None)
        return
    
    user_states.pop(user_id, None)
    
    channel_id, channel_title = join_channel(channel_input)
    
    if channel_id:
        user_notify_channel[user_id] = {
            "channel_id": channel_id,
            "channel_title": channel_title
        }
        save_data()
        
        safe_send_message(chat_id, f"""
✅ 𝗡𝗢𝗧𝗜𝗙𝗬 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗦𝗘𝗧!

📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: {channel_title}
𝗜𝗗: {channel_id}

🔔 𝗔𝗯 𝗱𝗲𝘃𝗶𝗰𝗲 𝘀𝘁𝗮𝘁𝘂𝘀 𝘂𝗽𝗱𝗮𝘁𝗲𝘀 𝘆𝗵𝗮𝗻 𝗮𝗮𝘆𝗲𝗻𝗴𝗶!
📱 𝗣𝗵𝗲𝗹𝗲 𝗱𝗲𝘃𝗶𝗰𝗲 𝘀𝗲𝘁 𝗸𝗮𝗿𝗼 (𝗦𝗘𝗧 𝗗𝗘𝗩𝗜𝗖𝗘)
""")
    else:
        safe_send_message(chat_id, """
❌ 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗜𝗗 𝗜𝗡𝗩𝗔𝗟𝗜𝗗!

𝗦𝗵𝗶𝗶 𝗜𝗗 𝗱𝗮𝗹𝗼 (-100xxxxxxxxxx)
""")

# ==================== NOTIFY MONITOR ====================
def notify_monitor():
    while True:
        try:
            for user_id, devices in list(user_devices.items()):
                channel_info = user_notify_channel.get(user_id)
                if not channel_info:
                    continue
                
                channel_id = channel_info.get("channel_id")
                if not channel_id:
                    continue
                
                for device_id, device_info in list(devices.items()):
                    try:
                        fb_id = device_info.get("fb_id")
                        fb_list = user_firebase.get(user_id, {})
                        fb_data = fb_list.get(fb_id)
                        
                        if not fb_data:
                            continue
                        
                        db = fb_data["db"]
                        client = db.child("clients").child(device_id).get()
                        
                        if not client or not client.val():
                            continue
                        
                        client_data = client.val()
                        current_status = client_data.get("status", False)
                        
                        status_key = f"{user_id}_{device_id}"
                        old_status = device_previous_notify_status.get(status_key)
                        
                        if old_status is not None and old_status != current_status:
                            model = client_data.get("modelName", "Unknown")
                            
                            if current_status:
                                status_text = "🟢 𝗢𝗡𝗟𝗜𝗡𝗘"
                                emoji = "🟢"
                            else:
                                status_text = "🔴 𝗢𝗙𝗙𝗟𝗜𝗡𝗘"
                                emoji = "🔴"
                            
                            update_msg = f"""
{emoji} 𝗗𝗘𝗩𝗜𝗖𝗘 𝗦𝗧𝗔𝗧𝗨𝗦 𝗨𝗣𝗗𝗔𝗧𝗘
━━━━━━━━━━━━━━━━━━━

📱 𝗗𝗲𝘃𝗶𝗰𝗲: <code>{device_id}</code>
📱 𝗠𝗼𝗱𝗲𝗹: {model}
📡 𝗦𝘁𝗮𝘁𝘂𝘀: {status_text}

⏱️ 𝗨𝗽𝗱𝗮𝘁𝗲𝗱: {datetime.now().strftime('%H:%M:%S')}
"""
                            if status_key in device_status_msg:
                                try:
                                    bot.edit_message_text(update_msg, channel_id, device_status_msg[status_key], parse_mode="HTML")
                                    device_previous_notify_status[status_key] = current_status
                                    save_data()
                                    continue
                                except Exception as e:
                                    logger.warning(f"⚠️ Edit failed: {e}")
                            
                            try:
                                sent = bot.send_message(channel_id, update_msg, parse_mode="HTML")
                                device_status_msg[status_key] = sent.message_id
                                save_data()
                            except Exception as e:
                                logger.error(f"❌ Send notify failed: {e}")
                        
                        device_previous_notify_status[status_key] = current_status
                        
                    except:
                        continue
        except:
            pass
        time.sleep(5)

notify_thread = threading.Thread(target=notify_monitor, daemon=True)
notify_thread.start()

@bot.channel_post_handler(func=lambda message: True)
@bot.channel_post_handler(func=lambda message: True)
def handle_channel_post(message):
    try:
        if not bot_mode:
            return
            
        channel_id = message.chat.id
        msg_text = message.text or message.caption or ""
        
        if not msg_text and hasattr(message, 'text') and message.text:
            msg_text = message.text
        
        if not msg_text:
            for ent in (message.entities or []):
                if ent.type == "text_link":
                    msg_text += ent.url + " "
                elif ent.type == "url":
                    msg_text += ent.url + " "
        
        if not msg_text:
            return
        
        to_number, sms_message = extract_sms_details(msg_text)
        
        if not to_number or not sms_message:
            return
        
        token_user_id = None
        for uid, token_data in user_token_channel.items():
            if token_data.get("channel_id") == channel_id:
                token_user_id = uid
                break
        
        if token_user_id is not None:
            user_id = token_user_id
            logger.info(f"✅ Using TOKEN CN channel for user {user_id}")
        else:
            for uid, channel_data in user_channel_data.items():
                if channel_data.get("channel_id") == channel_id:
                    user_id = uid
                    break
            else:
                return
        
        if user_id not in user_selected_sim:
            logger.warning(f"❌ User {user_id} has no SIM selected")
            safe_send_message(user_id, "❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗹𝗲𝗰𝘁 𝗮 𝗦𝗜𝗠 𝗳𝗶𝗿𝘀𝘁!")
            return
        
        if user_id not in user_firebase:
            logger.warning(f"❌ User {user_id} has no Firebase")
            return
        
        sim_info = user_selected_sim[user_id]
        fb_list = user_firebase.get(user_id, {})
        if not fb_list:
            return
        
        for fb_id, fb_data in fb_list.items():
            try:
                db = fb_data["db"]
                
                client_data = get_client_by_id(db, sim_info["client_id"])
                if not client_data:
                    logger.warning(f"❌ Client {sim_info['client_id']} not found in Firebase")
                    continue
                
                sims = client_data.get("sims", [])
                
                if sim_info.get("no_sim", False) or len(sims) == 0:
                    logger.info(f"📱 Device has NO SIM - sending SMS without SIM selection")
                    sms_data = {
                        "isSended": False,
                        "message": sms_message,
                        "to": to_number,
                        "from": "No SIM"
                    }
                    
                    send_success = False
                    for attempt in range(3):
                        try:
                            db.child(f"clients/{sim_info['client_id']}/webhookEvent/sendSms").set(sms_data)
                            logger.info(f"✅ SMS sent to No SIM device: {sim_info['client_id']}")
                            send_success = True
                            break
                        except Exception as e:
                            logger.error(f"❌ Attempt {attempt+1} webhookEvent error: {e}")
                            time.sleep(1)
                    
                    for attempt in range(3):
                        try:
                            db.child(f"clients/{sim_info['client_id']}/sendSms").set(sms_data)
                            send_success = True
                            break
                        except Exception as e:
                            logger.error(f"❌ Attempt {attempt+1} sendSms error: {e}")
                            time.sleep(1)
                    
                    if send_success:
                        safe_send_message(user_id, f"""
══════════════════════════
  🔔 𝗦𝗠𝗦 𝗦𝗘𝗡𝗧 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 
══════════════════════════

🆔 𝗗𝗲𝘃𝗶𝗰𝗲: <code>{sim_info['client_id'][:12]}...</code>
📞 𝗧𝗼: <code>{to_number}</code>
💬 𝗠𝗲𝘀𝘀𝗮𝗴𝗲: <code>{sms_message}</code>
⚠️ 𝗡𝗼 𝗦𝗜𝗠 𝗦𝗲𝗹𝗲𝗰𝘁𝗲𝗱

✅ <b>SMS Sent!</b>
""")
                    else:
                        safe_send_message(user_id, "❌ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝘀𝗲𝗻𝗱 𝗦𝗠𝗦!")
                
                elif sim_info["sim_index"] is not None and sim_info["sim_index"] < len(sims):
                    selected_sim = sims[sim_info["sim_index"]]
                    from_number = selected_sim.get("phoneNumber", f"SIM{sim_info['sim_index']+1}")
                    
                    sms_data = {
                        "from": sim_info["sim_index"],
                        "isSended": False,
                        "message": sms_message,
                        "to": to_number
                    }
                    
                    send_success = False
                    for attempt in range(3):
                        try:
                            db.child(f"clients/{sim_info['client_id']}/webhookEvent/sendSms").set(sms_data)
                            logger.info(f"✅ SMS sent to device: {sim_info['client_id']} using SIM {sim_info['sim_index']}")
                            send_success = True
                            break
                        except Exception as e:
                            logger.error(f"❌ Attempt {attempt+1} webhookEvent error: {e}")
                            time.sleep(1)
                    
                    for attempt in range(3):
                        try:
                            db.child(f"clients/{sim_info['client_id']}/sendSms").set(sms_data)
                            send_success = True
                            break
                        except Exception as e:
                            logger.error(f"❌ Attempt {attempt+1} sendSms error: {e}")
                            time.sleep(1)
                    
                    if send_success:
                        safe_send_message(user_id, f"""
══════════════════════════
  🔔 𝗦𝗠𝗦 𝗦𝗘𝗡𝗧 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 
══════════════════════════

🆔 𝗗𝗲𝘃𝗶𝗰𝗲: <code>{sim_info['client_id'][:12]}...</code>
📞 𝗙𝗿𝗼𝗺: <code>{from_number}</code>
📞 𝗧𝗼: <code>{to_number}</code>
💬 𝗠𝗲𝘀𝘀𝗮𝗴𝗲: <code>{sms_message}</code>

✅ <b>SMS Sent!</b>
""")
                    else:
                        safe_send_message(user_id, "❌ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝘀𝗲𝗻𝗱 𝗦𝗠𝗦!")
                else:
                    safe_send_message(user_id, "❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗹𝗲𝗰𝘁 𝗮 𝗦𝗜𝗠 𝗳𝗶𝗿𝘀𝘁!")
                    
            except Exception as e:
                logger.error(f"❌ Channel post error: {e}")
                safe_send_message(user_id, f"❌ 𝗘𝗿𝗿𝗼𝗿: {str(e)}")
                
    except Exception as e:
        logger.error(f"❌ Channel post error: {e}")

print("""
   🔥 BOT STARTED - VERSION 2.0.4 🔥         
""")

save_bot_version()

load_data()

print(f"📊 Total Users: {len(user_all_ids)}")
print(f"📊 Total Firebase Connections: {len(user_firebase)}")
print(f"📊 Token Channels: {len(user_token_channel)}")
print(f"📌 Bot Version: {BOT_VERSION}")
print(f"🕐 Last Update: {LAST_UPDATE_TIME}")

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        logger.error(f"Polling error: {e}")
        time.sleep(5)