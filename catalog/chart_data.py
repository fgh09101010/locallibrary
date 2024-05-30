import json
import random

def random_num():
    random_number = random.randint(0, 255)
    return random_number


def Doughnut(x):
    d=dict()
    for i in x:
        l=i.language
        if l not in d:
            d[l]=1
        else:
            d[l]+=1
    l1=[]
    l2=[]
    l3=[]
    l4=[]
    for k,v in d.items():
        l1.append(str(k))
        l2.append(v)
        c=[random_num(),random_num(),random_num()]
        l3.append("rgba"+str(tuple(c+[0.2])))
        l4.append("rgba"+str(tuple(c+[1])))

    data = {
        'labels': l1,
        'datasets': [{
            'label': 'Doughnut Chart',
            'data': l2,
            'backgroundColor': l3,
            'borderColor': l4,
            'borderWidth': 1
        }]
    }
    chart_data=json.dumps(data)
    return chart_data

def Barchart(x):
    d=dict()
    for i in x:
        l=i.get_status_display()
        if l not in d:
            d[l]=1
        else:
            d[l]+=1

    l1=[]
    l2=[]
    l3=[]
    l4=[]
    for k,v in d.items():
        l1.append(str(k))
        l2.append(v)
        c=[random_num(),random_num(),random_num()]
        l3.append("rgba"+str(tuple(c+[0.2])))
        l4.append("rgba"+str(tuple(c+[1])))

    data= {
              "labels": l1, 
              "datasets": [{
                  "label": 'Book Status', 
                  "data": l2, 
                  "backgroundColor": l3,
                  "borderColor": l4,
                  "borderWidth": 1
              }]
          }
    chart_data=json.dumps(data)
    return chart_data