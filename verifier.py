import subprocess
import os

def test_lambda_execution(code_dir: str, target_version: str = "python3.12") -> tuple[bool, str]:
    version_tag = target_version.replace("python", "")
    image_name = f"public.ecr.aws/lambda/python:{version_tag}"
    
    test_script = (
        "import lambda_function; "
        "res = lambda_function.lambda_handler({}, None); "
        "print('EXECUTION_OK:', res)"
    )
    
    docker_cmd = [
        "docker", "run", "--rm",
        "--entrypoint", "python",
        "-v", f"{os.path.abspath(code_dir)}:/var/task",
        image_name,
        "-c", test_script
    ]
    
    try:
        run_res = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=60)
        if run_res.returncode == 0 and "EXECUTION_OK" in run_res.stdout:
            return True, run_res.stdout
        return False, run_res.stderr or run_res.stdout
    except Exception as e:
        return False, str(e)