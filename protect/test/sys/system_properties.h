// Host stand-in for bionic's property API (tests only).
#define PROP_VALUE_MAX 92
int __system_property_get(const char *name, char *value);
int __system_property_set(const char *name, const char *value);
