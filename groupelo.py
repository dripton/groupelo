#!/usr/bin/env python

"""Calculate Elo ratings for a series of game results, where games can
include variable numbers of players and teams.

See http://en.wikipedia.org/wiki/Elo_rating_system

New players start at 1500
Rn = Ro + K(W-We)
Rn is new rating
Ro is previous rating
K is the same for every 2-player match
W is 1 for win, 0 for loss, 0.5 for draw

We is win expectancy
For 2 players, We = 1 / (10 ** (-delta/400) + 1)
where delta is the difference in ratings

For N players, assume each player played a game against
each of his opponents.  But reduce K so that multiplayer
matches count the same as 2-player matches.
"""

__copyright__ = "Copyright 2010 David Ripton"
__license__ = "MIT"

import sys
import itertools
from collections import defaultdict

STARTING_RATING = 1500
CATEGORIES = [
    "overall",
    "group", "individual",
    "armed", "unarmed",
    "tournament", "exhibition",
]

def constant_factory(value):
    return itertools.repeat(value).next

def explode(li):
    """Convert a list of strings into a list of lists of strings.

    Each inner list is one team.
    """
    result = []
    for el in li:
        li2 = el.split("&")
        inner = [el2.strip() for el2 in li2]
        result.append(inner)
    return result

def win_expectancy(r1, r2):
    """Return the win expectancy for the player with rating r1 against
    the player with rating r2."""
    return 1.0 / (10 ** ((r2 - r1) / 400.0) + 1)

def rating_delta(r1, r2, w):
    """Return the rating delta (relative to player with rating r1) for a
    match between players with ratings r1 and r2, and result w.

    w is 1 for a win for r1, 0 for a loss for r1, and 0.5 for a draw.
    """
    k = 50
    we = win_expectancy(r1, r2)
    return k * (w - we)

def bare_name(name):
    """Return name without any trailing '*' or '!' characters."""
    while name and (name[-1] == "*" or name[-1] == "!"):
        name = name[:-1]
    return name


class Elo(object):
    def __init__(self, category, lines):
        assert category in CATEGORIES
        self.category = category
        self.lines = lines

        # name: rating
        self.ratings = defaultdict(constant_factory(STARTING_RATING))
        # name: number of wins
        self.wins = defaultdict(int)
        # name: number of losses
        self.losses = defaultdict(int)
        # name: number of killings
        self.killings = defaultdict(int)
        # name: number of maimings
        self.maimings = defaultdict(int)

    def process(self, line):
        """Process a line denoting one match, and update the ratings."""
        line = line.strip()
        if not line or line.startswith("#"):
            return
        parts = line.split(",")
        assert len(parts) >= 4
        game_id = parts[0].strip()
        armed_unarmed = parts[1].strip()
        tournament_exhibition = parts[2].strip()
        winners = [parts[3]]
        losers = parts[4:]
        winner_lists = explode(winners)
        loser_lists = explode(losers)

        # Filter out results for the wrong category of fight
        if self.category == "overall":
            pass
        elif self.category == "group":
            if len(winner_lists[0]) == 1 and len(loser_lists) == 1:
                return
        elif self.category == "individual":
            if len(winner_lists[0]) > 1 or len(loser_lists) > 1:
                return
        elif self.category == "armed":
            if armed_unarmed != self.category:
                return
        elif self.category == "unarmed":
            if armed_unarmed != self.category:
                return
        elif self.category == "tournament":
            if tournament_exhibition != self.category:
                return
        elif self.category == "exhibition":
            if tournament_exhibition != self.category:
                return

        # name: change in rating
        deltas = defaultdict(int)

        for winner_list in winner_lists:
            for winner in winner_list:
                name = bare_name(winner)
                self.wins[name] += 1
                self.killings[name] += winner.count("!")
                self.maimings[name] += winner.count("*")
        for loser_list in loser_lists:
            for loser in loser_list:
                name = bare_name(loser)
                self.losses[name] += 1
                self.killings[name] += loser.count("!")
                self.maimings[name] += loser.count("*")

        for ii, loser_list in enumerate(loser_lists):
            for loser in loser_list:
                while loser and (loser[-1] == "*" or loser[-1] == "!"):
                    loser = loser[:-1]
                opponent_count = 0
                for winner_list in winner_lists:
                    for winner in winner_list:
                        while winner and (winner.endswith("*") or
                          winner.endswith("!")):
                            winner = winner[:-1]
                        opponent_count += 1
                        wr = self.ratings[winner]
                        lr = self.ratings[loser]
                        delta = rating_delta(wr, lr, 1)
                        deltas[winner] += delta
                        deltas[loser] -= delta
                # Only the losers after this one, to avoid double-counting.
                for jj in xrange(ii + 1, len(loser_lists)):
                    loser_list2 = loser_lists[jj]
                    for loser2 in loser_list2:
                        while loser2 and (loser2.endswith("*") or
                          loser2.endswith("!")):
                            loser2 = loser2[:-1]
                        opponent_count += 1
                        r1 = self.ratings[loser]
                        r2 = self.ratings[loser2]
                        delta = rating_delta(r1, r2, 0.5)
                        deltas[loser] += delta
                        deltas[loser2] -= delta
        adjusted_deltas = {}
        for key, value in deltas.iteritems():
            adjusted_deltas[key] = value / opponent_count
        for name, delta in adjusted_deltas.iteritems():
            self.ratings[name] += delta

    def process_all(self):
        """Process all lines."""
        for line in self.lines:
            self.process(line)

    def output(self):
        sorted_ratings = sorted((
          (rating, name) for name, rating in self.ratings.iteritems()),
          reverse=True)
        print self.category
        for rating, name in sorted_ratings:
            print "%.3f %s (%d-%d) %dk, %dm" % (rating, name,
              self.wins[name], self.losses[name], self.killings[name],
              self.maimings[name])
        print


def main():
    if len(sys.argv) > 1:
        fn = sys.argv[1]
        fil = open(fn)
    else:
        fil = sys.stdin
    bytes = fil.read()
    fil.close()
    lines = bytes.split("\n")
    for category in CATEGORIES:
        elo = Elo(category, lines)
        elo.process_all()
        elo.output()


if __name__ == "__main__":
    main()
