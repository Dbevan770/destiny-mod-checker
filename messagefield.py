class MessageField:
    def __init__(self, _name, _value):
        self.name = _name
        self.value = _value

class ArmorMessageField:
    def __init__(self, _title, _value, _mobility, _resilience, _recovery, _discipline, _intellect, _strength):
        self.title = _title
        self.value = _value
        self.mobility = _mobility
        self.resilience = _resilience
        self.recovery = _recovery
        self.discipline = _discipline
        self.intellect = _intellect
        self.strength = _strength