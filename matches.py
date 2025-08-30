"""
Demo of Gale-Shapley stable matching algorithm.
Written by Michael Goldwasser
Modified by Vicki Allan

For simplicity, the file format is assumed (without checking) to match
the following format:

  bob:     alice,carol
  david:   carol,alice

and likewise for the applicant file,  and the identifiers should be
self-consistent between the two files.
If a match is unacceptable, it is not listed in the preferences.

"""
from numpy import *

class Person:
    """
    Represent a generic person
    """

    def __init__(self, name, priorities):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        self.name = name
        self.priorities = priorities
        self.partner = None
        self.rank = None

    def __repr__(self):
        return 'Name is ' + self.name + '\n' + \
            'Partner is currently ' + str(self.partner) + str(self.rank) + '\n' + \
            'priority list is ' + str(self.priorities)


class Employer(Person):
    def __init__(self, name, priorities):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        Person.__init__(self, name, priorities)
        self.proposalIndex = 0  # next person in our list to whom we might propose

    def nextProposal(self):
        if self.proposalIndex >= len(self.priorities):
            #print('returned None')
            return None
        goal = self.priorities[self.proposalIndex]
        self.proposalIndex += 1
        return goal

    def __repr__(self):
        return Person.__repr__(self) + '\n' + \
            'next proposal would be to person at position ' + str(self.proposalIndex)


class Applicant(Person):

    def __init__(self, name, priorities):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        Person.__init__(self, name, priorities)

        # now compute a reverse lookup for efficient candidate rating
        self.ranking = {}
        for rank in range(len(priorities)):
            self.ranking[priorities[rank]] = rank

    def evaluateProposal(self, suitor):
        """
        Evaluates a proposal, though does not enact it.

        suitor is the string identifier for the employer who is proposing

        returns True if proposal should be accepted, False otherwise
        """
        if suitor in self.ranking:
            if self.partner == None or self.ranking[suitor] < self.ranking[self.partner]:
                self.rank = self.ranking[suitor] + 1
                return True
            else:
                return False
        else:
            return False

def parseFile(filename):
    """
    Returns a list of (name,priority_list) pairs.
    """
    people = []
    # f = file(filename)
    with open(filename) as f:
        for line in f:
            pieces = line.split(':')
            name = pieces[0].strip()
            if name:
                priorities = pieces[1].strip().split(',')
                for i in range(len(priorities)):
                    priorities[i] = priorities[i].strip()
                people.append((name, priorities))
        f.close()
    return people


def printPairings(employer, applicant):
    totalUtility = 0
    matchCt = 0
    for empl in employer.values():
        # print(man)
        if empl.partner:
            print(empl.name, empl.rank, 'is paired with', str(empl.partner), applicant[str(empl.partner)].rank)
            totalUtility += empl.rank + applicant[str(empl.partner)].rank
            matchCt = matchCt + 1
        else:
            print(empl.name, 'is NOT paired')

    print('Total Utility ', totalUtility, ' for ', matchCt, ' matchings')


def doMatch(msg,fileTuple):
    print("\n\n"+msg+" working with files ", fileTuple)
    employerList = parseFile(fileTuple[0])
    employerPref = dict()
    # each item in hr_list is a person and their priority list
    for person, priority in employerList:
        # employerPref[person[0]] = Employer(person[0], person[1])
        employerPref[person] = Employer(person, priority)
    unmatched = list(employerPref.keys())

    # initialize dictionary of appllicants
    applicant_list = parseFile(fileTuple[1])
    applicants = dict()
    # each item in applicant_list is a person and their priority list
    for person, priority in applicant_list:
        applicants[person] = Applicant(person, priority)
    verbose = fileTuple[2]
    ############################### the real algorithm ##################################
    while len(unmatched) > 0:
        if verbose:
            print("Unmatched employers ", unmatched)
        m = employerPref[unmatched[0]]  # pick arbitrary unmatched employer
        n = m.nextProposal()
        if n is None:
            if verbose:
                print('No more options ' + str(m))
            unmatched.pop(0)
            continue
        who = applicants[n]  # identify highest-rank applicant to which
        #    m has not yet proposed
        if verbose: print(m.name, 'proposes to', who.name)

        if who.evaluateProposal(m.name):
            if verbose: print('  ', who.name, 'accepts the proposal')

            if who.partner:
                # previous partner is getting dumped
                mOld = employerPref[who.partner]
                if verbose:
                    print('  ', mOld.name, 'gets dumped')

                mOld.partner = None
                mOld.rank = 0
                unmatched.append(mOld.name)

            unmatched.pop(0)
            who.partner = m.name
            m.partner = who.name
            m.rank = m.proposalIndex
        else:
            if verbose:
                print('  ', who.name, 'rejects the proposal')

        if verbose:
            print("Tentative Pairings are as follows:")
            printPairings(employerPref, applicants)

    # we should be done
    print("Final Pairings are as follows:")
    printPairings(employerPref, applicants)


files = [("Employers0.txt", "Applicants0.txt", True)] #,
         #("Employers.txt", "Applicants.txt", False),
         #("Employers3.txt", "Applicants3.txt", False),
         #("Employers1.txt", "Applicants1.txt", False),
         #("Employers2.txt","Applicants2.txt", False)]
for fileTuple in files:
    doMatch("Employers propose ", fileTuple)


