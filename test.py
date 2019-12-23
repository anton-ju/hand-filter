import unittest
from handproc import renumber_places
 pypokertoolsfrom pypokertools.parsers import PSHandHistory

class Test(unittest.TestCase):
    def test_renumber_places(self):
        with open('2762507411.txt') as f:
            hh_text = f.read()
        hh_text = '''

        Dr.Octagon77 collected 1510 from pot
        busto_soon finished the tournament in 14th place
        newguy89 finished the tournament in 14th place

        PokerStars Hand #207287950000: Tournament #2762507411, $26.96+$0.54 USD Hold'em No Limit - Match Round I, Level II (50/100) - 2019/12/20 1:28:53 MSK [2019/12/19 17:28:53 ET]
        Table '2762507411 1' 4-max Seat #3 is the button
        Seat 3: Dr.Octagon77 (945 in chips)
        Seat 4: DiggErr555 (1055 in chips)
        Dr.Octagon77: posts the ante 20
        DiggErr555: posts the ante 20
        Dr.Octagon77: posts small blind 50
        DiggErr555: posts big blind 100
        *** HOLE CARDS ***
        Dealt to DiggErr555 [Kd 9s]
        Dr.Octagon77: raises 825 to 925 and is all-in
        DiggErr555: calls 825
        *** FLOP *** [7s Ks 8s]
        *** TURN *** [7s Ks 8s] [3d]
        *** RIVER *** [7s Ks 8s 3d] [Jh]
        *** SHOW DOWN ***
        DiggErr555: shows [Kd 9s] (a pair of Kings)
        Dr.Octagon77: shows [4s 4c] (a pair of Fours)
        DiggErr555 collected 1890 from pot
        *** SUMMARY ***
        Total pot 1890 | Rake 0
        Board [7s Ks 8s 3d Jh]
        Seat 3: Dr.Octagon77 (button) (small blind) showed [4s 4c] and lost with a pair of Fours
        Seat 4: DiggErr555 (big blind) showed [Kd 9s] and won (1890) with a pair of Kings
        '''
        result = renumber_places(hh_text)
        self.assertTrue(result.
        pass


if __name__ == 'main':
   unittest.main()


