from collections import Counter
positions=['11:30', '00:15', '01:30', '03:00', '04:15', '05:30', '06:15', '07:30', '09:00', '10:15', '11:30', '11:45', '00:15', '00:30', '01:00', '01:30', '02:00', '02:45', '03:30', '04:15', '04:45', '05:30', '06:30', '07:00', '07:45', '08:30', '09:30', '10:15', '10:45']

def parse(t):
    h,m=map(int,t.split(":"))
    if h==12: h=0
    return (h*60+m)/2.0
angles=sorted(parse(t) for t in positions)
unique=sorted(set(angles))
def gaps(arr):
    return [((arr[(i+1)%len(arr)]-arr[i])%360) for i in range(len(arr))]
print({"count_total":len(angles),"count_unique":len(unique),"duplicate_angles":{k:v for k,v in Counter(angles).items() if v>1},"all_gaps":gaps(angles),"unique_gaps":gaps(unique)})
