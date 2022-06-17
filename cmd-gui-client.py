import requests
import sys
from pprint import pformat, pprint
import pyautogui
import time


if __name__ == '__main__':
    TEST_MODE = False
    session = requests.Session()
    if TEST_MODE:
        username = 'TestUserName'
        server_url = 'http://127.0.0.1:5001'
    else:
        username = pyautogui.prompt('Введите ник')
        server_url = pyautogui.prompt('Введите URL сервера')

    client_id = session.post(server_url + '/register', params={'player_name': username}).json()['result']

    game_chosen = False
    while not game_chosen:
        # получить список игр
        response = session.get(server_url + '/get_games').json()
        if response['status'] == 'ok':
            games = response['result']
        else:
            pyautogui.alert('Ошибка получения списка игр. {}'.format(pformat(response)))
            sys.exit()
        action = ''
        if len(games) > 0:
            buttons_with_games_ids = []
            for i in games:
                buttons_with_games_ids.append(i['id']+' '+i['players'])
            buttons_with_games_ids.append('+')
            action = pyautogui.confirm(
                text='Найдено игр: {}'.format(len(games)),
                buttons=buttons_with_games_ids
            )
            if action == '+':
                # создать новую, несмотря на существующие
                amount_of_players = pyautogui.confirm(
                    text='Сколько игроков?',
                    buttons=[2, 3, 4]
                )
                response = session.post(server_url + '/create_game',
                                        params={'amount_of_players': amount_of_players}).json()
            else:
                # получен id желаемой игры
                game_chosen = action.split()[0]
        else:
            # игр нет, создать новую
            amount_of_players = pyautogui.confirm(
                text='Не найдено игр, создаю новую. На сколько игроков?',
                buttons=[2, 3, 4]
            )
            response = session.post(server_url + '/create_game', params={'amount_of_players': amount_of_players})
    response = session.post(server_url + '/enlist_for_game', params={'game_id': game_chosen, 'player_id': client_id})
    pyautogui.alert('Вы зашли в игру. Нажмите ОК для ожидания старта.')
    game_started = False
    while not game_started:
        time.sleep(1)
        response = session.get(server_url + '/game_state', params={'game_id': game_chosen}).json()
        if response['result']['is_started']:
            game_started = True
    pyautogui.alert('Игра началась')
    game_cycle = True
    while game_cycle:
        time.sleep(1)
        game_state = session.get(server_url + '/game_state', params={'game_id': game_chosen}).json()['result']
        if game_state['whose_move'] == client_id:
            print('Ваш ход')
            actions = {'Взять карту': 'do_raid', 'Закончить рейд': 'end_raid'}
            action = pyautogui.confirm(text='Выберите действие', buttons=[_ for _ in actions])
            response = session.get(server_url + '/game_state', params={'game_id': game_chosen}).json()
        else:
            pass
