* Grid_topology_test

Tämä on kanditutkielman yhteydessä tuotettu koe, jossa neliö- ja kuusioverkkojen eroja testataan A*-polunetsinnän yhteydessä. astar_square ja astar_hex sisältävät algoritmit, joissa on omat heuristiikat, kaaren pituudet, jne. Visualizer on pygame-kirjastoa käyttävä GUI. Automoitujen testien aikana pygame ei piirrä mitään, jotta pygame ei vaikuta algoritmin suoritusnopeuteen.
** Kokeen rakenne
*** 1
Koe aloitetaan luomalla alkuperäiskartta, joka edustaa maastoa, jossa polunetsintää halutaan suorittaa. Tämä vastaa kaupunkia, metsää, tai mitä tahansa muuta maastoa, jossa on selviä esteitä, joita pitää välttää matkalla maaliin. Luomme alkuperäiskartan käyttämällä shapely-kirjastoa.
