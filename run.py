# -*- coding: UTF-8 -*-
import argparse

import requests
from requests.sessions import Session
from terminaltables import GithubFlavoredMarkdownTable


class JumpClient():
    BASIC_URL = 'https://switch.jumpvg.com'

    def __init__(self, cookie):
        self.cookie = cookie
        self.session = Session()
        self.lottery_dict = {}
        self.headers = {'Host': 'switch.jumpvg.com',
                        'authentication': cookie}

    def login_app(self):
        self.headers = {'Host': 'switch.jumpvg.com',
                        'Cookie': f'qiyeToken={self.cookie}'}
        ret = self.session.post(f'{JumpClient.BASIC_URL}/switch/youzan/login', headers=self.headers,
                                data='https://switch.jumpvg.com/switch/youzan/login').json()
        if ret['success'] == 0:
            return True
        return False

    def list_all_lottery(self):
        ret = self.session.get(f'{JumpClient.BASIC_URL}/jump/lottery/list?type=0&offset=0&limit=1000000').json()
        if ret['success']:
            for lottery in ret['data']:
                self.lottery_dict[lottery['lotteryId']] = {'name': lottery['rewardName'],
                                                           'drawingTime': lottery['drawingTime'],
                                                           'joinCount': lottery['joinNum'],
                                                           'rewardNum': lottery['rewardNum']}

    def check_lottery_join_status(self, lottery_id):
        ret = self.session.get(f'{JumpClient.BASIC_URL}/jump/lottery/detail?lotteryId={lottery_id}',
                               headers=self.headers).json()
        if ret['data']['isJoinLottery'] == 1:
            return True
        return False

    def check_lottery_count_status(self, lottery_id):
        ret = self.session.get(f'{JumpClient.BASIC_URL}/jump/lottery/login/info?lotteryId={lottery_id}',
                               headers=self.headers).json()
        if ret['success']:
            data = ret['data']
            node_list = [int(item) for item in data['node'].split(',')]
            day_list = [int(item) for item in data['day'].split(',')]
            current_day = data['currDay']
            if data['already'] is not None:
                already_day = [int(item) for item in data['already'].split(',')]
            else:
                already_day = []
            lottery_day_node = {'totalDays': data['totalDay'],
                                'day_list': day_list,
                                'node_list': node_list,
                                'current_day': current_day,
                                'already_day': already_day,
                                'lottery_count': data['lotteryCount'],
                                'max_lottery_count': sum(node_list) + 100}
            self.lottery_dict[lottery_id]['lottery_detail'] = lottery_day_node
        return self.lottery_dict[lottery_id]['lottery_detail']

    def get_lottery(self, lottery_id, lottery_type):
        ret = self.session.get(
            f'{JumpClient.BASIC_URL}/jump/lottery/join/record?type={lottery_type}&lotteryId={lottery_id}',
            headers=self.headers).json()
        if ret['success']:
            return True
        return False

    def get_flow_status(self):
        ret = self.session.get(
            f'{JumpClient.BASIC_URL}/jump/flow/info',
            headers=self.headers).json()
        return ret['data']

    def get_nday_flow(self, day=1):
        ret = self.session.get(f'{JumpClient.BASIC_URL}/jump/flow/add?type={day}',
                               headers=self.headers).json()
        if ret['success']:
            return True
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='test the argparse package')
    parser.add_argument('--cookie', '-c', help='input the cookie')
    parser.add_argument('--serverKey', '-s', help='input the serverKey')
    args = parser.parse_args()
    params = vars(args)
    cookie = params['cookie']
    serverKey = params['serverKey']
    client = JumpClient(cookie)
    # print('登录系统:', end='')
    # if client.login_app():
    #     print('登录成功')
    # else:
    #     print('登录失败')
    #     exit(1)
    print('获取当前所有抽奖...')
    client.list_all_lottery()
    for lottery_id, detail in client.lottery_dict.items():
        print(f'检查[{detail["name"]}--{lottery_id}]参与情况:', end='')
        join_status = client.check_lottery_join_status(lottery_id)
        if join_status:
            print(f'已参与')
            print(f'检查[{detail["name"]}--{lottery_id}]奖票领取情况:', end='')
            client.check_lottery_count_status(lottery_id)
            lottery_detail = detail['lottery_detail']
            print(f'已登录{lottery_detail["current_day"]}.', end='')
            for idx, day in enumerate(lottery_detail['day_list']):
                if lottery_detail['current_day'] >= day:
                    if day not in lottery_detail['already_day']:
                        print(f'补领第{day}天的奖励。', end='')
                        client.get_lottery(lottery_id, idx + 2)
            print('')
        else:
            print(f'未参与，现在参加')
            client.get_lottery(lottery_id, 1)

    for lottery_id, detail in client.lottery_dict.items():
        print(f'刷新[{detail["name"]}--{lottery_id}]参与情况')
        client.check_lottery_count_status(lottery_id)

    print('开始执行流量领取...')
    print('获取流量获取周期天数...')
    flow_data = client.get_flow_status()
    day_kv = {1: False, 3: False, 4: False}
    for day, _ in day_kv.items():
        print(f'领取{day}流量: ', end='')
        if client.get_nday_flow(day):
            print('success')
            day_kv[day] = True
        else:
            print('fail')

    table_lottery_data = [['序号', 'id号', '名称', '奖品数量', '开奖时间', '参与人数', '参与天数', '奖票数量', '最大可得奖票']]
    for idx, lottery_id in enumerate(client.lottery_dict):
        detail = client.lottery_dict[lottery_id]
        table_lottery_data.append(
            [idx + 1, lottery_id, detail['name'].split('x')[0], detail['rewardNum'], detail['drawingTime'],
             detail['joinCount'],
             detail['lottery_detail']['current_day'], detail['lottery_detail']['lottery_count'],
             detail['lottery_detail']['max_lottery_count']])
    table_flow_data = [['登录天数', '当日流量领取', '3日流量领取', '4日流量领取', '总流量'],
                       [flow_data['loginDay'], True if flow_data['isLoginReceive'] == 2 else False, day_kv[3],
                        day_kv[4], f'{flow_data["flowNumber"]}MB']]

    table_lottery = GithubFlavoredMarkdownTable(table_lottery_data)
    table_flow = GithubFlavoredMarkdownTable(table_flow_data)
    print(table_lottery.table)
    print(table_flow.table)
    if serverKey:
        print(f'执行推送')
        requests.post(f'https://sctapi.ftqq.com/{serverKey}.send',
                      data={'title': 'JumpAutoJoin状态',
                            'desp': f'{table_lottery.table}\n\n{table_flow.table}'})
