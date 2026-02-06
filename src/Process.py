class Process:
    """Represents a physics process definition loaded from JSON."""

    def __init__(self, name, incoming, outgoing, model, notes=""):
        self.name = name
        self.incoming = incoming
        self.outgoing = outgoing
        self.model = model
        self.notes = notes

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or not value:
            raise ValueError("name must be a non-empty string")
        self._name = value

    @property
    def incoming(self):
        return self._incoming

    @incoming.setter
    def incoming(self, value):
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError("incoming must be a list of strings")
        self._incoming = value

    @property
    def outgoing(self):
        return self._outgoing

    @outgoing.setter
    def outgoing(self, value):
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError("outgoing must be a list of strings")
        self._outgoing = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        if not isinstance(value, str) or not value:
            raise ValueError("model must be a non-empty string")
        self._model = value

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        if not isinstance(value, str):
            raise ValueError("notes must be a string")
        self._notes = value

    def __repr__(self):
        return f"Process(name={self.name!r}, model={self.model!r})"

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            incoming=data["incoming"],
            outgoing=data["outgoing"],
            model=data["model"],
            notes=data.get("notes", "")
        )
