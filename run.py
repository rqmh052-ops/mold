#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║         EVERIX - Free Fire Auto Account Generator       ║
║         Powered by: termux_guest_gen engine             ║
╚══════════════════════════════════════════════════════════╝

تشغيل:  python run.py
الإعدادات في ملف everix.py
"""

import time
import json
import requests as req_lib
from pathlib import Path
from datetime import datetime

# ── تحميل الإعدادات من everix.py ─────────────────────────────
try:
    from everix import (
        ACCOUNT_BASE_NAME,
        ACCOUNT_COUNT,
        REGION,
        FIXED_PASSWORD,
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID,
    )
except ImportError as e:
    print(f"[ERROR] تعذّر تحميل everix.py: {e}")
    raise SystemExit(1)

# ── تحميل المحرك الأصلي ───────────────────────────────────────
from termux_guest_gen import (
    load_accounts,
    load_proxies,
    resolve_accounts_file,
    find_next_superscript_number,
    to_superscript,
    format_nickname,
    generate_gohar_branded_password,
    create_complete_guest_account,
)

# ─────────────────────────────────────────────────────────────
# دوال التيليجرام
# ─────────────────────────────────────────────────────────────

TG_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def tg_send(text: str, silent: bool = False) -> bool:
    """يرسل رسالة نصية للبوت، يطبع النتيجة في التيرمينال."""
    url = f"{TG_API}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_notification": silent,
    }
    try:
        r = req_lib.post(url, json=payload, timeout=10)
        data = r.json()
        if data.get("ok"):
            print(f"  [TG ✓] رسالة أُرسلت للبوت (message_id={data['result']['message_id']})")
            return True
        else:
            print(f"  [TG ✗] خطأ من تيليجرام: {data.get('description', 'unknown')}")
            return False
    except Exception as ex:
        print(f"  [TG ✗] فشل الاتصال بالبوت: {ex}")
        return False


def format_single_account_msg(acc: dict, index: int, total: int) -> str:
    """يبني رسالة حساب واحد."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"🎮 <b>حساب جديد [{index}/{total}]</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>الاسم     :</b> <code>{acc['nickname']}</code>\n"
        f"🆔 <b>UID      :</b> <code>{acc['uid']}</code>\n"
        f"🎯 <b>Game UID :</b> <code>{acc['game_uid']}</code>\n"
        f"🔑 <b>الباسورد :</b> <code>{acc['password']}</code>\n"
        f"🌍 <b>المنطقة  :</b> <code>{acc['region']}</code>\n"
        f"🕐 <b>الوقت    :</b> <code>{ts}</code>\n"
    )


def format_summary_msg(accounts: list, success: int, total: int) -> str:
    """يبني رسالة الملخص النهائي بكل الحسابات."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"✅ <b>انتهت عملية الإنشاء</b>\n",
        f"📊 نجح: <b>{success}/{total}</b> حساب\n",
        f"⏰ <code>{ts}</code>\n",
        "━━━━━━━━━━━━━━━━━━━━━━\n",
    ]
    for i, acc in enumerate(accounts, 1):
        lines.append(
            f"<b>[{i}]</b> {acc['nickname']} | "
            f"UID: <code>{acc['uid']}</code> | "
            f"Pass: <code>{acc['password']}</code>\n"
        )
    return "".join(lines)


# ─────────────────────────────────────────────────────────────
# الدالة الرئيسية
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("          EVERIX - Free Fire Guest Account Generator")
    print("=" * 65)
    print(f"  اسم الحسابات  : {ACCOUNT_BASE_NAME}")
    print(f"  عدد الحسابات  : {ACCOUNT_COUNT}")
    print(f"  المنطقة       : {REGION}")
    print(f"  كلمة المرور   : {'ثابتة' if FIXED_PASSWORD else 'عشوائية تلقائياً'}")
    print(f"  التيليجرام    : {'مفعّل' if TELEGRAM_BOT_TOKEN else 'معطّل'}")
    print("=" * 65)

    # تحميل البيانات الحالية
    accounts_db  = load_accounts()
    proxies      = load_proxies()

    print(f"  قاعدة البيانات : {len(accounts_db)} حساب محفوظ في {resolve_accounts_file()}")
    if proxies:
        print(f"  البروكسيات    : {len(proxies)} بروكسي محمّل")
    else:
        print("  البروكسيات    : لا توجد (اتصال مباشر)")
    print()

    # تحديد بداية الترقيم
    start_num = find_next_superscript_number(accounts_db, ACCOUNT_BASE_NAME)
    print(f"  الترقيم يبدأ من: {ACCOUNT_BASE_NAME}{to_superscript(start_num)}")
    print()

    # إعلام تيليجرام ببدء العملية
    tg_send(
        f"🚀 <b>بدأت عملية إنشاء الحسابات</b>\n"
        f"📝 الاسم: <code>{ACCOUNT_BASE_NAME}</code>\n"
        f"🔢 العدد: <b>{ACCOUNT_COUNT}</b>\n"
        f"🌍 المنطقة: <b>{REGION}</b>"
    )

    created_this_run = []
    success_count    = 0

    print("=" * 65)
    print(f"  بدء الإنشاء - {ACCOUNT_COUNT} حساب...")
    print("=" * 65)

    for i in range(ACCOUNT_COUNT):
        current_num = start_num + i
        nick = format_nickname(ACCOUNT_BASE_NAME, current_num)
        pwd  = FIXED_PASSWORD if FIXED_PASSWORD else generate_gohar_branded_password()

        # اختيار البروكسي
        current_proxy  = None
        proxy_display  = "Direct Network"
        if proxies:
            current_proxy = proxies[i % len(proxies)]
            proxy_display = current_proxy.split("@")[-1] if "@" in current_proxy else current_proxy

        print(f"\n[{i+1}/{ACCOUNT_COUNT}] جاري إنشاء: {nick}  |  بروكسي: {proxy_display}")

        acc = create_complete_guest_account(
            nickname=nick,
            password=pwd,
            region=REGION,
            proxy=current_proxy,
        )

        if acc:
            success_count += 1
            created_this_run.append(acc)

            print(f"  [✓ نجح]  الاسم: {acc['nickname']}")
            print(f"           UID:      {acc['uid']}")
            print(f"           Game UID: {acc['game_uid']}")
            print(f"           Password: {acc['password']}")

            # إرسال الحساب فوراً للتيليجرام
            tg_send(format_single_account_msg(acc, i + 1, ACCOUNT_COUNT))
        else:
            print(f"  [✗ فشل]  Garena رفضت التسجيل أو rate-limit. الحساب {i+1} تجاوزناه.")

            tg_send(
                f"⚠️ <b>فشل الحساب [{i+1}/{ACCOUNT_COUNT}]</b>\n"
                f"الاسم المحاول: <code>{nick}</code>\n"
                f"السبب المحتمل: rate-limit أو مشكلة شبكة"
            )

        # تأخير بسيط بين الحسابات
        if i < ACCOUNT_COUNT - 1:
            time.sleep(0.5)

    # ─── ملخص نهائي ───────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"  اكتملت العملية!  نجح: {success_count}/{ACCOUNT_COUNT}")
    print(f"  الملف المحفوظ  : {resolve_accounts_file()}")
    print("=" * 65)

    # إرسال ملخص نهائي للتيليجرام (كل الحسابات دفعة واحدة)
    if created_this_run:
        print(f"\n  [TG] جاري إرسال الملخص النهائي ({success_count} حساب دفعة واحدة)...")
        summary = format_summary_msg(created_this_run, success_count, ACCOUNT_COUNT)
        tg_send(summary)
    else:
        tg_send(
            f"❌ <b>فشلت جميع المحاولات</b>\n"
            f"0/{ACCOUNT_COUNT} حساب تم إنشاؤه.\n"
            f"تحقق من الشبكة أو البروكسيات."
        )

    print("\n  [✓] انتهى البرنامج.")


if __name__ == "__main__":
    main()
