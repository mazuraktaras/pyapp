from uenergoapp.adsbobject.adsbobject import ADSBDB
from pprint import pprint

bs = ADSBDB()
result = bs.get_flight_states()
pprint(result)
