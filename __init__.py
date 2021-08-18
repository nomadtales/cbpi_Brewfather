from modules import cbpi
import requests

bf_uri = "http://log.brewfather.net/stream"

def bf_api_id():
  api_id = cbpi.get_config_parameter("brewfather_api_id", None)
  if api_id is None:
    try:
      cbpi.add_config_parameter("brewfather_api_id", "", "text", "Brewfather API Id")
      return ""
    except:
      cbpi.notify("Brewfather Error", "Unable to update brewfather_api_id parameter within database. Try updating CraftBeerPi and reboot.", type="danger", timeout=None)
  else:
    return api_id

# interval in seconds
@cbpi.backgroundtask(key="brewfather_task", interval=905)
def brewfather_background_task(api):
  api_id = bf_api_id()
  if api_id == "":
    cbpi.notify("Brewfather Error", "Id not set. Update brewfather_api_id parameter within System > Parameters.", type="danger", timeout=None)
    return

  for i, fermenter in cbpi.cache.get("fermenter").iteritems():

    # if we have a beer name, we will log the temperatures
    if fermenter.brewname and fermenter.brewname.strip():
      try:
        queryString = {
          "id": api_id
        }
        
        # Changed so that it matches my Fermenter Configuration in CraftBeerPi3
        data = {
          "name": fermenter.name,
          "beer": fermenter.brewname,
          "temp": cbpi.get_sensor_value(fermenter.sensor3), 
          "aux_temp": cbpi.get_sensor_value(fermenter.sensor), 
          "ext_temp": cbpi.get_sensor_value(fermenter.sensor2), 
          "temp_unit": cbpi.get_config_parameter("unit", "C")
        }

        response = requests.post(bf_uri, params=queryString, json=data)

        if response.status_code != 200:
          cbpi.notify("Brewfather Error", "Received unsuccessful response. Ensure API Id is correct. HTTP Error Code: " + str(response.status_code), type="danger", timeout=None)

      except BaseException as error:
        cbpi.notify("Brewfather Error", "Unable to send message." + str(error), type="danger", timeout=None)
        pass