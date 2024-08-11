# twttr = {"twitter": None}
# yt = {"youtube": "link"}
# inst = {"instagram": None}
# fb = {"facebook": "link"}
#
# l = [twttr, yt, inst, fb]
# dict1 = {}
# for x in l:
#     # print(list(x.values()))
#     if (list(x.values())[0]) != None:
#         dict1[list(x.keys())[0]] = list(x.values())[0]
# print(dict1)

task_details_str = "Build a website | make a trailer"


task_details_list = task_details_str.split('|')
tasks = []
for idx, task_detail in enumerate(task_details_list, start=1):
    task_dict = {
        'SlNo': idx,
        'TaskDetail': task_detail.strip(),
        'Status': 'PENDING'
    }
    tasks.append(task_dict)
print(str(tasks))