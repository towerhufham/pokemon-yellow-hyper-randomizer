import json
import random

def getPokemonNames():
	names = []
	with open("names.txt", "r") as file:
		for line in file:
			names.append(line.upper())
	return names
	
def generateMarkovTable(names):
	markov = {}
	for name in names:
		name = name.lower()
		for i in range(0, len(name)-1):
			char = name[i]
			nextChar = name[i+1]
			if char in markov:
				if nextChar in markov[char]:
					markov[char][nextChar] += 1
				else:
					markov[char][nextChar] = 1
			else:
				markov[char] = {}
				markov[char][nextChar] = 1
	with open("nameMarkov.json", "w") as file:
		json.dump(markov, file, indent=1)
		
def generateName(minLength=4, maxLength=10):
	with open("nameMarkov.json") as file:
		markov = json.load(file)
		char = random.choice([k for k in markov.keys()])
		name = char
		while True:
			#get probabilities
			probTable = markov[char]
			probSum = sum(probTable.values())
			
			r = random.randint(1, probSum+1)
			for key, value in probTable.items():
				if r < value:
					char = key
					break
				else:
					r -= value
			
			if char != "\n":
				name = name + char
			else:
				char = "."
				
			if char == ".":
				#if name isn't long enough, try again
				if len(name) - 1 < minLength: #sub 1 because \n doesn't count
					return generateName(minLength, maxLength)
				else:
					#pad the name so it's maxLength
					name = name + "."*(maxLength - len(name))
					return name
			elif len(name) == maxLength - 1:
				name = name + "."
				return name
	
		
if __name__ == "__main__":
	generateMarkovTable(getPokemonNames())
	with open("nameMarkov.json") as file:
		print(generateName().upper())