
# mapping from provider_code to accept_invoice() function
# key - provider code
# value - tuple of (provider name, viewname)
# where viewname will be used by reverse() with addition of Invoice code as parameter
PAYMENTS_PROVIDERS = {
}

# list of application-plugins for providing payments.
# this list populated by apps.register_payment() call
payments_apps = []