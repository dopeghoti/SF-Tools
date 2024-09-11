The following are for the Dedicated server only *prior to* the 1.0 release.  The API documentation is included with
the Satisfactory game client.  As such, because it is tied to a Satisfactory purchase, I will not include it verbatim here
without permission from Coffee Stain.

The following is the only known details about how to converse with the Dedicated Server query port (by default, UDP/15777):

Request: 
- 1 byte message id: 0 for polling the server state
- 1 byte protocol version: currently 0
- 8 bytes user data that will just be echoed back to the client (eg client uses this for a timestamp so it can calculate roundtrip time).

Response: 
- 1 byte message id: the server responds with message id 1 to a request with message id 0
- 1 byte protocol version: currently 0
- 8 bytes client data: the 8 bytes from the request echoed
- 1 byte server state: 1 - Idle (no game loaded), 2 - currently loading or creating a game, 3 - currently in game
- 4 bytes server version
- 2 bytes beacon port

Only message IDs 0 (server state query) and 1 (server state reply) are currently known.
