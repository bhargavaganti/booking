ANONYMOUS_USER_ID=-1
AUTH_PROFILE_MODULE = 'appomatic_booking.Profile'
AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)
