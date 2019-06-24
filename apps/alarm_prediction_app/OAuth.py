


user = # A User object usually obtained from request.
storage = Storage(CredentialsModel, 'id', user, 'credential')
credential = storage.get()
...
storage.put(credential)

# https://developers.google.com/api-client-library/python/guide/django