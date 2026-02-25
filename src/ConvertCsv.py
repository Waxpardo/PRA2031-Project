import csv
from pathlib import Path

def convert_csv_to_txt(csv_file, txt_file):
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "outputs" / csv_file
    txt_path = project_root / "outputs" / txt_file

    if not csv_path.exists():
        print(f"Error: {csv_path} not found.")
        return

    with open(csv_path, mode='r') as f:
        reader = csv.DictReader(f)
        events = {}
        for row in reader:
            ev_id = int(row['event'])
            if ev_id not in events:
                events[ev_id] = []
            events[ev_id].append(row)

    with open(txt_path, mode='w') as f:
        for ev_id in sorted(events.keys()):
            f.write(f"Event {ev_id}\n")
            for part in events[ev_id]:
                # Format: {event_id} | {particle_id} | {name} | (E: {E}, px: {px}, py: {py}, pz: {pz})
                # Event ID is 3 digits padded with zeros
                # Particle ID is 3 characters wide, right-aligned
                # Particle Name is 12 characters wide
                # Four-momentum components formatted with %8.3f
                
                event_id_str = f"{ev_id:03d}"
                pdg_id = int(part['id'])
                name = part['name']
                
                # In OurOutput.txt, "mother" info is used as Name for visualization consistency 
                # but based on previous solution summary, it was mapping name.
                # Let's look at OurOutput.txt again: 
                # 000 |  13 | Initial Beam | (E:   45.590, px:    0.000, py:    0.000, pz:   45.590)
                # In mumu_EW.csv, the particles have names like "mu-", "mu+", "W-", etc.
                # However, the previous conversion used fixed columns.
                
                # Check status/mother to determine if it's Initial Beam or Collision?
                # Actually, the previous solution summary said:
                # {event_id} | {particle_id} | {name} | (E: {E}, px: {px}, py: {py}, pz: {pz})
                
                name_col = name
                if part['isFinal'] == '0' and part['mother1'] == '0':
                    name_col = "Initial Beam"
                elif part['isFinal'] == '1':
                    name_col = "Collision"

                e = float(part['E'])
                px = float(part['px'])
                py = float(part['py'])
                pz = float(part['pz'])

                f.write(f"    {event_id_str} | {pdg_id:>3} | {name_col:<12} | (E: {e:8.3f}, px: {px:8.3f}, py: {py:8.3f}, pz: {pz:8.3f})\n")
            f.write("\n")

    print(f"Successfully converted {csv_path} to {txt_path}")

if __name__ == "__main__":
    convert_csv_to_txt("mumu_EW.csv", "mumu_EW.txt")
