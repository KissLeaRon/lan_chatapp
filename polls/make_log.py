import json

path = '../chat.log'

with open(path) as f:
    logs = f.read()

logs_dict = []
hoge = logs.split("\n")

for s in hoge:
    if len(s) != 0:
        logs_dict.append(json.loads(s))

for s in logs_dict:
    file_name = s['datetime'][:10]
    file_name = file_name.replace('/','_')
    with open('log/'+file_name+'.log', 'a+') as f:
        f.write(json.dumps(s)+'\n')

with open(path, 'w') as f:
    f.write('')

