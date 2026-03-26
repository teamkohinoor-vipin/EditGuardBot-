# Telegram Edit Guard Bot

A powerful Telegram bot that prevents message editing abuse in groups. Automatically deletes edited messages from unauthorized users, provides authorization system, admin controls, and analytics.

## Features

- **Anti-Edit** – Automatically delete edited messages from unauthorized users.
- **Authorization** – Grant/revoke edit permission using `/approve` and `/unapprove`.
- **Admin Controls** – Silent mode, custom warning messages, and settings view.
- **User Status** – Check your own authorization status with `/mystatus`.
- **Analytics** – Bot owner can view total users, groups, and list all groups with invite links.
- **Welcome Message** – Beautiful start message with inline buttons: Help, Add to Group, Developer, Support Chat.
- **JSON Database** – Lightweight, no external database required.

## Commands

### User Commands
- `/start` – Register and see welcome message.
- `/help` – Show all commands.
- `/mystatus` – Check if you're authorized to edit in the current group.

### Admin Commands (Group Admins only)
- `/approve` or `/auth` – Allow a user to edit messages (reply or user ID).
- `/unapprove` or `/unauth` – Revoke edit permission.
- `/authusers` – List all authorized users.
- `/setwarn` – Set a custom warning message.
- `/silent on/off` – Toggle warning messages.
- `/settings` – View current group settings.

### Owner Commands (Private chat)
- `/stats` – Show total users and groups.
- `/groups` – List all groups the bot is in with links.

## Deployment

### 1. Prerequisites
- Python 3.10 or higher
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- API ID and Hash from [my.telegram.org](https://my.telegram.org)

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/edit-guard-bot.git
cd edit-guard-bot
