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

    def __init__(self, name: str, priorities: list):
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


class Proposer(Person):
    def __init__(self, name: str, priorities: list):
        """
        name is a string which uniquely identifies this person

        priorities is a list of strings which specifies a ranking of all
          potential partners, from best to worst
        """
        Person.__init__(self, name, priorities)
        self.proposalIndex = 0  # next person in our list to whom we might propose

    def nextProposal(self) -> int:
        if self.proposalIndex >= len(self.priorities):
            #print('returned None')
            return None
        goal: int = self.priorities[self.proposalIndex]
        self.proposalIndex += 1
        return goal

    def __repr__(self):
        return Person.__repr__(self) + '\n' + \
            'next proposal would be to person at position ' + str(self.proposalIndex)
    
class Proposee(Person):

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

    def evaluateProposal(self, suitor: str) -> bool:
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
        return False
    
    def evaluateGreedily(self, suitor: int) -> bool:
        """
        Evaluates a proposal, though does not enact it.

        Suitor is the string identifier for the proposer who is proposing

        returns True if the proposee is not matched, False otherwise
        """
        if suitor in self.ranking:
            if self.partner == None:
                self.rank = self.ranking[suitor] + 1
                return True
        return False

def parseFile(filename: str) -> list[str]:
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


def printPairings(proposerPref: dict, proposees: dict, proposer: str, proposee: str):
    totalUtility: int = 0
    proposerUtility: int = 0
    proposeeUtility: int = 0
    matchCt: int = 0
    for prop in proposerPref.values():
        # print(man)
        if prop.partner:
            print(prop.name, prop.rank, 'is paired with', str(prop.partner), proposees[str(prop.partner)].rank)
            proposerUtility += prop.rank
            proposeeUtility += proposees[str(prop.partner)].rank
            totalUtility += prop.rank + proposees[str(prop.partner)].rank
            matchCt = matchCt + 1
        else:
            print(prop.name, 'is NOT paired')

    print('Total Utility ', totalUtility, ' for ', matchCt, ' matchings')
    print(proposer, 'Utility', proposerUtility)
    print(proposee, 'Utility', proposeeUtility)



def doMatch(msg: str,fileTuple: tuple, proposer: str, proposee: str) -> void:
    """
    Performs Gale Shapley matching algorithm

    Args:
        msg (string): Message for before output
        fileTuple (tuple): Contains the files that are being worked with, as well as bool for verbose option
        proposer (string): Used to print out who is proposing
        proposee (string): Used to print out who is being proposed to
    """
    print("\n\n"+msg+" working with files ", fileTuple)
    proposerList = parseFile(fileTuple[0])
    proposerPref = dict()
    # each item in hr_list is a person and their priority list
    for person, priority in proposerList:
        # proposerPref[person[0]] = Proposer(person[0], person[1])
        proposerPref[person] = Proposer(person, priority)
    unmatched = list(proposerPref.keys())

    # initialize dictionary of appllicants
    proposeeList = parseFile(fileTuple[1])
    proposees = dict()
    # each item in proposeeList is a person and their priority list
    for person, priority in proposeeList:
        proposees[person] = Proposee(person, priority)
    verbose = fileTuple[2]
    ############################### the real algorithm ##################################
    while len(unmatched) > 0:
        if verbose:
            print("Unmatched " + proposer + "s", unmatched)
        m = proposerPref[unmatched[0]]  # pick arbitrary unmatched employer
        n = m.nextProposal()
        if n is None:
            if verbose:
                print('No more options ' + str(m))
            unmatched.pop(0)
            continue
        who = proposees[n]  # identify highest-rank applicant to which
        #    m has not yet proposed
        if verbose: print(m.name, 'proposes to', who.name)

        if who.evaluateProposal(m.name):
            if verbose: print('  ', who.name, 'accepts the proposal')

            if who.partner:
                # previous partner is getting dumped
                mOld = proposerPref[who.partner]
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
            printPairings(proposerPref, proposees, proposer, proposee)

    # we should be done
    print("Final Pairings are as follows:")
    printPairings(proposerPref, proposees, proposer, proposee)

def doGreedyMatch(msg: str, fileTuple: tuple, proposer: str, proposee: str) -> void:
    """
    Performs Greedy matching algorithm

    Args:
        msg (string): Message for before output
        fileTuple (tuple): Contains the files that are being worked with, as well as bool for verbose option
        proposer (string): Used to print out who is proposing
        proposee (string): Used to print out who is being proposed to
    """
    print("\n\n"+msg+" working with files ", fileTuple)
    proposerList = parseFile(fileTuple[0])
    proposerPref = dict()
    # each item in hr_list is a person and their priority list
    for person, priority in proposerList:
        # proposerPref[person[0]] = Proposer(person[0], person[1])
        proposerPref[person] = Proposer(person, priority)
    unmatched = list(proposerPref.keys())

    # initialize dictionary of appllicants
    proposeeList = parseFile(fileTuple[1])
    proposees = dict()
    # each item in proposeeList is a person and their priority list
    for person, priority in proposeeList:
        proposees[person] = Proposee(person, priority)
    verbose = fileTuple[2]
    ############################### the real algorithm ##################################
    while len(unmatched) > 0:
        if verbose:
            print("Unmatched " + proposer + "s", unmatched)
        m = proposerPref[unmatched[0]]  # pick arbitrary unmatched employer
        n = m.nextProposal()
        if n is None:
            if verbose:
                print('No more options ' + str(m))
            unmatched.pop(0)
            continue
        who = proposees[n]  # identify highest-rank applicant to which
        #    m has not yet proposed
        if verbose: print(m.name, 'proposes to', who.name)

        if who.evaluateGreedily(m.name):
            if verbose: print('  ', who.name, 'accepts the proposal')

            if who.partner:
                # previous partner is getting dumped
                mOld = proposerPref[who.partner]
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
            printPairings(proposerPref, proposees, proposer, proposee)

    # we should be done
    print("Final Pairings are as follows:")
    printPairings(proposerPref, proposees, proposer, proposee)

files = [("Employers0.txt", "Applicants0.txt", True),
         ("Employers.txt", "Applicants.txt", True),
         ("Employers3.txt", "Applicants3.txt", True),
         # ("Employers1.txt", "Applicants1.txt", False),
         # ("Employers2.txt","Applicants2.txt", False)
        ]
for fileTuple in files:
    doMatch("Employers propose ", fileTuple, "Employer", "Applicant")
    doGreedyMatch("Employers greedy propose ", fileTuple, "Employer", "Applicant")



