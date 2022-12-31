class MessageField:
    def __init__(self, _name, _value):
        self.name = _name
        self.value = _value

class ArmorMessageField:
    def __init__(self, _name, _value, _mobility, _resilience, _recovery, _discipline, _intellect, _strength):
        self.name = _name
        self.value = _value
        self.mobility = _mobility
        self.resilience = _resilience
        self.recovery = _recovery
        self.discipline = _discipline
        self.intellect = _intellect
        self.strength = _strength

    def generateValueMessage(self):
        self.value = f"Mobility: {self.mobility}᲼᲼᲼᲼᲼᲼᲼᲼Resilience: {self.resilience}᲼᲼᲼᲼᲼᲼᲼᲼Recovery: {self.recovery}\nDiscipline: {self.discipline}᲼᲼᲼᲼᲼᲼᲼᲼Intellect: {self.intellect}᲼᲼᲼᲼᲼᲼᲼᲼Strength: {self.strength}"