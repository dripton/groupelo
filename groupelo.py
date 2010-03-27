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

def constant_factory(value):
    return itertools.repeat(value).next

# name: rating
ratings = defaultdict(constant_factory(STARTING_RATING))
# name: number of wins
wins = defaultdict(int)
# name: number of losses
losses = defaultdict(int)
# name: number of killings
killings = defaultdict(int)
# name: number of maimings
maimings = defaultdict(int)

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

def process(line):
    """Process a line denoting one match, and return an updated ratings
    dictionary."""
    global ratings
    line = line.strip()
    if not line or line.startswith("#"):
        return ratings
    parts = line.split(",")
    assert len(parts) >= 4
    game_id = parts[0]
    game_type = parts[1]
    winners = [parts[2]]
    losers = parts[3:]
    winner_lists = explode(winners)
    loser_lists = explode(losers)

    # name: change in rating
    deltas = defaultdict(int)

    for winner_list in winner_lists:
        for winner in winner_list:
            name = bare_name(winner)
            wins[name] += 1
            killings[name] += winner.count("!")
            maimings[name] += winner.count("*")
    for loser_list in loser_lists:
        for loser in loser_list:
            name = bare_name(loser)
            losses[name] += 1
            killings[name] += loser.count("!")
            maimings[name] += loser.count("*")

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
                    wr = ratings[winner]
                    lr = ratings[loser]
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
                    r1 = ratings[loser]
                    r2 = ratings[loser2]
                    delta = rating_delta(r1, r2, 0.5)
                    deltas[loser] += delta
                    deltas[loser2] -= delta
    adjusted_deltas = {}
    for key, value in deltas.iteritems():
        adjusted_deltas[key] = value / opponent_count
    for name, delta in adjusted_deltas.iteritems():
        ratings[name] += delta

def main():
    if len(sys.argv) > 1:
        fn = sys.argv[1]
        fil = open(fn)
    else:
        fil = sys.stdin
    for line in fil:
        process(line)
    sorted_ratings = sorted((
      (rating, name) for name, rating in ratings.iteritems()),
      reverse=True)
    print "Overall"
    for rating, name in sorted_ratings:
        print "%.3f %s (%d-%d) %dk, %dm" % (rating, name,
          wins[name], losses[name], killings[name], maimings[name])

if __name__ == "__main__":
    main()
