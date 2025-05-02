# 411-finalProject Weather APP

For our project we used the OpenWeather API. The app allows users to create accounts, authenticate, and fetch current weather information for various cities. The app allows users to login/logout, update weather information, and update their accounts.

## Routes

### Health Check

- **Route**: `/api/health`
- **Request Type**: GET
- **Purpose**: Confirms that the service is running.
- **Request Body**: None
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: `{ "status": "success", "message": "Service is running" }`

---

### Create Account

- **Route**: `/api/create-user`
- **Request Type**: PUT
- **Purpose**: Creates a new user account with a username and password.
- **Request Body**:
  - `username` (String): User's chosen username
  - `password` (String): User's chosen password
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 201
    - Content:
      ```json
      {
        "status": "success",
        "message": "User 'newuser123' created successfully"
      }
      ```
  - **Error Response** (Missing fields):
    - Code: 400
    - Content:
      ```json
      {
        "status": "error",
        "message": "Username and password are required"
      }
      ```
- **Example Request**:
  ```json
  {
    "username": "newuser123",
    "password": "securepassword"
  }

 - **Example Response**:
  ```json
     { "status": "success", "message": "User 'newuser123' created successfully" }

  
 ```

  ### Login

- **Route**: `/api/login`
- **Request Type**: POST
- **Purpose**: Authenticates an existing user
- **Request Body**:
  - `username` (String): User's username
  - `password` (String): User's  password
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 201
    - Content:
      ```json
       {
            "status": "success",
            "message": "User 'newuser123' logged in"
        }
      ```
- **Example Request**:
  ```json
  {
    "username": "newuser123",
    "password": "securepassword"
  }
  ``` 
  - **Example Response**:
  ```json
  {     "status": "success",
           "message": "User 'newuser123' logged in"
  }
  ```
  ### Logout

- **Route**: `/api/logout`
- **Request Type**: POST
- **Purpose**: logs out an user
- **Request Body**:
  - `None`
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content:
      ```json
       {
            "status": "success",
            "message": "User 'newuser123' logged out"
        }
      ```

 ### Change Password
- **Route**: `/api/change-password`
- **Request Type**: POST
- **Purpose**: Allows authenicated user to change their password
- **Request Body**:
  - `new_password (String): New password`
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content:
      ```json
       {
      "status": "success",
        "message": "Password changed"
      }

   - **Example request**:
     ```
        { "new_password": "newsecurepassword" }
 
      ```

   ### Reset users Table
- **Route**: `/api/reset-users`
- **Request Type**: DELETE
- **Purpose**: Removes all existing users in the users table and recreate it
- **Request Body**:
  - `None`
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content:
      ```json
       {
          "status": "success",
          "message": "Users table recreated successfully"
      }
 
      ```

 ### Get All weather data
- **Route**: `/api/weather`
- **Request Type**: GET
- **Purpose**: Returns all weather records
- **Request Body**:
  - `None`
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: List of weather records


   ### Add weather
- **Route**: `/api/weather
- **Request Type**: POST
- **Purpose**: Adds a weather record to the lsit based on the given city
- **Request Body**:
  - `city_name (String): City to fetch weather for`
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 201
    - Content:
      ```json
       {
          "status": "success",
          "message": "Weather data added for Boston"
      }

     - **Example request**:
     { "city_name": "Boston" }  
 
      ```

      
 ### Get weahter by city
- **Route**: `/api/weather/<city_name>`
- **Request Type**: GET
- **Purpose**: Retrieved weather data for a specific city
- **URL Paremeter**:
  - `city_name (String): City name to search for`
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content: Weather for the specify city.

  ### Update weather by city
- **Route**: `/api/weather/<city_name>`
- **Request Type**: Put
- **Purpose**: updates the weather data for a specific city
- **URL parameter**:
  - `city_name (String): City name to update`
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content:
      ```json
       {
          "status": "success",
          "message": "Weather data updated for Boston"
      }
 
      ``` 

 ### Delete weather by city
- **Route**: `/api/weather/<city_name>`
- **Request Type**: DELETE
- **Purpose**: Deletes a city weather data
- **URL parameter**:
  - `city_name (String): City name to delete`
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content:
      ```json
       {
           "status": "success",
            "message": "Weather data for Boston deleted"
      }
 
      ```

 ### clear all weather
- **Route**: `/api/weather`
- **Request Type**: DELETE
- **Purpose**: Deletes all stored weather records
- **URL parameter**:
  - `city_name (String): City name to delete`
- **Response Format**: JSON
  - **Success Response Example**:
    - Code: 200
    - Content:
      ```json
       {
           "status": "success",
          "message": "All weather data cleared"
      }
 
      ```







    



