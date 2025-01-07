class Cuadro:
    def __init__(self, lado=None, area=None, centrox=None):
        self.lado = lado
        self.area = area
        self.centrox = centrox

    def asignar_lado(self, lado):
        self.lado = lado

    def asignar_area(self, area):
        self.area = area

    def asignar_centrox(self, centrox):
        self.centrox = centrox

    def mostrar_cuadro(self):
        return f"Características del cuadro: lado={self.lado}, área={self.area}, centrox={self.centrox}"

    def mostrar_area(self):
        return self.area
