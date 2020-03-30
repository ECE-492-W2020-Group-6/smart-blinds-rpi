# Running Flask Server Natively
To run the flask server, we need to set the proper environment variables. 
For Linux, use: 
```
    $ export FLASK_ENV=development
    $ export FLASK_APP=app.py
    $ export USE_TEMP_SENSOR=false
    $ export USE_MOTOR=false
```
To set non-default values for authentication parameters, use:
```
    $ export SECRET_KEY=<a secret key>
    $ export TOKEN_DURATION_MINUTES=<integer number of minutes>
```

For TESTING purposes, the JWT auth can be bypassed by running the server with
```
    $ export USE_JWT=false
```
Otherwise, the default is to use JWT authentication.

On Windows(cmd), use either:
```
> set FLASK_ENV=development
> set FLASK_APP=app.py
> set USE_TEMP_SENSOR=false
> set USE_MOTOR=false
```

or if the above doesn't work, use (in powershell)
```
> $env:FLASK_ENV = "development"
> $env:FLASK_APP = "app.py"
> $env:USE_TEMP_SENSOR=$false
> $env:USE_MOTOR=$false
```

Then, the app can be run with 
```
flask run 
```
to create a local server on 127.0.0.1:5000 (default) 

For an externally visible server, use the command 
```
flask run --host="<ip>"
```
to set the ip. It can be set to the default route 0.0.0.0 to listen on all of your own IPs or just a specific one for an interface. 
The port can also be set with `--port`

# Running Flask Server using Docker

From the root of the repo, run:

`./run-server.sh`

This automatically runs a container in daemon code that runs the flask server, with the flask server in development mode.
A server is now running on 127.0.0.1:5000.
To set specific env variables, run the container manually and add the env vars to the docker run command.
Alternatively, a docker compose file can be used.

To see logs in stdout, run:

`docker logs --follow rpi-code`

To run an interactive session in the container:

`./run-interactive.sh`
