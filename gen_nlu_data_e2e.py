'''
  根据domain.yml文件来自动生成
  1. nlu.json训练数据
  2. stories.md话术文件（TODO）
  3. actions.py文件处理词槽缺失
'''

import yaml

template_domain = yaml.load(open('./template_data/DomainTemplate.yml'),Loader=yaml.FullLoader)
chatette_file = open('./Chatette-master/examples/book_meeting.chatette','w')
slots = template_domain['slots']
intents = template_domain['intents']
entities = template_domain['entities']
templates = template_domain['templates']
actions = template_domain['actions']

print(intents[7:])
print(entities)
print()
for intent in intents[7:]:
    chatette_file.write("@[%s]('training': '100', 'testing': '100')\n"%intent)
    chatette_file.write("\t帮我@[%s]@[%s]@[%s]\n"%(entities[0],entities[1],entities[2]))
    for entitie in entities:
        chatette_file.write("@[%s]\n"%entitie)
        chatette_file.write("")
