from aiohttp import web
import sys


GAMES = {}


class TicTacToe(object):
    PLAYER_1 = 1
    PLAYER_2 = 2
    EMPTY = 0

    def __init__(self, name):
        self.board = [[self.EMPTY] * 3, [self.EMPTY] * 3, [self.EMPTY] * 3]
        self.winner = None
        self.next_player = 1
        self.name = name

    def place(self, player, x, y):
        """Place the symbol at the index."""

        if self.winner:
            raise RuntimeError('Player "{}" has already won the game.'.format(self.winner))

        if player not in {self.PLAYER_1, self.PLAYER_2}:
            raise ValueError('Player symbol must either be 1 or 2')

        if player != self.next_player:
            raise RuntimeError("It's not your turn. Player {} should play now!".format(self.next_player))

        try:
            if self.board[x][y] != self.EMPTY:
                raise RuntimeError('Spot {}, {} already has a piece by the opposite player.'.format(x, y))
        except IndexError:
            raise RuntimeError("Bad coordinates! x and y must be 0,1 or 2 integers")

        self.board[x][y] = player
        self.next_player = 2 if player == 1 else 1
        self._check_for_win()
        self._check_for_draw()

    @staticmethod
    def _check_line(iterable, player):
        """Check if an iterable of pieces were all placed by the same player."""
        return all(map(lambda piece: piece == player, iterable))

    def _check_for_win(self):
        """Check if a player has won."""
        for player in {self.PLAYER_1, self.PLAYER_2}:
            # 1. Check all rows
            for row in self.board:
                if self._check_line(row, player):
                    self.winner = player
                    return

            # 2. Check all columns
            for column in zip(*self.board):
                if self._check_line(column, player):
                    self.winner = player
                    return

            # 3. Check the two diagonals
            diagonals = [
                [self.board[0][0], self.board[1][1], self.board[2][2]],
                [self.board[0][2], self.board[1][1], self.board[2][0]],
            ]
            for diagonal in diagonals:
                if self._check_line(diagonal, player):
                    self.winner = player
                    return

    def _check_for_draw(self):
        if self.EMPTY not in set([item for sublist in self.board for item in sublist]):
            self.winner = 0


def generate_game_id():
    try:
        max_game_id = max(GAMES.keys())
        return max_game_id + 1
    except ValueError:
        return 1


async def start_handler(request):
    game_id = generate_game_id()
    name = request.rel_url.query.get("name", "")
    GAMES[game_id] = TicTacToe(name=name)

    res = {"id": game_id}

    return web.json_response(res)


async def status_handler(request):
    try:
        game_id = int(request.rel_url.query["game"])
    except (KeyError, ValueError):
        return web.HTTPBadRequest(text="specify valid game id, it must be an integer")

    try:
        game = GAMES[game_id]
    except KeyError:
        return web.HTTPNotFound(text="unknown game id")

    if game.winner is not None:
        res = {"winner": game.winner}
    else:
        res = {"board": game.board, "next": game.next_player}

    return web.json_response(res)


async def play_handler(request):
    try:
        game_id = int(request.rel_url.query["game"])
    except (KeyError, ValueError):
        return web.HTTPBadRequest(text="specify valid game id, it must be an integer")

    try:
        game = GAMES[game_id]
    except KeyError:
        return web.HTTPNotFound(text="unknown game id")

    try:
        player = int(request.rel_url.query["player"])
        if player not in {1, 2}:
            raise ValueError
    except (KeyError, ValueError):
        return web.HTTPBadRequest(text="specify valid player, it must be an integer - 1 or 2")

    try:
        x = int(request.rel_url.query["x"])
        y = int(request.rel_url.query["y"])
    except (KeyError, ValueError):
        return web.HTTPBadRequest(text="specify valid x and y coordinate, it must be an integer")

    try:
        game.place(player, x, y)
        res = {"status": "ok"}
    except (ValueError, RuntimeError) as msg:
        res = {
            "status": "bad",
            "message": str(msg),
        }

    return web.json_response(res)


async def list_handler(request):
    res = []
    for game_id, game in GAMES.items():
        res.append({"id": game_id, "name": game.name})

    return web.json_response(res)


async def test_handler(request):
    try:
        game_id = int(request.rel_url.query["game"])
    except (KeyError, ValueError):
        return web.HTTPBadRequest(text="specify valid game id, it must be an integer")

    try:
        game = GAMES[game_id]
    except KeyError:
        return web.HTTPNotFound(text="unknown game id")

    try:
        next_player = int(request.rel_url.query["next_player"])
        if next_player not in {1, 2}:
            raise ValueError
    except (KeyError, ValueError):
        return web.HTTPBadRequest(text="specify valid player, it must be an integer - 1 or 2")

    try:
        board_setup = request.rel_url.query["board_setup"]
        data_list = [int(x) for x in board_setup]
        game.board = [data_list[i:i + 3] for i in range(0, len(data_list), 3)]
        game.next_player = next_player
        res = {"status": "ok", "board": game.board, "next_player": game.next_player}
    except (ValueError, RuntimeError) as msg:
        res = {
            "status": "bad",
            "message": str(msg),
        }

    return web.json_response(res)


def run_app(port):
    app = web.Application()
    app.add_routes([web.get('/start', start_handler),
                    web.get('/status', status_handler),
                    web.get('/play', play_handler),
                    web.get('/list', list_handler),
                    web.get('/test_setup', test_handler)])
    web.run_app(app, port=port)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("First argument must be port!")

    my_port = int(sys.argv[1])
    if my_port < 1 or my_port > 65535:
        sys.exit("Invalid port!")
    run_app(my_port)
