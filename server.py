from fastapi import FastAPI
import random
import uvicorn


CARD_NAMES = [
    'Штурвал',
    'Нож',
    'Пистолет',
    'Компас',
    'Свеча',
    'Попугай',
    'Сундук',
    'Ключ',
    'Ром',
    'Якорь',
]


class Game:
    def __init__(self, max_players):
        self.unique_id = str(random.randint(100000, 999999))
        self.is_started = False
        self.max_players = max_players
        self.players_list = []
        self.whose_move = None
        self.card_decks = {
            'treasure': [],
            'raid': [],
            'drop': []
        }
        for name in CARD_NAMES:
            for i in range(6):
                if i == 0:
                    deck = 'drop'
                else:
                    deck = 'treasure'
                if name == 'Попугай':
                    self.card_decks[deck].append(name + ' ' + str(i+4))
                else:
                    self.card_decks[deck].append(name + ' ' + str(i+2))

    def enlist_player(self, player_id):
        if len(self.players_list) < self.max_players:
            self.players_list.append(player_id)
            if len(self.players_list) == self.max_players:
                self.get_started()
            return True
        else:
            self.get_started()
            return False

    def get_started(self):
        self.is_started = True
        for player_id in self.players_list:
            self.card_decks[player_id] = []
        self.whose_move = self.players_list[0]

    def get_state(self):
        return {
            'cards': self.card_decks,
            'whose_move': self.whose_move,
            'is_started': self.is_started,
        }

    def transit_move_to_next_player(self):
        if self.players_list.index(self.whose_move) == self.max_players - 1:
            self.whose_move = self.players_list[0]
        else:
            self.whose_move = self.players_list[self.players_list.index(self.whose_move)+1]

    def make_move(self, player_id, action):
        if player_id != self.whose_move:
            return False
        if action == 'do_raid':
            # игрок тянет карту из колоды в рейд
            # перемешать колоду
            random.shuffle(self.card_decks['treasure'])
            # вытащить одну карту
            pulled_card = self.card_decks['treasure'].pop()
            # выцепить имя карты
            pulled_card_name = pulled_card.split[0]
            # пройтись по картам в рейде и сравнить
            for card in self.card_decks['raid']:
                raided_card_name = card.split[0]
                if pulled_card_name == raided_card_name:
                    # вытащена повторная карта, рейд уходит в сброс
                    for i in range(len(self.card_decks['raid'])):
                        self.card_decks['drop'].append(self.card_decks['raid'].pop())
                    # смена хода
                    self.transit_move_to_next_player()
                    return 'raid_lost'
            else:
                return True
        if action == 'end_raid':
            # пройтись по каждой карте в рейде
            for i in range(len(self.card_decks['raid'])):
                # взять карту из рейда и получить ее имя
                raided_card = self.card_decks['raid'].pop()
                raided_card_name = raided_card.split()[0]
                # переместить карту в список к игроку
                self.card_decks['player_id'].append(raided_card)
            # смена хода
            self.transit_move_to_next_player()
            return True


app = FastAPI()

# словарь с ключами - id игр и соответствующими значениями - объектами класса Game
GAMES = {}

# словарь с ключами - id игроков и соответствующими значениями - их именами
PLAYERS = {}


@app.get('/')
def index():
    return {
        'status': 'ok',
        'result': {
            'message': 'Hello to the Treasure Island client!'
        }
    }


@app.post('/register/')
def register(player_name: str):
    while True:
        player_id = str(random.randint(10000, 99999))
        if player_id not in PLAYERS:
            break
    PLAYERS[player_id] = player_name
    return {
        'status': 'ok',
        'result': player_id
    }


@app.get('/get_games/')
def get_games():
    games_dicts_list = []
    for game in GAMES:
        if not GAMES[game].is_started:
            games_dicts_list.append({
                'id': GAMES[game].unique_id,
                'players': '{}/{}'.format(len(GAMES[game].players_list), GAMES[game].max_players)
            })
    return {
        'status': 'ok',
        'result': games_dicts_list
    }


@app.post('/create_game/')
def create_game(amount_of_players: int = 2):
    if amount_of_players < 2 or amount_of_players > 4:
        return {
            'status': 'fail',
            'error': 'Wrong players amount while creating game'
        }
    new_game = Game(amount_of_players)
    GAMES[new_game.unique_id] = new_game
    return {
        'status': 'ok',
        'result': new_game.unique_id
    }


@app.post('/enlist_for_game/')
def enlist_for_a_game(game_id: str, player_id: str):
    if GAMES[game_id].enlist_player(player_id):
        return {
            'status': 'ok',
            'result': 'ok'
        }
    else:
        return {
            'status': 'fail',
            'result': 'Enough players already'
        }


@app.get('/game_state')
def get_game_state(game_id: str):
    inspected_game = GAMES.get(game_id, False)
    if not inspected_game == False:
        return {
            'status': 'ok',
            'result': inspected_game.get_state()
        }
    else:
        return {
            'status': 'fail',
            'error': 'No game with this ID'
        }


@app.post('/make_move')
def make_move(game_id, player_id, action):
    game_in_action: Game = GAMES.get('game_id')
    game_in_action.make_move(player_id, action)
    return game_in_action.get_state()


if __name__ == '__main__':
    uvicorn.run(
        'server:app',
        host='127.0.0.1',
        port=5001,
        reload=True
    )
