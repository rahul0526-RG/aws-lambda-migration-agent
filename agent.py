import os
import re
import shutil
from gemini_engine import migrate_lambda_code
from verifier import test_lambda_execution

TARGET_RUNTIME = "python3.12"
TARGET_REPO_PATH = "./mock_repo"

def update_iac_templates(repo_path: str, target_runtime: str):
    sam_file = os.path.join(repo_path, "template.yaml")
    if os.path.exists(sam_file):
        with open(sam_file, "r") as f:
            content = f.read()
        updated = re.sub(r'Runtime:\s*python3\.[789]', f'Runtime: {target_runtime}', content)
        with open(sam_file, "w") as f:
            f.write(updated)
        print(f"[+] Updated SAM template.yaml runtime to {target_runtime}")

def align_custom_layer_structure(repo_path: str, target_runtime: str):
    layers_base = os.path.join(repo_path, "layers", "python", "lib")
    if not os.path.exists(layers_base):
        return

    target_dir = os.path.join(layers_base, target_runtime)

    for folder in os.listdir(layers_base):
        if folder.startswith("python3.") and folder != target_runtime:
            old_dir = os.path.join(layers_base, folder)
            # If the target directory already exists, remove it first
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.move(old_dir, target_dir)
            print(f"[+] Aligned layer directory: {folder} -> {target_runtime}")

def run_migration():
    print("=" * 60)
    print(f"Starting AWS Lambda Migration Agent (Target: {TARGET_RUNTIME})")
    print("=" * 60)

    # 1. Update IaC
    update_iac_templates(TARGET_REPO_PATH, TARGET_RUNTIME)

    # 2. Fix layer paths safely
    align_custom_layer_structure(TARGET_REPO_PATH, TARGET_RUNTIME)

    # 3. Read old code & requirements
    code_path = os.path.join(TARGET_REPO_PATH, "lambda_function.py")
    req_path = os.path.join(TARGET_REPO_PATH, "requirements.txt")

    with open(code_path, "r", encoding="utf-8") as f:
        source_code = f.read()
    with open(req_path, "r", encoding="utf-8") as f:
        requirements = f.read()

    # 4. Refactor with Gemini
    print("[+] Sending code to Gemini for refactoring...")
    result = migrate_lambda_code(source_code, requirements, TARGET_RUNTIME)

    # 5. Save the updated files
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(result["refactored_code"])
    with open(req_path, "w", encoding="utf-8") as f:
        f.write(result["updated_requirements"])
    print("[+] Saved refactored code and upgraded requirements.txt")

    # 6. Verify with Docker
    print("[+] Running verification inside official AWS Lambda container...")
    success, output = test_lambda_execution(TARGET_REPO_PATH, TARGET_RUNTIME)

    if success:
        print("\n[SUCCESS] Lambda handler passed verification inside Python 3.12 container!")
        print("\nSummary of changes applied by Gemini:")
        for change in result["summary_of_changes"]:
            print(f" - {change}")
    else:
        print(f"\n[FAIL] Container execution test failed:\n{output}")

if __name__ == "__main__":
    run_migration()