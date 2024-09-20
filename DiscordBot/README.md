# Discord Bot

The objective of the tooling in this directory will be to evolve into a Discord bot which will be able
to monitor and control a Satisfactory server, and provide an interface with which to do so to a specified
Guild.

The Bot should do the following:
 - Obtain its configuration through its environment or a `.env` file
 - Relay server status (Offline, idle/paused, online) and number of players (if any)
   - By means of setting its name or the name of a channel in near-real-time (realisticly 5-10 second old data)
 - Allow users granted a specific role to issue commands to be relayed through the API, including:
   - Shutdown the server
   - Show detailed server status
   - Set options such as auto-pause and other items accessible though the API
   - List available saved games
   - Load a saved game
   - Start a new game session
 - Commands should be issued through slash commands (e. g. `/sfbot shutdown`)
