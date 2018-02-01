# plusone-server
Server written in python ([flask](http://flask.pocoo.org/) and [socket.io](https://socket.io/)) to manage requests from the plusone app.

## Features
- Chat implemented in sockets-io
- ORM saves information(Events and Users) in any database (in this case it's a heroku postgres)
- API which uses Auth tokens
