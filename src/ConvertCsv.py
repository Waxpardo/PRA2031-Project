import csv
from pathlib import Path

"""
This script converts standardized CSV data from PYTHIA into a custom 
text-based format used for internal simulation analysis.
"""


def ConvertCsvToTxt(csvFile, txtFile):
    # Determine the project directory structure to locate input/output folders
    projectRoot = Path(__file__).resolve().parent.parent
    csvPath = projectRoot / "outputs" / csvFile
    txtPath = projectRoot / "outputs" / txtFile

    if not csvPath.exists():
        print(f"Error: {csvPath} not found.")
        return

    # A 'Dictionary' to group particles by their specific event ID.
    # In a collider, one 'Event' is a single collision producing multiple particles.
    eventsMap = {}

    with open(csvPath, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            eventId = int(row['event'])
            # If this is a new collision we haven't seen, create a new list for it
            if eventId not in eventsMap:
                eventsMap[eventId] = []
            eventsMap[eventId].append(row)

    # Begin writing the formatted text file
    with open(txtPath, mode='w') as file:
        # Sort events numerically to ensure progression is consistent
        for eventId in sorted(eventsMap.keys()):
            # Header line that the SimulatorComparison class uses to split data
            file.write(f"Event {eventId}\n")

            for part in eventsMap[eventId]:
                # eventIdStr: Formats the ID as 3 digits (e.g., 001 instead of 1)
                eventIdStr = f"{eventId:03d}"
                pdgId = int(part['id'])
                particleName = part['name']

                # Logic to label the "Lifecycle" of the particle:
                # 'Initial Beam' particles are the ones colliding.
                # 'Collision' (or Final State) particles are what fly out into the detectors.
                nameColumn = particleName
                if part['isFinal'] == '0' and part['mother1'] == '0':
                    nameColumn = "Initial Beam"
                elif part['isFinal'] == '1':
                    nameColumn = "Collision"

                # Extract the Four-Momentum: A mathematical vector (E, px, py, pz)
                # that fully describes the particle's energy and direction.
                energyVal = float(part['E'])
                pxVal = float(part['px'])
                pyVal = float(part['py'])
                pzVal = float(part['pz'])

                # Write the line with specific padding (e.g., :8.3f) so columns align vertically.
                # This makes the TXT file human-readable and easy for the 're' (regex) tool to parse.
                file.write(f"    {eventIdStr} | {pdgId:>3} | {nameColumn:<12} | "
                           f"(E: {energyVal:8.3f}, px: {pxVal:8.3f}, py: {pyVal:8.3f}, pz: {pzVal:8.3f})\n")

            # Add a newline between events for visual clarity
            file.write("\n")

    print(f"Successfully converted {csvPath} to {txtPath}")


# Standard Python entry point to run the conversion
if __name__ == "__main__":
    ConvertCsvToTxt("mumu_EW.csv", "mumu_EW.txt")