To run the flask server, we need to set the proper environment variables. 
For Linux, use: 
```
    $ export FLASK_ENV=development
    $ export FLASK_APP=app.py
```

On Windows, use either:
```
> set FLASK_ENV=development
> set FLASK_APP=app.py
```

or if the above doesn't work, use
```
> $env:FLASK_ENV = "development"
> $env:FLASK_APP = "app.py"
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
