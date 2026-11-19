#!/usr/bin/env python3

import json
import subprocess
import os
import tempfile
import argparse


def main():
    parser = argparse.ArgumentParser(description="Yul2CHC dual mode")
    parser.add_argument("-json", "--input-json", help="Path to JSON input file")
    args = parser.parse_args()

    # Path assoluti degli script di supporto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generate_facts_path = os.path.join(script_dir, "generate_facts.py")
    replace_path = os.path.join(script_dir, "replace_character.py")

    # ==============================
    # PIPELINE MODE
    # ==============================
    if args.input_json:
        input_json = os.path.abspath(args.input_json)
        output = os.path.dirname(input_json)

        base_name = os.path.splitext(os.path.basename(input_json))[0]
        c_name = base_name

    # ==============================
    # INTERACTIVE MODE
    # ==============================
    else:
        input_json = input("Enter the full path to the JSON input file: ").strip()
        output = input("Enter the full path for the final output file: ").strip()
        c_name = input("contract name: ").strip()

        input_json = os.path.abspath(input_json)
        output = os.path.abspath(output)

    # ==============================
    # COMMON PART
    # ==============================
    base, _ = os.path.splitext(c_name)
    final_output = os.path.join(output, base + ".txt")

    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(final_output, "w", encoding="utf-8") as fout:
        fout.write("")

    # For each contract in JSON
    for contract_name, contract_data in data.items():
        print(f"Processing contract: {contract_name}")

        # Temporary JSON file containing only this contract
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json", encoding="utf-8") as temp_file:
            temp_json_path = temp_file.name
            json.dump({contract_name: contract_data}, temp_file, indent=4)

        # Temporary output file for generate_facts.py
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".pl", encoding="utf-8") as temp_output_file:
            temp_output_path = temp_output_file.name

        cmd = ["python3", generate_facts_path, temp_json_path, temp_output_path, contract_name]
        subprocess.run(cmd, check=True)

        # Read generated output
        with open(temp_output_path, "r", encoding="utf-8") as fout:
            contract_output = fout.read()

        # Append to final output
        with open(final_output, "a", encoding="utf-8") as fout:
            fout.write(f"% {contract_name} contract\n")
            fout.write(contract_output)
            fout.write("\n\n")

        # Delete temp files
        os.remove(temp_json_path)
        os.remove(temp_output_path)

    print(f"Final output written to: {final_output}")

    # Final normalization step
    cmd = ["python3", replace_path, final_output]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()