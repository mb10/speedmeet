import random
import itertools
people = list("abcdefghijklmnopqrstuvwxyz")
datadict = {}
def generaterandom(n):
	return random.randrange(1,n+1)

#a program that imitates "speed dating" for a group of people trying to get to know each other. Takes a dict with structure {person: {match:score, }, }, and generates a schedule of people to meet based people's self-selected scores of how well they already know each other. Returns dict.
#TO DO: Integrate with csv or database of real inputs, generate formatted datecards to distribute

#dummy data for testing, stucture {person: {match:score, }, }
for i in people:
	use = []
	for p in people:
		if p != i:
			use.append(p)
	datadict[i] = {}
	for item in use:
			datadict[i][item] = generaterandom(10)

people = datadict.keys()

#TO-DO: will need to clean up people's responses to remove nonparticipants
#TO-DO: adjusting ranges all to same scale would more evenly weight what each person says, even if some use fewer extremes.

matches = {} 
#{person: {match: score, }, }
for person in datadict:
	for match in datadict[person]: #for each pairing of each person ab:
		if (match, person) in matches:	#if (b,a) is in the dict, add the number to that number
			matches[(match, person)] += datadict[person][match]
		else: #if (b,a) is not in the dict create (a,b) as that number
			matches[(person, match)] = datadict[person][match]

#get list of pairs sorted by rank
ranking = [{"match": list(match), "rank": matches[match]} for match in matches]
ranking = sorted(ranking, key = lambda item : item["rank"], reverse=True)

#test cases for get_free TO DELETE
two = [[0, ['a', 'b']], [1, ['a', 'b']], [2, []], [3, ['a', 'b']], [4, []], [5, ['a','b']], [6, ['a', 'b']], [7, ['a', 'b']], [8, ['a','b']], [9, ['a', 'b']]]
twofoursix = [[0, ['a', 'b']], [1, ['a', 'b']], [2, []], [3, ['a', 'b']], [4, []], [5, ['a','b']], [6, []], [7, ['a', 'b']], [8, ['a','b']], [9, ['a', 'b']]]
maybenine = [[0, ['a', 'b']], [1, ['a', 'b']], [2, []], [3, ['a', 'b']], [4, ['a','b']], [5, ['a','b']], [6, ['a', 'b']], [7, ['a', 'b']], [8, ['a','b']], [9, []]]

def old_get_free(person, maxconsec):
	#finds all the available rounds for a person, making sure no run goes longer than maxconsec
	freeslots = []
	current_round = 0
	all_rounds = person

	while current_round < len(all_rounds):
		before = []
		after = []
		if all_rounds[current_round][1] == []:
			beforebreak = True
			afterbreak = True
			if current_round >= maxconsec: 
				before = all_rounds[current_round-maxconsec:current_round]
			else:
				beforebreak = False
			if len(all_rounds)-current_round > maxconsec:
				after = all_rounds[current_round+1:current_round+1+maxconsec]
			else:
				afterbreak = False
			if len(before) > 0:
				for i in before:
					if i[1] == []:
						beforebreak = False
			if len(after) > 0:
				for i in after:
					if i[1] == []:
						afterbreak = False
			if afterbreak == False and beforebreak == False:
				freeslots.append(current_round)
			#problem: can end up with len 2x - 1 if both sides are x-1
			#need to rewrite to count backwards and forwards from position?
		current_round += 1
	return freeslots


def get_free(person, maxconsec):
	current_round = 0
	free_slots = []
	while current_round < len(person):
		if person[current_round][1] == []:
			left = 1
			right = 1
			while current_round - left >= 0 and person[current_round-left][1] != []:
				left +=1
			while current_round + right < len(person) and person[current_round + right][1] != []:
				right +=1
			if left + right - 1 <= maxconsec:
				free_slots.append(current_round)
		current_round += 1
	return free_slots

def pick_round(person1, person2, maxconsec):
	#find matching open rounds for two people and return one of them at random
	person1free = get_free(person1, maxconsec)
	person2free = get_free(person2, maxconsec)
	both_free = [i for i in person1free if i in person2free]
	if both_free:
		choice = random.choice(both_free)
		return choice
	else:
		return None

#takes rankings and other parameters and creates a datecard for each person
# to do: add failsafe for people with too few filled rounds. to poach from people with full cards?
def best_matches_rounds(ranking, rounds, maxconsec):
	datecards = dict((person, [[i,[]] for i in range(0,rounds)]) for person in people)
	rank_index = 0
	used = []
	unused = []
	while rank_index < len(ranking):
		person1, person2 = ranking[rank_index]["match"][0], ranking[rank_index]["match"][1]
		round_to_fill = pick_round(datecards[person1], datecards[person2], maxconsec)
		if round_to_fill != None:
			datecards[person1][round_to_fill][1] = [person1,person2]
			datecards[person2][round_to_fill][1] = [person2,person1]
			used.append(ranking[rank_index])
		else:
			unused.append(ranking[rank_index])
		rank_index+=1
	return datecards


def create_person_ranks(ranking):
	#create a dict in format {person: [list of matches ranked by match strength}
	person_ranks = {}	
	for rank in ranking:
		match = rank["match"]
		rank = rank["rank"]
		for person in match:
			if person in person_ranks:
				person_ranks[person].append([match, rank])			
			else:
				person_ranks[person] = [[match, rank]]
	return person_ranks

def sorted_running_list(datecards, maxconsec, person_ranks):
	#returns a list of people who still have available date slots and possible matches, sorted in order of number of slots free
	running_list = []
	for person in datecards:
		rounds_free = get_free(datecards[person], maxconsec)
		if rounds_free != []:# and rank_indices[person] < len(person_ranks[person]): #need a test to find out if no possible matches
			running_list.append([person, len(rounds_free)])
	running_list = sorted(running_list, key = lambda item : item[1], reverse = True)
	return [i[0] for i in running_list]


def by_person_rounds(ranking, rounds, maxconsec):
	#lines each person up with 0 or 1 dates per round until no more dates possible
	datecards = dict((person, [[i,[]] for i in range(0,rounds)]) for person in people) #people is currently global variable
	used = []
	person_ranks = create_person_ranks(ranking) 
	running_list = random.sample(list(people), len(list(people))) #start with list of people in random order
	successful_round = True
	while len(running_list) > 0 and successful_round == True:
		matched_this_round = [] #matched list makes sure no person gets more than one date per round
		successful_round = False #if no match found for any person in running_list, stops loop
		for person in running_list:
			person = person[0]
			current_index = 0 #breaks loop for each person when all matches tested
			while current_index < len(person_ranks[person]) and person not in matched_this_round: #match_found == False: 
				match = person_ranks[person][current_index][0]
				person1, person2 = match[0], match[1]
				if match not in used and person1 in running_list and person2 in running_list and person1 not in matched_this_round and person2 not in matched_this_round:
					round_to_fill = pick_round(datecards[person1], datecards[person2], maxconsec)
					if round_to_fill != None:
						datecards[person1][round_to_fill][1] = [person1,person2]
						datecards[person2][round_to_fill][1] = [person2,person1]
						matched_this_round.append(person1)
						matched_this_round.append(person2)
						used.append(match)
						successful_round = True
				current_index += 1
		running_list = sorted_running_list(datecards, maxconsec, person_ranks)
	return datecards

rounds = by_person_rounds(ranking, 10, 5)

for item in rounds:
	print item, rounds[item], len(rounds[item])














