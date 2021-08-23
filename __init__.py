from modules import cbpi
import requests
import logging
import json

bf_uri = "http://log.brewfather.net/stream?id="

DEBUG = True

def log(s):
  if DEBUG:
      s = "cbpi_Brewfather: " + s
      cbpi.app.logger.info(s)

def bf_api_id():
  api_id = cbpi.get_config_parameter("brewfather_api_id", None)
  if api_id is None:
    try:
      cbpi.add_config_parameter("brewfather_api_id", "", "text", "Brewfather API Id")
      return ""
    except:
      cbpi.notify("Brewfather Error", "Unable to update brewfather_api_id parameter within database. Try updating CraftBeerPi and reboot.", type="danger", timeout=None)
      log("Unable to update brewfather_api_id parameter within database. Try updating CraftBeerPi and reboot.")
  else:
    return api_id

# interval in seconds
@cbpi.backgroundtask(key="brewfather_task", interval=900)
def brewfather_background_task(api):
  
  # Get the api id
  api_id = bf_api_id()

  # generate the uri
  uri = bf_uri + api_id
  #uri = "http://log.brewfather.net/stream?id=DkwcJB53PfhbAu"

  log("cbpi_Brewfather Start")
  
  if api_id == "":
    cbpi.notify("Brewfather Error", "Id not set. Update brewfather_api_id parameter within System > Parameters.", type="danger", timeout=None)
    return

  # Create a payload hashtable
  payload = {}

  # Get the fermenter details
  for i, fermenter in cbpi.cache.get("fermenter").iteritems():
    log("key %s value.name %s value.instance.last_value %s value.type %s" % (i, fermenter.name, fermenter.instance.last_value, fermenter.type))

    # if we have a beer name, we will log the temperatures
    if fermenter.brewname and fermenter.brewname.strip():

      payload['name'] = fermenter.name
      payload['beer'] = fermenter.brewname
      payload['temp'] = cbpi.get_sensor_value(fermenter.sensor3)
      payload['aux_temp'] = cbpi.get_sensor_value(fermenter.sensor)
      payload['ext_temp'] = cbpi.get_sensor_value(fermenter.sensor2)
      payload['temp_unit'] = cbpi.get_config_parameter("unit", "C")
      payload['gravity_unit'] = "G"

  # Get the iSpindel sensor details
  for key, sensors in cbpi.cache.get("sensors").iteritems():
    log("key %s value.name %s value.instance.last_value %s value.type %s" % (key, sensors.name, sensors.instance.last_value, sensors.type))

    if (sensors.type == "iSpindel"):
      if (sensors.instance.sensorType == "Battery"):
          payload['battery'] = sensors.instance.last_value
      if (sensors.instance.sensorType == "Gravity"):
          payload['gravity'] = sensors.instance.last_value

  try:
 
    log("uri: %s, Payload: %s" % (uri, json.dumps(payload)))
    cbpi.notify("uri: %s, Payload: %s" % (uri, json.dumps(payload)))

    # send payload to BrewFather
    response = requests.post(uri, json=payload)

    log("Result %s" % response.text)
    cbpi.notify("Result %s" % response.text)

    if response.status_code != 200:
      cbpi.notify("Brewfather Error", "Received unsuccessful response. Ensure API Id is correct. HTTP Error Code: " + str(response.status_code), type="danger", timeout=None)

  except BaseException as error:
    cbpi.notify("Brewfather Error", "Unable to send message." + str(error), type="danger", timeout=None)
  pass
  
  log("cbpi_Brewfather End")