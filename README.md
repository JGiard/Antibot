# Antibot

## Introduction

This is a python framework to create slack bots.

It abstract most of the boilerplate code to interact with slack and encapsulate slack json data in nice native classes.

## How to install
Install Antibot
```bash
pip install antibot
```

Install plugins in the same python environment. Antibot will detect them during startup.

## How to run

You need to create a new app on https://api.slack.com/apps.
1. Go to OAuth & Permissions, set scopes (at least),
   * users:read
   * users:read.email
   * files:write

   and install OAuth Tokens
2. Launch Antibot with the following environment variables:
   * SLACK_BOT_USER_TOKEN : can be found under `Bot User OAuth Access Token` in `OAuth & Permissions` page
   * SIGNING_SECRET : can be found in the `Basic Information` page
   * WS_API_KEY : is a random secret of you choice to call non-slack related api on your bot
   * MONGO_URI : Mongo connection string to an accessible mongo instance
   * DEV=true while in development
3. Make Antibot accessible with a public URL (in development you can use http://localhost.run/, but you will need to update URLs regularly)
4. Enable `Interactivity` in `Interactivity & Shortcuts`, and set URL to `https://antibot-public-url/action`
5. Create command in `Slash Commands`, and set URL to `https://antibot-public-url/your/command` (installed commands are listed during Antibot startup)


## How to create a plugin

Use [cookiecutter](https://github.com/cookiecutter/cookiecutter) on https://github.com/JGiard/Antibot-plugins-template

## Coding

There is lot of stuff you can do, check the other projects for examples.

Use `@command("/myplugin/route")` to react to slash command (don't forget to create the correspond command in slack).

Always use the block api from `antibot.slack.messages` when creating messages.

Use `@block_action(action_id="...")` to react to interactive components on messages.

Use `@ws("/myplugin/route)` to create a raw endpoint.
