# emptyepsilon-docker

Dockerfile for running emptyepsilon headless with Discord bot.

## Setup

1. Get the `Dockerfile` from this repository.
2. Build the image with Docker.
3. Create a file `bot-env` with the following content:

        DISCORD_API_TOKEN=cat_on_keyboard_string
        DISCORD_BOT_OWNER=discord_user_id
        PRIVILEGED_ROLE=discord_role

4. Start the server with `docker run -p 35666:35666 --env-file bot-env IMAGE`

## Usage

The bot controls the server. Type !help, !hilfe or !h in Discord to list the commands.

## FAQ

**It's speaking german!**  
Yes, it's not multilingual at the moment. Sorry.

**I get an error `TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'`**  
`DISCORD_BOT_OWNER` may not be empty or missing. This will be fixed in a future version.

**How do i get an api token?**  
https://discordpy.readthedocs.io/en/stable/discord.html

**Can I change the version of EmptyEpsilon?**  
Yes, just change the following lines at the top of `Dockerfile`:

        ENV VERSION_MAJOR "2021"
        ENV VERSION_MINOR "03"
        ENV VERSION_PATCH "31"
