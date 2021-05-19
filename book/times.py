from django.db import models

class IntTimes(models.IntegerChoices):
    T800AM = 1200,"8:00AM"
    T815AM = 1215,"8:15AM"
    T830AM = 1230,"8:30AM"
    T845AM = 1245,"8:45AM"
    T900AM = 1300,"9:00AM"
    T915AM = 1315,"9:15AM"
    T930AM = 1330,"9:30AM"
    T945AM = 1345,"9:45AM"
    T1000AM = 1400,"10:00AM"
    T1015AM = 1415,"10:15AM"
    T1030AM = 1430,"10:30AM"
    T1045AM = 1445,"10:45AM"
    T1100AM = 1500,"11:00AM"
    T1115AM = 1515,"11:15AM"
    T1130AM = 1530,"11:30AM"
    T1145AM = 1545,"11:45AM"
    T1200PM = 1600,"12:00PM"
    T1215PM = 1615,"12:15PM"
    T1230PM = 1630,"12:30PM"
    T1245PM = 1645,"12:45PM"
    T100PM = 1700,"1:00PM"
    T115PM = 1715,"1:15PM"
    T130PM = 1730,"1:30PM"
    T145PM = 1745,"1:45PM"
    T200PM = 1800,"2:00PM"
    T215PM = 1815,"2:15PM"
    T230PM = 1830,"2:30PM"
    T245PM = 1845,"2:45PM"
    T300PM = 1900,"3:00PM"
    T315PM = 1915,"3:15PM"
    T330PM = 1930,"3:30PM"
    T345PM = 1945,"3:45PM"
    T400PM = 2000,"4:00PM"
    T415PM = 2015,"4:15PM"
    T430PM = 2030,"4:30PM"
    T445PM = 2045,"4:45PM"
    T500PM = 2100,"5:00PM"
    T515PM = 2115,"5:15PM"
    T530PM = 2130,"5:30PM"
    T545PM = 2145,"5:45PM"
    T600PM = 2200,"6:00PM"
    T615PM = 2215,"6:15PM"
    T630PM = 2230,"6:30PM"
    T645PM = 2245,"6:45PM"
    T700PM = 2300,"7:00PM"
    T715PM = 2315,"7:15PM"
    T730PM = 2330,"7:30PM"
    T745PM = 2345,"7:45PM"

    def getKeys():
        l = []
        for time in IntTimes.choices:
            l.append(str(time[0]))
        return l
    
    def getValues():
        l = []
        for time in IntTimes.choices:
            l.append(time[1])
        return l