class Person:
    def __init__(self, iz):
        self.isZombie = iz
        self.wasVaccinated = False
        self.turnsVaccinated = 0
        self.isVaccinated = False
        self.halfCured = False
        self.wasCured = False
        self.stunned = False

    def clone(self):
        ret = Person(self.isZombie)
        ret.wasVaccinated = self.wasVaccinated
        ret.turnsVaccinated = self.turnsVaccinated
        ret.isVaccinated = self.isVaccinated
        ret.halfCured = self.halfCured
        ret.wasCured = self.wasCured
        ret.stunned = self.stunned
        return ret

    # Checks whether a piece is in the hospital
    def isInHospital(self, coords):
        if coords[0] < 3 and coords[1] < 3:
            return True
        else:
            return False

    def __str__(self) -> str:
        return f"Person who is a zombie? {self.isZombie}"

    def __repr__(self) -> str:
        return str(self)
