class ConfigBase(object):
    def get(self, prop):
        try:
            return getattr(self, prop)
        except Exception as e:
            e.message = 'Unable to access that property. ' + e.message

    def set(self, prop, value):
        try:
            return setattr(self, prop, value)
        except Exception as e:
            e.message = 'Unable to set that property/value. ' + e.message


