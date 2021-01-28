# Forrzar UTF-8 en todos los cmdlets con -Encoding
$PSDefaultParameterValues['*:Encoding'] = 'utf-8'

# Global Variables
# Smart cd
$GLOBAL:previousDir = ''
$GLOBAL:pwd = ''
# Help Variables
$GLOBAL:pshrc = 'C:\Users\Lucas\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1'
$GLOBAL:psh_history = 'C:\Users\Lucas\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt'

# Hacer accessible el historial de las sesiones anteriores.
Copy-Item $psh_history C:\Users\Lucas\ps_history.txt



# Bash-like aliases
set-alias -Name cat -Value get-content -Option AllScope
set-alias -Name clear -Value clear-host -Option AllScope
set-alias -Name cp -Value copy-item -Option AllScope
set-alias -Name ls -Value get-childitem -Option AllScope
set-alias -Name mv -Value move-item -Option AllScope
set-alias -Name pwd -Value get-location -Option AllScope
set-alias -Name rm -Value remove-item -Option AllScope
set-alias -Name rmdir -Value remove-item -Option AllScope
set-alias -Name echo -Value write-output -Option AllScope

# Smart cd
set-alias -Name cd -Value push-location -Option AllScope -PassThru -Force 1> $null
set-alias -Name popd -Value pop-location -Option AllScope
set-alias -Name pushd -Value push-location -Option AllScope

# Aliases para programas
set-alias -Name subl -Value 'C:\Program Files\Sublime Text 3\sublime_text.exe' -Option AllScope



# CMD-like aliases y otros
# set-alias -Name cls -Value clear-host -Option AllScope
# set-alias -Name chdir -Value set-location -Option AllScope
# set-alias -Name copy -Value copy-item -Option AllScope
# set-alias -Name del -Value remove-item -Option AllScope
# set-alias -Name dir -Value get-childitem -Option AllScope
# set-alias -Name erase -Value remove-item -Option AllScope
# set-alias -Name move -Value move-item -Option AllScope
# set-alias -Name rd -Value remove-item -Option AllScope
# set-alias -Name ren -Value rename-item -Option AllScope
# set-alias -Name set -Value set-variable -Option AllScope
# set-alias -Name type -Value get-content -Option AllScope
# set-alias -Name h -Value get-history -Option AllScope
# set-alias -Name history -Value get-history -Option AllScope
# set-alias -Name kill -Value stop-process -Option AllScope
# set-alias -Name lp -Value out-printer -Option AllScope
# set-alias -Name mount -Value new-mshdrive -Option AllScope
# set-alias -Name ps -Value get-process -Option AllScope
# set-alias -Name r -Value invoke-history -Option AllScope

# Help functions
function help
{
    get-help $args[0] | out-host -paging
}

function man
{
    get-help $args[0] | out-host -paging
}

function mkdir
{
    new-item -type directory -path $args
}

# Smart cd
function prompt
{
    # Add ~ as Home
    $escapedHome = [regex]::escape("$HOME")
    $shortDir = $(get-location | %{$_ -replace "$escapedHome" , '~'})
    # Dinamically resizing path size
    if ( $shortDir.length -gt 40 ){
        $originalLength = $shortDir.length
        $i = 1
        $dirArray = $shortDir -Split '\\'
        $shortDir = $dirArray[($dirArray.length - $i)]
        while ( $shortDir.length -lt 40 ){
            $i++
            $shortDir = $dirArray[($dirArray.length - $i)] , $shortDir -join '\'
        }
        if ( $shortDir.length -ne $originalLength ){
            $shortDir = '…' , $shortDir -join '\'
        }
    }
    # Prompt line
    Write-Host "PS $shortDir>" -NoNewLine -foregroundcolor Green
    # cd functionality
    $GLOBAL:nowPath = (get-location).Path
    if ($nowPath -ne $GLOBAL:pwd) {
        $GLOBAL:previousDir = $GLOBAL:pwd
        $GLOBAL:pwd = $nowPath
    }
    return ' '
}

function BackOneDir{
    set-location $GLOBAL:previousDir
}
set-alias -Name 'cd-' -Value BackOneDir -Option AllScope

function touch
{
    if($args[0] -eq $null)
    {
        throw "No filename supplied"
    }
    foreach ($item in $args)
    {
        $file = $item

        if (Test-Path $file)
        {
            (get-childitem $file).LastWriteTime = Get-Date
        }
        else
        {
            write-output $null > $file
        }
    }
}