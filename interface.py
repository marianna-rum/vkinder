# импорты
from datetime import datetime 

from dateutil.relativedelta import relativedelta

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import community_token, access_token
from core import VkTools

class BotInterface():

    param_questions = {
        'name': 'Как вас зовут?',
        'bdate': 'Сколько Вам лет?',
        'home_town': 'Из какого Вы города?',
        'relation': 'Вы состоите в отношениях?'
        }

    def __init__(self,community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(access_token)
        self.params = None
        self.missing_param = None

    def validate_params(self,user_answer=None):
        #Результаты проверки неизвестны
        if self.missing_param is None:
             for param_name, param_value in self.params.items():
                  if param_value is None:
                       self.missing_param = param_name
                       self.message_send(int(self.params['id']), self.param_questions[self.missing_param])
                       return
             self.missing_param = None
        #Есть недостающие параметры пользователя
        else:
            if(self.missing_param=='bdate'):
                age = int(user_answer)
                bdate = datetime.now() - relativedelta(years=age)
                self.params['bdate'] = bdate.strftime("%d.%m.%Y")
                self.validate_params()
 

        #if self.params['bdate'] is None:
        #    self.message_send(int(self.params['id']),'А сколько Вам лет?' )    
    
    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )
        
    def execute_command(self,uid, command):
        if command == 'привет':
            self.params = self.api.get_profile_info(uid)
            self.message_send(uid, f'здравствуй {self.params["name"]}')
            self.validate_params()
        elif command == 'пока':
            self.message_send(uid, 'пока')
        else:
            self.message_send(uid, 'команда не опознана')


        
    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if self.missing_param is None:
                    self.execute_command(event.user_id,command)
                else:
                    self.validate_params(command)

                


if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()

            
