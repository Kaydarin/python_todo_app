# Python Todo

This is an example **Python Todo API** system. Uses **Flask** & **SQLAlchemy** packages.

## Setup
1. Get `JWT_KEY`, `GITHUB_CLIENT_ID` & `GITHUB_CLIENT_SECRET` from admin.
2. Put those keys in `docker-compose.yaml` to its respected environment variables.

## Run
1. Type `docker compose up` or `docker compose up -d` in terminal to start the project. By default, it will run at `http://127.0.0.1:5000`
2. To close it, run `docker compose down`

## Usage
1. Login the app using **GitHub** account at `http://127.0.0.1:5000` or `http://127.0.0.1:5000/login`
2. After login, `JWT` key will be shown, copy it and put it as `Authorization` header to any network protocols client such as `curl` or Postman to execute the app APIs.
3. Refer **Documentation** below to execute further.

## Documentation
To test the functionality, at first, we'll need to understand the structure. There is **Task** and there is **Todo**. One user can create many tasks and each task can have many todos. So, user will need to create a **task** before they can create a **todo**. Below are all the routes for this project:-

### Login

- Route: `/login`
- Type: **GET**
- URL Parameters: **N/A**
- Body Example: **N/A**

### List Tasks

- Route: `/list-tasks`
- Type: **GET**
- URL Parameters:
  - `limit` (**Interger**)
  - `page` (**Interger**)
- Body Example: **N/A**

### Show Task

- Route: `/task/<TASK_ID>`
- Type: **GET**
- URL Parameters: **N/A**
- Body Example: **N/A**

### Add Task

- Route: `/add-task`
- Type: **POST**
- URL Parameters: **N/A**
- Body Example:
    ```
    {
        title: 'Some title'
    }
    ```

### Update Task

- Route: `/update-task`
- Type: **PATCH**
- URL Parameters: **N/A**
- Body Example:
    ```
    {
        id: 1
        title: 'Some new title'
    }
    ```

### Remove Task

- Route: `/remove-task`
- Type: **DELETE**
- URL Parameters: **N/A**
- Body Example:
    ```
    {
        id: 1
    }
    ```

### List Todos

- Route: `/list-todo`
- Type: **GET**
- URL Parameters:
  - `limit` (**Interger**)
  - `page` (**Interger**)
- Body Example: **N/A**

### Show Todo

- Route: `/todo/<TODO_ID>`
- Type: **GET**
- URL Parameters: **N/A**
- Body Example: **N/A**

### Add Todo

- Route: `/add-todo`
- Type: **POST**
- URL Parameters: **N/A**
- Body Example:
    ```
    {
        task_id: 1
        title: 'Some title'
    }
    ```

### Update Todo

- Route: `/update-todo`
- Type: **PATCH**
- URL Parameters: **N/A**
- Body Example:
    ```
    {
        id: 1
        title: 'Some new title'
    }
    ```

### Mark Todo

- Route: `/mark-todo`
- Type: **PATCH**
- URL Parameters: **N/A**
- Body Example:
    ```
    {
        id: 1
        done: 1
    }
    ```
    ```
    {
        id: 1
        done: 0
    }
    ```

### Remove Todo

- Route: `/remove-todo`
- Type: **DELETE**
- URL Parameters: **N/A**
- Body Example:
    ```
    {
        id: 1
    }
    ```