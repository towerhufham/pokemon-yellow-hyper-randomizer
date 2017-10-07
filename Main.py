import json
import random
__author__ = "Tower Hufham"

def internalIDs():
	"""
	Returns a list of all the used internal IDs in Pokemon Yellow
	"""
	#invalid is the list of unused internal id's
	invalid = [-1, 31, 32, 50, 52, 56, 61, 62, 63, 67, 68, 69, 79, 80, 81, 86, 87, 94, 95, 115, 121, 122, 127, 134, 135, 137, 140, 146, 156, 159, 160, 161, 162, 172, 174, 175, 181, 182, 183, 184]
	return [n for n in range(1, 191) if n not in invalid]
	
def randomInternalID():
	"""
	Returns a random (used) internal ID.
	"""
	return random.choice(internalIDs())
	
def getAllPokemonAddresses():
	"""
	Returns a list of the starting addresses in the main pokemon data bank (starting at 0x0383de in the rom)
	Note: the bank is in pokedex order, not internal id order
	"""
	firstAddress = int("0x0383de", base=16) #bulbasaur
	numberOfPokemon = 150 #don't change mew, as that would corrupt data in red/blue
	dataSize = 28 #number of bytes each pokemon has in memory
	addresses = []
	for i in range(firstAddress, firstAddress + numberOfPokemon * dataSize, dataSize):
		addresses.append(hex(i))
	return addresses
	
class bytePos(object):
	"""
	A simple object that contains 1 byte of data, and its corresponding address in the rom
	This was created as an easy way to change bytes in the rom in large batches
	This code will often reference "bplists", which are just a list of these objects
	Note: requires rom to be in "r+b" mode
	"""
	def __init__(self, rom, pos):
		"""
		Sets the byte field to be the byte in the rom at the given address
		"""
		self.pos = pos
		rom.seek(pos)
		self.byte = rom.read(1).hex()
		rom.seek(0)
	
	def __str__(self):
		return "[pos: " + str(self.pos) + ", value: " + str(self.byte) + "]"
	
	def write(self, rom):
		"""
		Seeks this bytepos's address in the rom, then writes self.byte to it
		"""
		rom.seek(self.pos)
		rom.write(bytearray.fromhex(self.byte))
		rom.seek(0)

def shuffleBytes(bplist):
	"""
	Shuffles all the "byte" fields from a list of bytePos, while leaving the positions unchanged
	"""
	#get all byte fields
	bytes = [b.byte for b in bplist]
	#shuffle them
	random.shuffle(bytes)
	#assign new bytes
	for i in range(len(bplist)):
		bplist[i].byte = bytes[i]

#Note: currently doesn't work because of the rom's internal bank structure		
def randomizeSprites(rom, addresses, output):
	"""
	A (mostly failed) attempt at randomizing the sprites.
	Currently doesn't work because of the way the sprite banks are scattered about the rom
	"""
	#this function is complicated, but this will help: https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_base_stats_data_structure_in_Generation_I#Sprites
	sprites = []
	for a in addresses:
		indexAddress = int(a, base=16)
		rom.seek(indexAddress)
		index = rom.read(1)
		
		spriteAddress = int(a, base=16) + 10
		rom.seek(spriteAddress)
		sprites.append((index, rom.read(5)))
	random.shuffle(sprites)
	for i in range(len(addresses)):
		indexAddress = int(addresses[i], base=16)
		output.seek(indexAddress)
		output.write(sprites[i][0])
	
		spriteAddress = int(addresses[i], base=16) + 10
		output.seek(spriteAddress)
		output.write(sprites[i][1])
	rom.seek(0)
	output.seek(0)
	
def generateName(minLength=4, maxLength=10):
	"""
	Uses nameMarkov.json to generate a name using a markov chain based on pokemon names (not just first gen)
	"""
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
	
def randomizedCryData(rom):
	"""
	Returns a bplist of randomized cry data.
	Currently breaks the rival, and possibly more stuff
	"""
	#each cry data has 3 different attributes, which are shuffled seperately
	param1 = []
	param2 = []
	param3 = []
	for i in range(234594, 235900, 3): #start of bank to end of bank in steps of 3
		param1.append(bytePos(rom, i))
		param2.append(bytePos(rom, i+1))
		param3.append(bytePos(rom, i+2))
	shuffleBytes(param1)
	shuffleBytes(param2)
	shuffleBytes(param3)
	return param1 + param2 + param3
	
def randomizedEvolutionLearnsetData(rom):
	"""
	Returns a bplist containing shuffled pointers to pokemon learnset data
	Only randomizes pointers between pokemon of the same evolution stage
	"""
	dataList = {"basic": [], "stage1": [], "stage2": []}
	basicIDs = [1, 2, 3, 4, 5, 6, 11, 12, 13, 15, 17, 19, 23, 24, 25, 26, 27, 29, 30, 33, 34, 36, 37, 40, 42, 43, 44, 47, 48, 51, 53, 55, 57, 58, 59, 60, 64, 65, 70, 71, 72, 76, 77, 78, 82, 84, 88, 90, 92, 96, 98, 100, 102, 106, 107, 108, 109, 112, 123, 132, 133, 148, 153, 157, 163, 165, 169, 170, 171, 173, 176, 177, 180, 185, 188]
	stage1IDs = [8, 9, 10, 18, 20, 22, 35, 39, 41, 45, 46, 54, 83, 85, 89, 91, 93, 97, 99, 101, 103, 104, 105, 110, 113, 116, 117, 118, 119, 120, 124, 128, 129, 130, 136, 138, 139, 141, 142, 143, 144, 145, 147, 150, 152, 155, 158, 164, 166, 167, 168, 178, 179, 186, 189]
	stage2IDs = [7, 14, 16, 21, 28, 38, 49, 66, 73, 74, 75, 111, 114, 125, 131, 149, 151, 154, 187, 190]
	#note: the legendary birds, mew, and mewtwo are counted as stage2
	#maybe instead of evolution stage, it should be sorted by how many evolutions the pokemon has left?
	currentid = 1
	for i in range(242149, 242529, 2): #start of bank to end of bank in steps of 2
		#there are room for 190 pokemon in this bank, but only 151 are used
		#we need to make sure we're using valid data (currentid keeps track of which id we're on)
		if currentid in basicIDs:
			dataList["basic"].append((bytePos(rom, i), bytePos(rom, i+1)))
		elif currentid in stage1IDs:
			dataList["stage1"].append((bytePos(rom, i), bytePos(rom, i+1)))
		elif currentid in stage2IDs:
			dataList["stage2"].append((bytePos(rom, i), bytePos(rom, i+1)))
		currentid += 1
	
	#create a clone of the tuples in datalist, then shuffle
	shuffledBasic = [t for t in dataList["basic"]]
	shuffled1 = [t for t in dataList["stage1"]]
	shuffled2 = [t for t in dataList["stage2"]]
	random.shuffle(shuffledBasic)
	random.shuffle(shuffled1)
	random.shuffle(shuffled2)
	
	for i in range(len(dataList["basic"])):
		dataList["basic"][i][0].byte = shuffledBasic[i][0].byte
		dataList["basic"][i][1].byte = shuffledBasic[i][1].byte
	for i in range(len(dataList["stage1"])):
		dataList["stage1"][i][0].byte = shuffled1[i][0].byte
		dataList["stage1"][i][1].byte = shuffled1[i][1].byte
	for i in range(len(dataList["stage2"])):
		dataList["stage2"][i][0].byte = shuffled2[i][0].byte
		dataList["stage2"][i][1].byte = shuffled2[i][1].byte
	
	bplist = []
	for s in dataList:
		for t in dataList[s]:
			bplist.append(t[0])
			bplist.append(t[1])
	return bplist
	
	
def randomizeNames(output):
	"""
	Generates a new name for each pokemon, then writes it to the given file.
	Note: does not use bytepos's or bplists
	"""
	#get string name
	output.seek(950272) #name bank address
	for p in range(189): #there are 189 pokemon slots, some unused
		name = generateName()
		for char in name:
			if char != ".":
				output.write(bytes([ord(char)+31])) #+95 converts ord() to pokemon's character codes
			else:
				output.write(bytearray.fromhex("50"))
	
def buildRomWithBytePosList(rom, bplist):
	"""
	Takes in a rom with a list of bytePos's, then writes all of them to a new rom
	"""
	with open("output.gbc", mode="wb") as output:
		#start with a file exactly the same as rom
		rom.seek(0)
		base = rom.read()
		output.write(base)
		
		#for each bytePos in list, change those bytes
		for b in bplist:
			b.write(output)
		
		randomizeNames(output)
	
if __name__ == "__main__":
	with open("Pokemon - Yellow Version.gbc", mode="rb") as rom:
	
		#get the pokemon addresses (minus mew)
		addresses = getAllPokemonAddresses()
		
		#init bplist
		bplist = []
		
		#these functions makes things easier
		def getPokemonStat(rom, addresses, offset):
			"""Returns every pokemon's stat (chosen stat is dependant on offset) in the main pokemon data bank""" 
			return [bytePos(rom, int(address, base=16)+offset) for address in addresses]
		
		def extendBpList(offset):
			"""Shuffles a sub-bplist and adds it to the main bplist"""
			sublist = getPokemonStat(rom, addresses, offset)
			shuffleBytes(sublist)
			bplist.extend(sublist)
		
		#get new...
		#base hp
		extendBpList(1)
		#base attack
		extendBpList(2)
		#base defense
		extendBpList(3)
		#base speed
		extendBpList(4)
		#base special
		extendBpList(5)
		#first types
		extendBpList(6)
		#second types
		extendBpList(7)
		
		#these next few stats are easy to randomize, but probably shouldn't be touched for balance's sake
		#base catch rates
		#extendBpList(8)
		#base exp yields
		#extendBpList(9)
		#base growth rate
		#extendBpList(19)
		
		#randomize starting attacks
		extendBpList(15)
		extendBpList(16)
		extendBpList(17)
		extendBpList(18)
			
		#randomize palettes
		palettes = []
		for i in range(469282, 469431): #palette data range
			palettes.append(bytePos(rom, i))
		shuffleBytes(palettes)
		bplist.extend(palettes)
		
		#randomize cries (currently breaks rival, possibly other trainers)
		#bplist.extend(randomizedCryData(rom))
		
		#randomize "evolution/learnset" data
		bplist.extend(randomizedEvolutionLearnsetData(rom))
		
		#################################################################################
		# TODO: make evolution/learnset data randomize with respect to evolution stage	#
		# TODO: fix cry stuff					   										#
		#################################################################################
		
		#build rom
		buildRomWithBytePosList(rom, bplist)