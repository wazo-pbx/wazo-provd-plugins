# Limitations

Here is a list of what is known to be non-working or malfunctioning on this DECT system:

* **Phonebook**: the phonebook URL is too long for what the firmware accepts as a parameter.
  Therefore, the phonebook does not work.
  
 it is nevertheless possible to circumvent this limitation by following the wiki below 
  https://wiki.slemoal.fr/index.php/Wazo_Phonebook_SnomDECT
  
* **Timezone** : provd is not able to determine the country from a timezone. It is not possible
  to define the country of the DECT and the daylight-savings time changes.

* **Repeater
	M6 repeaters ONLY are supported in this firmware version.