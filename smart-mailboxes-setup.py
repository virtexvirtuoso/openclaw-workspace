#!/usr/bin/env python3
"""
Smart Mailboxes Setup for Apple Mail (macOS Sequoia+)
Creates 7 Smart Mailboxes based on email cleanup categories.
Run this script while Mail.app is QUIT — it modifies the SyncedSmartMailboxes.plist directly.

Usage:
  1. Quit Mail.app
  2. Run: python3 smart-mailboxes-setup.py
  3. Open Mail.app — smart mailboxes will appear in sidebar

Existing smart mailboxes are preserved.
"""

import plistlib
import uuid
import os
import shutil
import subprocess

PLIST_PATH = os.path.expanduser("~/Library/Mail/V10/MailData/SyncedSmartMailboxes.plist")
WANTED_NAMES = [
    "Action Required",
    "Shopping & Orders",
    "Promos & Marketing",
    "Security & Alerts",
    "Social & Apps",
    "Fitness & Health",
    "Newsletters & Subs",
]


def crit(header, expression=None, qualifier=None, name=None, special_mailbox_type=None):
    c = {"CriterionUniqueId": str(uuid.uuid4()).upper()}
    c["Header"] = header
    if expression is not None:
        c["Expression"] = expression
    if qualifier is not None:
        c["Qualifier"] = qualifier
    if name is not None:
        c["Name"] = name
    if special_mailbox_type is not None:
        c["SpecialMailboxType"] = special_mailbox_type
    return c


def compound(name, criteria, all_must_satisfy=1):
    return {
        "CriterionUniqueId": str(uuid.uuid4()).upper(),
        "Header": "Compound",
        "Name": name,
        "AllCriteriaMustBeSatisfied": all_must_satisfy,
        "Criteria": criteria,
    }


def standard_exclusions():
    return [
        crit("NotInTrashMailbox", name="omit trash"),
        crit("NotInASpecialMailbox", name="omit sent", special_mailbox_type=3),
        crit("NotInJunkMailbox", name="omit junk"),
    ]


def make_smart_mailbox(name, criteria, all_must_satisfy=1):
    return {
        "IMAPMailboxAttributes": 17,
        "MailboxAllCriteriaMustBeSatisfied": all_must_satisfy,
        "MailboxChildren": [],
        "MailboxCriteria": standard_exclusions() + criteria,
        "MailboxID": str(uuid.uuid4()).upper(),
        "MailboxName": name,
        "MailboxType": 7,
    }


def build_mailboxes():
    """Define all 7 smart mailboxes with their filter criteria."""
    return [
        # 1. Action Required: Flagged + Unread
        make_smart_mailbox("Action Required", [
            crit("FlaggedStatus", expression="1", qualifier="IsEqualTo"),
            crit("ReadStatus", expression="0", qualifier="IsEqualTo"),
        ]),

        # 2. Shopping & Orders
        make_smart_mailbox("Shopping & Orders", [
            compound("user criteria", [
                crit("Subject", expression="order", qualifier="Contains"),
                crit("Subject", expression="shipping", qualifier="Contains"),
                crit("Subject", expression="tracking", qualifier="Contains"),
                crit("Subject", expression="receipt", qualifier="Contains"),
                crit("Subject", expression="confirmation", qualifier="Contains"),
                crit("Subject", expression="delivery", qualifier="Contains"),
                crit("From", expression="planetofthevapes", qualifier="Contains"),
                crit("From", expression="crossrope", qualifier="Contains"),
                crit("From", expression="jawzrsize", qualifier="Contains"),
                crit("From", expression="palmetto", qualifier="Contains"),
                crit("From", expression="yeezy", qualifier="Contains"),
                crit("From", expression="shop", qualifier="Contains"),
            ], all_must_satisfy=0),
        ]),

        # 3. Promos & Marketing
        make_smart_mailbox("Promos & Marketing", [
            compound("user criteria", [
                crit("Subject", expression="sale", qualifier="Contains"),
                crit("Subject", expression="% off", qualifier="Contains"),
                crit("Subject", expression="deal", qualifier="Contains"),
                crit("Subject", expression="coupon", qualifier="Contains"),
                crit("Subject", expression="promo code", qualifier="Contains"),
                crit("Subject", expression="limited time", qualifier="Contains"),
                crit("From", expression="walgreens", qualifier="Contains"),
                crit("From", expression="lexington", qualifier="Contains"),
                crit("From", expression="lone survivalist", qualifier="Contains"),
            ], all_must_satisfy=0),
        ]),

        # 4. Security & Alerts
        make_smart_mailbox("Security & Alerts", [
            compound("user criteria", [
                crit("From", expression="security", qualifier="Contains"),
                crit("From", expression="noreply", qualifier="Contains"),
                crit("From", expression="no-reply", qualifier="Contains"),
                crit("From", expression="alert", qualifier="Contains"),
                crit("Subject", expression="sign-in", qualifier="Contains"),
                crit("Subject", expression="verification code", qualifier="Contains"),
                crit("Subject", expression="unusual activity", qualifier="Contains"),
                crit("Subject", expression="password", qualifier="Contains"),
            ], all_must_satisfy=0),
        ]),

        # 5. Social & Apps
        make_smart_mailbox("Social & Apps", [
            compound("user criteria", [
                crit("From", expression="tiktok", qualifier="Contains"),
                crit("From", expression="instagram", qualifier="Contains"),
                crit("From", expression="facebook", qualifier="Contains"),
                crit("From", expression="twitter", qualifier="Contains"),
                crit("From", expression="linkedin", qualifier="Contains"),
                crit("From", expression="snapchat", qualifier="Contains"),
                crit("From", expression="meta", qualifier="Contains"),
            ], all_must_satisfy=0),
        ]),

        # 6. Fitness & Health
        make_smart_mailbox("Fitness & Health", [
            compound("user criteria", [
                crit("From", expression="crossrope", qualifier="Contains"),
                crit("From", expression="jawzrsize", qualifier="Contains"),
                crit("From", expression="gym", qualifier="Contains"),
                crit("From", expression="fitness", qualifier="Contains"),
                crit("From", expression="workout", qualifier="Contains"),
            ], all_must_satisfy=0),
        ]),

        # 7. Newsletters & Subscriptions
        make_smart_mailbox("Newsletters & Subs", [
            compound("user criteria", [
                crit("Subject", expression="unsubscribe", qualifier="Contains"),
                crit("From", expression="newsletter", qualifier="Contains"),
                crit("Subject", expression="newsletter", qualifier="Contains"),
                crit("From", expression="digest", qualifier="Contains"),
                crit("Subject", expression="weekly", qualifier="Contains"),
            ], all_must_satisfy=0),
        ]),
    ]


def main():
    # Check if Mail is running
    result = subprocess.run(["pgrep", "-x", "Mail"], capture_output=True)
    if result.returncode == 0:
        print("⚠️  Mail.app is running! Quit Mail first, then run this script.")
        print("   Run: osascript -e 'tell application \"Mail\" to quit'")
        return 1

    if not os.path.exists(PLIST_PATH):
        print(f"❌ plist not found at {PLIST_PATH}")
        print("   Make sure Apple Mail has been opened at least once on this Mac.")
        return 1

    # Backup
    backup_path = PLIST_PATH + ".backup"
    shutil.copy2(PLIST_PATH, backup_path)
    print(f"📦 Backed up to {backup_path}")

    # Load existing
    with open(PLIST_PATH, 'rb') as f:
        plist = plistlib.load(f)

    existing_names = [mb["MailboxName"].strip() for mb in plist]
    print(f"📋 Existing smart mailboxes: {existing_names}")

    # Build new mailboxes (skip duplicates)
    new_mailboxes = build_mailboxes()
    added = 0
    skipped = 0
    for mb in new_mailboxes:
        if mb["MailboxName"] in existing_names:
            print(f"   ⏭️  {mb['MailboxName']} — already exists, skipping")
            skipped += 1
        else:
            plist.append(mb)
            print(f"   ✅ {mb['MailboxName']} — added")
            added += 1

    if added == 0:
        print("\n👍 All smart mailboxes already exist — nothing to add!")
        return 0

    # Write
    with open(PLIST_PATH, 'wb') as f:
        plistlib.dump(plist, f)

    # Validate
    result = subprocess.run(["plutil", "-lint", PLIST_PATH], capture_output=True, text=True)
    if "OK" in result.stdout:
        print(f"\n✅ Done! Added {added} smart mailboxes ({skipped} skipped as duplicates)")
        print(f"   Open Mail.app to see them in the sidebar.")
    else:
        print(f"\n❌ Plist validation failed: {result.stdout}")
        print(f"   Restoring backup...")
        shutil.copy2(backup_path, PLIST_PATH)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())