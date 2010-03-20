This code calculates Elo ratings (see
http://en.wikipedia.org/wiki/Elo_rating_system) for multiplayer games.

The data file format does not currently support draws, or games where the
non-winners need to be ranked rather than all lumped together as equal losers.
Adding support for those would be pretty easy, but I don't currently need
those features and I didn't want to complicate the data file.

I saw the idea for the the technique of treating a multi-player game as a
series of two-player games (winner beat each loser, losers drew each other,
scale down the K-value to prevent games with more players from counting more)
from a 2005 post on rec.games.trading-cards.jyhad by Frederick Scott.  It's
a pretty obvious and elegant idea so it probably predates that post by a few
decades.

I don't think the algorithm for team games is correct yet.  One's teammates'
ratings should factor in, since it's easy to win with strong teammates and
hard to win with weak teammates.
