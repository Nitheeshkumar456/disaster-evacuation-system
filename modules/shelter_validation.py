"""Shelter capacity and availability validation."""


def eligible_shelters(shelters, population):
    population = int(population)
    return [
        shelter for shelter in shelters
        if bool(shelter.get("available", True))
        and int(shelter.get("capacity", 0)) >= population
    ]
