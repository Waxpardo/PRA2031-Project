class Process:
    """
    A blueprint for any particle interaction.
    It defines who enters the collision and who leaves it.
    """

    def __init__(self, name, incoming, outgoing, model, notes=""):
        # We use setters to ensure the data passed in is valid from the start.
        self.Name = name
        self.Incoming = incoming
        self.Outgoing = outgoing
        self.Model = model
        self.Notes = notes

    @property
    def Name(self):
        return self.internalName

    @Name.setter
    def Name(self, value):
        # Ensures the process has a readable name like 'Muon Annihilation'
        if not isinstance(value, str) or not value:
            raise ValueError("name must be a non-empty string")
        self.internalName = value

    @property
    def Incoming(self):
        return self.internalIncoming

    @Incoming.setter
    def Incoming(self, value):
        # These are the 'Initial State' particles (the ones that collide).
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError("incoming must be a list of strings")
        self.internalIncoming = value

    @property
    def Outgoing(self):
        return self.internalOutgoing

    @Outgoing.setter
    def Outgoing(self, value):
        # These are the 'Final State' particles (the result of the collision).
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError("outgoing must be a list of strings")
        self.internalOutgoing = value

    @property
    def Model(self):
        return self.internalModel

    @Model.setter
    def Model(self, value):
        # Specifies the physics framework, such as 'Standard Model' or 'QED'.
        if not isinstance(value, str) or not value:
            raise ValueError("model must be a non-empty string")
        self.internalModel = value

    @property
    def Notes(self):
        return self.internalNotes

    @Notes.setter
    def Notes(self, value):
        # Extra context for the researcher (e.g., 'Validated against 2024 data').
        if not isinstance(value, str):
            raise ValueError("notes must be a string")
        self.internalNotes = value

    def __repr__(self):
        """Returns a technical string representation of the object."""
        return f"Process(name={self.Name!r}, model={self.Model!r})"

    @classmethod
    def FromDict(cls, data):
        """
        A 'Factory Method' that creates a Process object directly from
        a dictionary (useful when reading from JSON files).
        """
        return cls(
            name=data["name"],
            incoming=data["incoming"],
            outgoing=data["outgoing"],
            model=data["model"],
            notes=data.get("notes", "")
        )