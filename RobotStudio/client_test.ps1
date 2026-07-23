# Connects to the ex_p224.mod socket server (192.168.3.3:5000)
# 11 -> move to p10, 22 -> move to p20, 33 -> move to p30, qq -> end communication and exit

$ip = "192.168.3.3"
$port = 5000

function Read-Response($stream) {
    $buffer = New-Object byte[] 1024
    $bytesRead = $stream.Read($buffer, 0, $buffer.Length)
    return [System.Text.Encoding]::ASCII.GetString($buffer, 0, $bytesRead)
}

Write-Host "Connecting to robot server ${ip}:${port} ..."
$client = New-Object System.Net.Sockets.TcpClient
$client.Connect($ip, $port)
$stream = $client.GetStream()
Write-Host "Connected. Enter 11 / 22 / 33 / qq."

while ($true) {
    $cmd = Read-Host "Enter command (11/22/33/qq)"

    if ($cmd -notin @("11", "22", "33", "qq")) {
        Write-Host "Please enter only 11, 22, 33, or qq."
        continue
    }

    $bytes = [System.Text.Encoding]::ASCII.GetBytes($cmd)
    $stream.Write($bytes, 0, $bytes.Length)

    $response = Read-Response $stream
    Write-Host "Server response: $response"

    if ($cmd -eq "qq") {
        break
    }
}

$stream.Close()
$client.Close()
Write-Host "Connection closed."
