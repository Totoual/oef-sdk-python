from examples.weather.weather_schemas import WEATHER_DATAMODEL
from oef.agents import OEFAgent
from oef.api import CFP_TYPES
from oef.schema import AttributeSchema, DataModel, Description


class WeatherStation(OEFAgent):

    def on_cfp(self, origin: str, conversation_id : str, msg_id : int, target : int, query : CFP_TYPES):
        print("Received cfp from {0} cif {1} msgId {2} target {3} query [{4}]"
              .format(origin, conversation_id, msg_id, target, query))

        proposal = Description({"price": 13}, DataModel("weather_data", [AttributeSchema("price", int, True)]))
        self._connection.send_propose(conversation_id, origin, [proposal], msg_id + 1, target + 1)

    def on_accept(self, origin: str, conversation_id : str, msg_id : int, target : int):
        print("Received accept from {0} cif {1} msgId {2} target {3}".format(origin, conversation_id, msg_id, target))


if __name__ == "__main__":
    station_description = Description({"wind_speed": True,
                                       "temperature": True,
                                       "air_pressure": True,
                                       "humidity": True},
                                      WEATHER_DATAMODEL)
    agent = WeatherStation("weather_station", oef_addr="127.0.0.1", oef_port=3333)
    agent.connect()
    agent.register_service(station_description)
    agent.run()
