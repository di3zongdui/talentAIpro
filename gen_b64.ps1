$code='window.scrollTo(0,0)'
$bytes=[System.Text.Encoding]::UTF8.GetBytes($code)
$b64=[System.Convert]::ToBase64String($bytes)
Write-Output $b64
