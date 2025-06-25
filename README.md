# dsv-daisy-booker
## About
A discord bot capable of booking student group rooms and staff rooms via Daisy.
![Demo usage with the discord bot](images/Screenshot%202024-05-02%20084614.png)

## Usage
### Configuration
Configured via the following environment variables:
- SECOND_USER_ID - Student ID of the second user to be put on all bookable group room bookings
- SECOND_USER_SEARCH_TERM - search term that you used to find the second user in Daisy
- SU_USERNAME - your Stockholm University username and password, used to generate session tokens for Daisy
- SU_PASSWORD - your Stockholm University username and password, used to generate session tokens for Daisy
- SU_STAFF - if the user is a staff user in Daisy, optional, boolean as an integer 0 or 1
- CF_API_BASE_URL - see cloudflare documentation, used for LLM api calls
- CF_BEARER_TOKEN - see cloudflare documentation, used for LLM api calls
- DISCORD_OWNER_ID - your discord user id, the bot will only respond to you
- DISCORD_TOKEN - see discord documentation, used to run the discord bot
### Running
Build the docker image:
```bash
docker build -t dsv-daisy-booker .
```
and run it with the environment variables set:
```bash
docker run
    -e SECOND_USER_ID=
    ...
    -e DISCORD_TOKEN=
    dsv-daisy-booker
```
or with a .env file:
```bash
docker run --env-file .env dsv-daisy-booker
```

## Disclaimer
This project is not affiliated with Stockholm University or Daisy in any way. It is a personal project and should be used responsibly. Provided as is, no guarantees are made about its functionality or security.

## License
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE.md) file for more information.
