import aiohttp
import asyncio
import sys
import time
import uuid


class RequestSession(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}/"

    async def start_new_game(self, game_name):
        return await self.make_request(f"start?name={game_name}")

    async def get_game_status(self, game_id):
        return await self.make_request(f"status?game={game_id}")

    async def play_game(self, game_id, x, y, player):
        return await self.make_request(f"play?game={game_id}&x={x}&y={y}&player={player}")

    async def list_games(self):
        return await self.make_request("list")

    async def make_request(self, path):
        url = self.base_url + path

        async with aiohttp.ClientSession(raise_for_status=True) as client_session:
            async with client_session.get(url=url, raise_for_status=True) as resp:
                return await resp.json()  # TODO: try 4xx


if len(sys.argv) != 3:
    sys.exit("First argument must be host, second port!")

host = sys.argv[1]
port = int(sys.argv[2])
if port < 1 or port > 65535:
    sys.exit("Invalid port!")

rq_session = RequestSession(host, port)

PLAYERS_MAPPING = {0: "-", 1: "x", 2: "o"}


class Game(object):
    def __init__(self, game_id=None, game_name=None, status=None):
        self.id = game_id
        self.name = game_name
        self.status = status
        self.board = None
        self.next_player = None
        self.winner = None

    def load_from_dict(self, game_dict):
        self.id = game_dict["id"]
        self.name = game_dict.get("name") or self._generate_random_name()

    @staticmethod
    def _generate_random_name():
        return "game_" + str(uuid.uuid4())

    def print_info(self):
        print(f'{self.id} {self.name}')

    def refresh_status(self, srv_status):
        if "board" in srv_status:
            self.board = srv_status["board"]
            self.next_player = int(srv_status["next"])
            sum_board = sum([item for sublist in self.board for item in sublist])
            if sum_board == 0:
                self.status = "new"
            else:
                self.status = "playing"
        if "winner" in srv_status:
            self.status = "end"
            self.winner = int(srv_status["winner"])

    def print_board(self):
        output = ""
        for row in self.board:
            for i in row:
                output += PLAYERS_MAPPING[i]
            output += "\n"
        print(output[:-1])


class GameManager(object):
    def __init__(self, games):
        self.all_games = self._load_all_games(games)
        self.games_to_join = []
        self.current_game = None
        self.player = 0

    @staticmethod
    def _load_all_games(games):
        all_games = []
        for game_dict in games:
            g = Game()
            g.load_from_dict(game_dict)
            all_games.append(g)

        return all_games

    def print_games_to_join(self):
        print("List of games to join: ")
        for g in self.all_games:
            if g.status == "new":
                self.games_to_join.append(g)
                g.print_info()

    def add_game(self, game_dict):
        game = Game(game_id=game_dict["id"], game_name=game_dict.get("name"), status="new")
        self.all_games.append(game)
        self.games_to_join.append(game)
        self.current_game = game
        self.player = 1
        return self.current_game

    def join_game(self, game):
        self.current_game = game
        self.player = 2

    def get_game_by_id(self, gid):
        return [g for g in self.games_to_join if g.id == gid][0]


async def cli_ui():
    game_list = await rq_session.list_games()
    games = GameManager(game_list)
    for game in games.all_games:
        game_server_status = await rq_session.get_game_status(game.id)
        game.refresh_status(game_server_status)
    games.print_games_to_join()

    if games.all_games:
        input_msg = 'You can type "[game_id]" to join game or type "new [game_name]" to start a new game: '
    else:
        input_msg = 'Type "new [game_name]" to start a new game: '

    while True:
        player_choice = input(input_msg).strip()
        try:
            if player_choice.startswith("new"):
                # start new game with player 1
                chosen_game_name = player_choice.lstrip("new").strip()
                new_game = await rq_session.start_new_game(chosen_game_name)
                game = games.add_game(new_game)
                game_server_status = await rq_session.get_game_status(game.id)
                game.refresh_status(game_server_status)
                break
            elif int(player_choice):
                # join player 2 to game with inputted game_id
                game = games.get_game_by_id(int(player_choice))
                game_server_status = await rq_session.get_game_status(game.id)
                game.refresh_status(game_server_status)
                if game.status == "new":
                    games.join_game(game)
                break
            else:
                raise ValueError("Invalid input")
        except (TypeError, ValueError, IndexError):
            print('Wrong input! Choose valid game_id from the list of start new game with "new [name]" command!')

    game = games.current_game
    waiting = False

    while True:
        if game.status == "end":
            if game.winner == 0:
                print("draw")
            elif game.winner == games.player:
                print("you win")
            else:
                print("you lose")
            break

        if games.player == game.next_player:
            waiting = False
            game.print_board()

            while True:
                play = input("your turn ({0}): ".format(PLAYERS_MAPPING[games.player]))
                try:
                    x, y = play.strip().split()
                    res = await rq_session.play_game(game.id, x, y, games.player)
                    if res["status"] == "ok":
                        break
                    print("invalid input " + res["message"])
                except Exception:
                    print("invalid input")
        else:
            if not waiting:
                print("waiting for the other player")
                waiting = True
            time.sleep(1)

        game_server_status = await rq_session.get_game_status(game.id)
        game.refresh_status(game_server_status)


def run_game():
    loop = asyncio.get_event_loop()
    loop.create_task(cli_ui())
    loop.run_forever()


if __name__ == '__main__':
    run_game()
