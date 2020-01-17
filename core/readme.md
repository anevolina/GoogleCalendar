## main_api.py

The main point for communication with the module.  

- #### Functions

Authorization in Google Calendar processed in two steps:

#### `authorise_user_step1()`  
Function returns authorization url. User should follow this url, and 
grant access to their calendar. At the very end Google will issue a key 
which you should pass to the second step.
 
 *Input*  
 `Nothing`   
  
 *Output*  
`url: string` - authorization url.
 ___  
#### `authorise_user_step2(user_id, key)`  
Function will fetch token for given user, using provided key from the previous step.
  
 *Input*  
`user_id: integer` - user id as it will be in our database  
`key: string` - key issued from the previous step

*Output*  
`True/False` - return `True` if the key is correct.
___
#### `check_user_settings(user_id)`  
Function to check if we have credentials for given `user_id` in our database.
It raises `GCUnauthorisedUserError` exception if we don't have records. Use it to check if user authorised
this application for their Google Calendar.

*Input*  
`user_id: integer` - id for user as it'll be in the internal database.

*Output*  
`None`
___

#### `create_event(user_id, message)`  
Function will parse given raw `message`, searching for date, time, attendees and location,
and then publish an event at Google Calendar for given `user_id`.  
If it couldn't find date and/or time it'll create an event for the whole current day.
 
*Input*  
`user_id: integer` - user id as it is in the internal database  
`message: string` - user input

*Output*  
`event_status: string` - possible variants: `"CREATED"` if an event 
was created successfully and `"MISTAKE""` otherwise.  
`start: datetime` - at what time event was added  
`attendees: list` - emails which were parsed and added as guests from the message  
`location: string` - *doesn't work for now* - location which was parsed and added as a location
___
#### `add_calendar(user_id, calendar_name)`  
Function tries to fetch existed calendar by given `calendar_name` and if there is
no calendar with such a name it creates a new one.

*Input*  
`user_id: integer` - user id as it is in our database  
`calendar_name: string` - raw user input. Not case sensitive 'TesT' == 'test'.

*Output*  
`status: string` - possible variants: `"FETCHED"` - if calendar was successfully fetched
by given name, `"CREATED"` - if a new calendar was created, `"MISTAKE"` - otherwise.

___
#### `unbind_calendar(user_id)`  
Set calendar id to `"primary"` value. All further events will be added to the main
calendar for the user.
  
*Input*  
`user_id: integer` - user id as it is in our database

*Output*  
`True/False` - whether operation was successful or not.

___
- #### Exceptions

#### `GCUnauthorisedUserError`
Raised if user didn't authorised in Google Calendar service (we don't have
saved credentials for them).
