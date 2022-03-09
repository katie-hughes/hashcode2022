import numpy as np
import random
import os
from operator import attrgetter
os.chdir('input_data')


class Project:
	def __init__(self, name, days, score, deadline, nroles, skills):
		self.name = name
		self.days = days
		self.score = score
		self.deadline = deadline
		self.nroles = nroles
		self.skills = skills
		# urgent if: high score, small days to complete, small best before
		self.urgency = score/(deadline*days)
		# track the last day this project will receive points
		self.lastday = score + deadline
	def pprint(self):
		print(f'PROJECT NAME: {self.name}')
		print(f'Days to Complete: {self.days}')
		print(f'Score: {self.score}')
		print(f'Best Before: {self.deadline}')
		print(f'Number of Roles: {self.nroles}')
		print(f'Skills Needed: {self.skills}')
		print()


class Contributor:
	def __init__(self, name, skills):
		self.name = name
		self.skills = skills
	def cprint(self):
		print(f'Name: {self.name}')
		print(f'Skills: {self.skills}')
		print()


## PARSING

fname = 'a_an_example.in.txt'
#fname = 'b_better_start_small.in.txt'
#fname = 'c_collaboration.in.txt'
#fname = 'd_dense_schedule.in.txt'
#fname = 'e_exceptional_skills.in.txt'
#fname = 'f_find_great_mentors.in.txt'


solution_fname = 'sol_'+fname
solution = open(solution_fname, 'w')

contributor_list = []
project_list = []

with open(fname) as f:
	lines = f.readlines()
	first_line = (lines[0]).split()
	contributors = int(first_line[0])
	projects = int(first_line[1])
	index = 1

	for c in range(contributors):
		name = (lines[index]).split()[0]
		number_skills = int((lines[index]).split()[1])
		skills_had = {}
		for i in range(number_skills):
			index += 1
			skill_name = (lines[index]).split()[0]
			skill_level = int((lines[index]).split()[1])
			skills_had[skill_name] = skill_level
		cclass = Contributor(name, skills_had)
		contributor_list.append(cclass)
		index += 1


	for p in range(projects):
		spl = lines[index].split()
		project_name = spl[0]
		days = int(spl[1])
		score = int(spl[2])
		best_before = int(spl[3])
		number_roles = int(spl[4])
		skills_needed = {}
		for r in range(number_roles):
			index += 1
			skill_name = (lines[index]).split()[0]
			skill_level = int((lines[index]).split()[1])
			skills_needed[r] = (skill_name, skill_level)
			#if skill_name not in skills_needed:
			#	skills_needed[skill_name] = []
			#skills_needed[skill_name].append(skill_level)
		pclass = Project(project_name, days, score, best_before, number_roles, skills_needed)
		project_list.append(pclass)
		index += 1


for c in contributor_list:
	c.cprint()

for p in project_list:
	p.pprint()


def max_day(plist):
	# find the maximum day at which point u have no more points
	max = 0
	for p in plist:
		deadline = p.deadline
		score = p.score
		p_max = deadline + score
		if p_max > max:
			max = p_max
	return max

final_day = max_day(project_list)

print(f"Last day: {final_day}")

# I sort projects from most to least urgent
project_list = sorted(project_list, key = lambda x: -1.0*x.urgency)


# currently this does not account for mentors. implement later
def find_people(project, clist):
	skills = project.skills
	team = []
	team_dict = {}
	for n in skills: #every skill in project must be accounted for
		s = skills[n][0]
		required_level = skills[n][1]
		found = False
		for c in clist:
			c_skills = c.skills
			if s in c_skills: # must have right skill
				if c_skills[s] >= required_level: # skill must be high enough
					if c not in team: # same person cant be in twice
						team.append(c)
						team_dict[c] = [s, required_level,c_skills[s]]
						found = True
						break
		if not found:
			return ([], {})
	return (team, team_dict)


def score(p, completed_day):
	if p.deadline >= completed_day:
		print(f"Full points: {p.score}")
		return p.score
	else:
		points_off = completed_day - p.deadline
		s = p.score - points_off
		print(f"Reduced score {s}/{p.score}")
		if s>=0:
			return s
		else:
			return 0

removed = 0

def filter_project_list(plist, day):
	cpy = list(plist)
	for p in plist:
		if p.lastday < day:
			print(f"Removing project {p.name}")
			cpy.remove(p)
			global removed
			removed += 1
	return cpy



print("\n\n TEST \n \n ")

returning = {}
return_dates = []
completed = 0
cumulative_score = 0
d = 0
while d<final_day:
	print(f"\nDay {d}/{final_day}")
	if d in returning:
		for team in returning[d]:
			print("re adding team of", end=' ')
			for c in team:
				print(c.name, end=' ')
			print()
			contributor_list += team
		return_dates = list(filter(lambda x: x != d, return_dates))
	project_list = filter_project_list(project_list, d)
	project_list_copy = list(project_list)
	for p in project_list:
		team, team_dict = find_people(p, contributor_list)
		if not len(team):
			pass
			#print('team not found :(')
		else:
			print(f"team found for {p.name} yay!")
			project_list_copy.remove(p)
			solution.write(p.name+'\n')
			for c in team:
				print(c.name, end=' ')
				solution.write(c.name+' ')
			solution.write('\n')
			print()
			for c in team:
				# contributor cant work on other projects for now
				try:
					contributor_list.remove(c)
				except:
					print(f"{c.name} isnt in contributor list???")
					exit()
				# increment their skill if need be
				skill = team_dict[c][0]
				p_level = team_dict[c][1]
				c_level = team_dict[c][2]
				if c_level <= p_level:
					print(f"Incrementing skill {skill} for {c.name}")
					c.skills[skill] += 1
			print()
			# keep track of what day they should be put back in
			return_date = d + p.days
			print(f"return date is {return_date}")
			if return_date not in returning:
				returning[return_date] = []
			returning[return_date].append(team)
			return_dates.append(return_date)
			p_score = score(p, return_date)
			cumulative_score += p_score
			completed += 1
	## incrememtn the date to the nearest returning date
	project_list = project_list_copy
	if not len(return_dates):
		break
	else:
		next_date = min(return_dates)
		print(f'next date: {next_date}')
		d = next_date


print("ALL DONE")
projects_left = len(project_list)
print(f"{completed} projects completed")
print(f"{projects_left} projects left over")
print(f"{removed} projects removed")
print(f"{cumulative_score} final score")

a_score =  33
b_score =  743841
c_score =  82556
d_score =  133020
e_score =  1606532
f_score =  538623

finalscore = a_score + b_score + c_score + d_score + e_score + f_score

print(f"FINALSCORE {finalscore}")
# 10246205

solution.close()

solution = open(solution_fname, 'r+')
content = solution.read()
solution.seek(0)
solution.write(str(completed)+'\n'+content)
solution.close()
