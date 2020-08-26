import jsonpars

myParser = jsonpars.getValueMatcher()

result = myParser.match("{\"name\": \"john\", \"age\" : 25}")[1].value

print(result)
print("age:", result["age"])
print("name:", result["name"])