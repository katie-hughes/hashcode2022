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
	def pprint(self):
		print(f'PROJECT NAME: {self.name}')
		print(f'Days to Complete: {self.days}')
		print(f'Score: {self.score}')
		print(f'Best Before: {self.deadline}')
		print(f'Number of Roles: {self.nroles}')
		print(f'Skills Needed: {self.skills}')
		print()

#Project()


class Contributor:
	def __init__(self, name, skills):
		self.name = name
		self.skills = skills
	def cprint(self):
		print(f'Name: {self.name}')
		print(f'Skills: {self.skills}')
		print()


## PARSING

#fname = 'a_an_example.in.txt'
fname = 'b_better_start_small.in.txt'

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
			skills_needed[skill_name] = skill_level
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
	for s in skills:
		required_level = skills[s]
		found = False
		for c in clist:
			c_skills = c.skills
			if s in c_skills:
				if c_skills[s] >= required_level:
					team.append(c)
					team_dict[c] = [s, required_level,c_skills[s]]
					found = True
					break
		if not found:
			return ([], {})
	for c in team:
		print(c.name, end=' ')
	print()
	return (team, team_dict)


print("\n\n TEST \n \n ")

returning = {}
return_dates = []
d = 0
while d<final_day:
	print(f"\nDay {d}")
	if d in returning:
		for team in returning[d]:
			print(f"re adding team {team}")
			contributor_list += team
		return_dates = list(filter(lambda x: x != d, return_dates))
	project_list_copy = list(project_list)
	for p in project_list:
		print(p.name)
		team, team_dict = find_people(p, contributor_list)
		if not len(team):
			print('team not found :(')
		else:
			print("team found yay!")
			project_list_copy.remove(p)
			for c in team:
				# contributor cant work on other projects for now
				contributor_list.remove(c)
				# increment their skill if need be
				skill = team_dict[c][0]
				p_level = team_dict[c][1]
				c_level = team_dict[c][2]
				if c_level <= p_level:
					print(f"Incrementing skill {skill} for {c.name}")
					c.skills[skill] += 1
			# keep track of what day they should be put back in
			return_date = d + p.days
			print(f"return date is {return_date}")
			if return_date not in returning:
				returning[return_date] = []
			returning[return_date].append(team)
			return_dates.append(return_date)
	## incrememtn the date to the nearest returning date
	project_list = project_list_copy
	if not len(return_dates):
		break
	else:
		next_date = min(return_dates)
		print(f'next date: {next_date}')
		d = next_date


print("ALL DONE")
