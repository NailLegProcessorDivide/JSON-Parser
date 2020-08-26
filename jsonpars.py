#!/bin/python3

class element:
    def __init__(self, myType="None", value = None):
        self.myType = myType
        self.value = value

class matchDigit:
    def match(self, inText):
        if (len(inText) > 0) and (inText[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
            return (True, element("Digit", inText[0]), inText[1:])
        return (False, element(), inText)

class matchDigit19:
    def match(self, inText):
        if (len(inText) > 0) and (inText[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']):
            return (True, element("Digit", inText[0]), inText[1:])
        return (False, element(), inText)
        
class matchDigit0:
    def match(self, inText):
        if (len(inText) > 0) and (inText[0] in ['0']):
            return (True, element("Digit", inText[0]), inText[1:])
        return (False, element(), inText)

class parsechain:
    def __init__(self, subParser):
        self.parser = subParser
    def match(self, inText):
        last = True
        text = inText
        val = []
        mtype = "None"
        while last:
            last, ell, text = self.parser.match(text)
            if last:
                val.append(ell.value)
                mtype = "[ "+ell.myType+" ]"


        if len(val) == 0:
            return (False, element(), inText)
        return (True, element(mtype, val), text)


class matchWhiteSpace:
    def match(self, inText):
        if (len(inText) > 0) and (inText[0] in [' ', '\t', '\n', '\r']):
            nextSpace = self.match(inText[1:])
            if nextSpace[0]:
                return nextSpace
            return (True, element("whiteSpace"), inText[1:])
        return (True, element("whiteSpace"), inText)

class matchSymbol:
    def __init__(self, symbol):
        self.symbol = symbol
    def match(self, inText):
        if len(inText)>0 and inText[0] == self.symbol:
            return (True, element("symbol", self.symbol), inText[1:])
        return (False, element(), inText)

class matchOption:
    def __init__(self, subParser):
        self.parser = subParser
    def match(self, inText):
        out = self.parser.match(inText)
        out = (True, out[1], out[2])
        return out
        
class matchOne:
    def __init__(self, subParser1, subParser2):
        self.parser1 = subParser1
        self.parser2 = subParser2
    def match(self, inText):
        out = self.parser1.match(inText)
        if out[0]:
            return out
        out = self.parser2.match(inText)
        if out[0]:
            return out
        return (False, element(), inText)

class matchBoth:
    def __init__(self, subParser1, subParser2):
        self.parser1 = subParser1
        self.parser2 = subParser2
    def match(self, inText):
        out = self.parser1.match(inText)
        if out[0]:
            out2 = self.parser2.match(out[2])
            if out2[0]:
                nType = "{" + out[1].myType + ", " + out2[1].myType + "}"
                return (True, element(nType, [out[1].value] + [out2[1].value]), out2[2])
        return(False, element(), inText)


class matchNumber:
    def __init__(self):
        self.chainDigit = parsechain(matchDigit())
        self.d0 = matchDigit0()
        self.d19 = matchBoth(matchDigit19(), matchOption(self.chainDigit))
        self.oSub = matchOption(matchSymbol('-'))
        self.oSubAdd = matchOne(matchSymbol('+'), self.oSub)
        self.Ee = matchOne(matchSymbol('e'), matchSymbol('E'))
        self.integ = matchBoth(matchOption(self.oSub), matchOne(self.d19, self.d0))
        self.frac = matchOption(matchBoth(matchSymbol('.'), self.chainDigit))
        self.exp = matchOption(matchBoth(self.Ee, matchBoth(self.oSubAdd, self.chainDigit)))
        self.all = matchBoth(self.integ, matchBoth(self.frac, self.exp))

    def match(self, inText):
        encval = self.all.match(inText)
        if encval[0] == False:
            return encval
        value = encval[1].value

        signadd = 1
        if value[0][0] == '-':
            signadd = -1

        intval = int(value[0][1][0])
        if value[0][1][1] != None:
            for i in value[0][1][1]:
                intval = intval * 10 + int(i)

        floatval = 0
        divis = 1
        if value[1][0] != None:
            for i in value[1][0][1]:
                divis /= 10
                floatval = floatval * 10 + int(i)
        floatval *= divis

        exp = 0
        if value[1][1] != None:
            expsin = 1
            if value[1][1][1][0] == '-':
                expsin = -1
            for i in value[1][1][1][1]:
                exp = exp * 10 + int(i)
            exp *= expsin

        numval = (signadd * (intval + floatval)) * (10 ** exp) 

        return (True, element("Number", numval), encval[2])

class matchNot:
    def __init__(self, chars):
        self.chars = chars
    def match(self, inText):
        if len(inText) > 0 and not inText[0] in self.chars:
            return (True, element("symbol", inText[0]), inText[1:])
        return (False, element(), inText)

class matchSpecial:
    def match(self, inText):
        if len(inText) > 1 and inText[0] == '\\':
            val = ''
            offset = 2
            if inText[1] == '\"':
                val = '\"'
            elif inText[1] == '\\':
                val = '\\'
            elif inText[1] == '/':
                val = '/'
            elif inText[1] == 'b':
                val = '\b'
            elif inText[1] == 'f':
                val = '\f'
            elif inText[1] == 'n':
                val = '\n'
            elif inText[1] == 'r':
                val = '\r'
            elif inText[1] == 't':
                val = '\t'
            elif inText[1] == 'u':
                val = chr(eval("0x"+inText[2:6]))
                offset = 6

            return (True, element("symbol", val), inText[offset:])
        return (False, element(), inText)

class matchString:
    def __init__(self):
        self.quote = matchSymbol("\"")
        self.bulk = matchOne(matchNot("\\\b\r\n\"\f\t"), matchSpecial())
    def match(self, inText):
        fq = self.quote.match(inText)
        if fq[0]:
            val = ""
            cont = True
            iText = fq[2]
            while cont:
                cont, nextval, iText = self.bulk.match(iText)
                if cont:
                    val += nextval.value
            fq = self.quote.match(iText)
            if fq[0]:
                return (True, element("String", val), fq[2])
        return (False, element(), inText)

class matchBool:
    def match(self, inText):
        if inText[:4] == "true":
            return (True, element("Bool", True), inText[4:])
        if inText[:5] == "false":
            return (True, element("Bool", False), inText[5:])
        return (False, element(), inText)

class matchNull:
    def match(self, inText):
        if inText[:4] == "null":
            return (True, element("null", None), inText[4:])
        return (False, element(), inText)

class matchValue:
    def __init__(self, arrayM, objM):
        self.white = matchWhiteSpace()
        self.mVal = matchOne(
                    matchOne(matchOne(matchString(), matchNumber()),
                            matchOne(matchBool(), matchNull())),
                            matchOne(arrayM, objM))
    def match(self, inText):
        ws = self.white.match(inText)
        stuff = self.mVal.match(ws[2])
        ws = self.white.match(stuff[2])
        if stuff[0]:
            return (True, stuff[1], ws[2])
        return (False, element(), inText)

class matchArray:
    def __init__(self, objM):
        self.open = matchSymbol('[')
        self.comma = matchSymbol(',')
        self.close = matchSymbol(']')
        self.white = matchWhiteSpace()
        self.wClose = matchBoth(self.white, self.close)
        self.value = matchValue(self, objM)
        self.nextVal = matchBoth(self.comma, self.value)
    def match(self, inText):
        opdat = self.open.match(inText)
        arr = []
        if opdat[0]:
            cont, val, iText = self.value.match(opdat[2])
            vvalue = [0] + [val.value]
            while cont:
                arr.append(vvalue[1])
                cont, val, iText = self.nextVal.match(iText)
                vvalue = val.value
            opdat = self.close.match(iText)
            if opdat[0]:
                return (True, element("Array", arr), opdat[2])
        return (False, element(), inText)


class matchObject:
    def __init__(self):
        self.open = matchSymbol('{')
        self.close = matchSymbol('}')
        self.white = matchWhiteSpace()
        self.arrMatch = matchArray(self)
        self.kvPair = matchBoth(
                        matchBoth(self.white, matchString()),
                        matchBoth(
                            matchBoth(self.white, matchSymbol(':')),
                            self.arrMatch.value))
        self.nextKVPair = matchBoth(matchSymbol(','), self.kvPair)
    def match(self, inText):
        opdat = self.open.match(inText)
        obj = {}
        if opdat[0]:
            cont, val, iText = self.kvPair.match(opdat[2])
            vvalue = [0] + [val.value]
            while cont:
                obj[vvalue[1][0][1]] = vvalue[1][1][1]
                cont, val, iText = self.nextKVPair.match(iText)
                vvalue = val.value
            opdat = self.close.match(iText)
            if opdat[0]:
                return (True, element("Object", obj), opdat[2])
        return (False, element(), inText)

def getValueMatcher():
    vMatcher = matchObject()
    return vMatcher.arrMatch.value
    

if __name__ == "__main__":
    inp = input("> ")

    myMatcher = getValueMatcher()
    rval = myMatcher.match(inp)

    print(rval)
    print(rval[1].myType)
    print(rval[1].value)

