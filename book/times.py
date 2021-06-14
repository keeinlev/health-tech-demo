from django.db import models

class IntTimes(models.IntegerChoices):
    T800AM = 800,"8:00AM"
    T815AM = 815,"8:15AM"
    T830AM = 830,"8:30AM"
    T845AM = 845,"8:45AM"
    T900AM = 900,"9:00AM"
    T915AM = 915,"9:15AM"
    T930AM = 930,"9:30AM"
    T945AM = 945,"9:45AM"
    T1000AM = 1000,"10:00AM"
    T1015AM = 1015,"10:15AM"
    T1030AM = 1030,"10:30AM"
    T1045AM = 1045,"10:45AM"
    T1100AM = 1100,"11:00AM"
    T1115AM = 1115,"11:15AM"
    T1130AM = 1130,"11:30AM"
    T1145AM = 1145,"11:45AM"
    T1200PM = 1200,"12:00PM"
    T1215PM = 1215,"12:15PM"
    T1230PM = 1230,"12:30PM"
    T1245PM = 1245,"12:45PM"
    T100PM = 1300,"1:00PM"
    T115PM = 1315,"1:15PM"
    T130PM = 1330,"1:30PM"
    T145PM = 1345,"1:45PM"
    T200PM = 1400,"2:00PM"
    T215PM = 1415,"2:15PM"
    T230PM = 1430,"2:30PM"
    T245PM = 1445,"2:45PM"
    T300PM = 1500,"3:00PM"
    T315PM = 1515,"3:15PM"
    T330PM = 1530,"3:30PM"
    T345PM = 1545,"3:45PM"
    T400PM = 1600,"4:00PM"
    T415PM = 1615,"4:15PM"
    T430PM = 1630,"4:30PM"
    T445PM = 1645,"4:45PM"
    T500PM = 1700,"5:00PM"
    T515PM = 1715,"5:15PM"
    T530PM = 1730,"5:30PM"
    T545PM = 1745,"5:45PM"
    T600PM = 1800,"6:00PM"
    T615PM = 1815,"6:15PM"
    T630PM = 1830,"6:30PM"
    T645PM = 1845,"6:45PM"
    T700PM = 1900,"7:00PM"
    T715PM = 1915,"7:15PM"
    T730PM = 1930,"7:30PM"
    T745PM = 1945,"7:45PM"

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