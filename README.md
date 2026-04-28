# Grid_topology_test

Tämä on kanditutkielman yhteydessä tuotettu koe, jossa neliö- ja kuusioverkkojen eroja testataan A*-polunetsinnän yhteydessä. astar_square ja astar_hex sisältävät algoritmit, joissa on omat heuristiikat, kaaren pituudet, jne. Visualizer on pygame-kirjastoa käyttävä GUI. Automoitujen testien aikana pygame ei piirrä mitään, jotta pygame ei vaikuta algoritmin suoritusnopeuteen.
## Kokeen rakenne
## Alkuperäiskartta
Koe aloitetaan luomalla joukko alkuperäiskarttoja, jotka edustavat maastoa, jossa polunetsintää halutaan suorittaa. Tämä vastaa kaupunkia, metsää, tai mitä tahansa muuta maastoa, jossa on selviä esteitä, joita pitää välttää matkalla maaliin. Luomme alkuperäiskartan käyttämällä shapely-kirjastoa. random_maps_generator.py-tiedostossa oleva config kertoo minkälaiset asetukset ovat käytössä. Projektissa on käytössä 4 eri esteprosenttia, 10%, 20%, 30% ja 40%. Alkuperäiskarttoja luodaan niin, että vektorigrafiikalla piirretyt esteet peittävät esteprosentin verran alkuperäiskartan pinta-alasta. Kun alkuperäiskartta on luotu, aloitus- ja maalikoordinaatit lasketaan satunnaisesti.
![linkki plottiin](plot_images/0.20_terrain_8.png)
