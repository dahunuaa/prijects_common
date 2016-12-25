# -*- coding:utf-8 -*-

class Version(object):
    vl = []

    def __init__(self, str):
        self.vl = []
        try:
            vl = str.split('.')
            for i,v in enumerate(vl):
                if int(v) >= 10 and i != 0:
                    raise ValueError(u"小版本号需小于10")
                else:
                    self.vl.append(int(v))
        except Exception as e:
            print(e)
            raise ValueError(u"版本号不符合要求")

    def __str__(self):
        string = ""
        for v in self.vl:
            string += "%s." % v
        return string.strip(".")

    def update(self):
        rv = self.vl[::-1]
        res = []
        flag = 1
        for i, r in enumerate(rv):
            if r + flag >= 10:
                res.append(r + flag - 10)
                flag = 1
            else:
                res.append(r + flag)
                flag = 0
        if flag == 1:
            res[len(res) - 1] += 10
        self.vl = res[::-1]
        return self.__str__()
