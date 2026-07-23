# ===================================================================
# robot_connector.ps1 - connects to the ABB robot socket server (ex_p224.mod)
#
# Naming rules:
#   Function : Snake_Case, first letter capitalized (e.g. Read_Ip)
#   Variable : snake_case, first letter lowercase (e.g. robot_ip)
#   Class    : ALL_CAPS_SNAKE_CASE (e.g. ROBOT_CONNECTOR) - not used yet,
#              kept as a convention note in case this gets wrapped in a class later.
# ===================================================================

# Commands actually handled by ex_p224.mod (update here to refresh the banner too)
$valid_commands = @("11", "22", "33", "qq")

# Prompts for the robot IP address
function Read_Ip {
    return Read-Host "Enter robot IP"
}

# Prompts for the robot port number
function Read_Port {
    return Read-Host "Enter robot port"
}

# Tries to connect to the given IP/port. Returns a TcpClient on success, $null on failure
function Test_Connect($robot_ip, $robot_port) {
    try {
        $tcp_client = New-Object System.Net.Sockets.TcpClient
        $tcp_client.Connect($robot_ip, [int]$robot_port)
        return $tcp_client
    } catch {
        Write-Host "Connection failed: $($_.Exception.Message)"
        return $null
    }
}

# Prints the welcome banner and the list of valid commands
function Show_Banner {
    $command_list = $valid_commands -join ", "
    Write-Host ""
    Write-Host "This is abb robot connecter."
    Write-Host "Enter Command (Ex. $command_list)"
    Write-Host ""
}

# Prompts "Enter :" and returns the typed command
function Read_Command {
    return Read-Host "Enter"
}

# Sends a command string over the socket
function Send_Command($net_stream, $user_command) {
    $command_bytes = [System.Text.Encoding]::ASCII.GetBytes($user_command)
    $net_stream.Write($command_bytes, 0, $command_bytes.Length)
}

# Reads a response from the socket (kept separate from Send_Command so it can be
# called on its own once two-way communication is added)
function Get_Response($net_stream) {
    $read_buffer = New-Object byte[] 1024
    $bytes_read = $net_stream.Read($read_buffer, 0, $read_buffer.Length)
    return [System.Text.Encoding]::ASCII.GetString($read_buffer, 0, $bytes_read)
}

# Closes the stream and socket
function Close_Connect($tcp_client, $net_stream) {
    $net_stream.Close()
    $tcp_client.Close()
}

# Entry point: wires the functions above together
function Main {
    $tcp_client = $null
    while ($null -eq $tcp_client) {
        $robot_ip = Read_Ip
        $robot_port = Read_Port
        $tcp_client = Test_Connect $robot_ip $robot_port
    }

    $net_stream = $tcp_client.GetStream()
    Show_Banner

    while ($true) {
        $user_command = Read_Command
        Send_Command $net_stream $user_command
        $robot_reply = Get_Response $net_stream
        Write-Host "Robot reply: $robot_reply"

        if ($user_command -eq "qq") {
            break
        }
    }

    Close_Connect $tcp_client $net_stream
    Write-Host "Connection closed."
}

Main
