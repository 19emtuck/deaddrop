# Global overview

deaddrop is a simple http service that catch requests on a specific url (token based)
and returns the list of calls with timestamp and content json or form content

## licence

deaddrop is free software; you can redistribute it and/or modify it under
the terms of the M.I.T License.

## docker exec



``sudo docker build -t deaddrop:last .``


``sudo docker run -d -p 4014:80 --name deaddrop deaddrop:last``
