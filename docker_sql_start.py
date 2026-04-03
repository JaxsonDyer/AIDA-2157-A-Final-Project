import docker
from docker.errors import NotFound, APIError

def verify_docker_sql():
    """
    Starts the specific MS-SQL server in docker if it doesn't exist,
    or resumes it if it is stopped.
    """
    # --- Configuration ---
    container_name = "aida2157a-SQL-pgnaawmszydfuzabwixtlmbnainwxztt"
    # Note: Default MS-SQL username is always 'sa'
    db_password = r'eKyhH>"UGj]W=bqT|t,VMF?<Qj"%ow£YS[;=!|i]GTjR_GqIpG'
    image_name = "mcr.microsoft.com/mssql/server:2022-latest"
    host_port = 1433

    try:
        client = docker.from_env()
    except Exception as e:
        print(f"Error: Could not connect to Docker. Ensure Docker is running.\n{e}")
        return False

    try:
        # Check if container exists
        container = client.containers.get(container_name)
        
        if container.status == "running":
            print(f"Success: Container '{container_name}' is already running.")
        else:
            print(f"Container found with status '{container.status}'. Starting now...")
            container.start()
            print("Success: Container started.")
        return True

    except NotFound:
        # Create new container
        print(f"Container '{container_name}' not found. Initializing setup...")
        try:
            client.containers.run(
                image=image_name,
                name=container_name,
                environment={
                    "ACCEPT_EULA": "Y",
                    "MSSQL_SA_PASSWORD": db_password
                },
                ports={'1433/tcp': host_port},
                detach=True
            )
            print(f"Success: Container created and started on port {host_port}.")
            return True
        except APIError as e:
            print(f"Failed to create container: {e}")
            return False

# This allows you to still run the file directly to test it
if __name__ == "__main__":
    verify_docker_sql()